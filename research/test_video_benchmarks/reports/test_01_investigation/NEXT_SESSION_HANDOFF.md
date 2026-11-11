# Next-session handoff prompt: remaining rally-boundary failures

Copy/use this complete document as the instruction for the next session. The companion `research/next_session_failure_inventory.json` contains all 28 structured issues, both full metrics, all 36 row comparisons and four unmatched predictions. No new labels or predictions were created for this handoff.

## Mission and operating rules

You are the senior computer-vision/ML evaluation engineer continuing the Badminton Analytics investigation. Fix remaining failures component by component through evidence-backed experiments. Preserve other analytics. Continue until issues are verified fixed or explicitly documented with the exact missing evidence/access and next experiment. Do not claim unknowns are fixed or promise perfect boundaries unsupported by footage.

Use a central orchestrator and specialized auditors where parallel work helps. Assign exclusive production-file ownership; coordinate shared interfaces, engine, FSM, schemas and configuration centrally. Do not let agents modify the same production files concurrently.

This is continued work, not a new threshold exercise. Read current code as well as reports. Specialist audits mostly describe the original baseline; later commits already fix some defects. Do not rediscover fixed issues as open failures or rewrite the whole pipeline.

Repository: `/home/administrator/Desktop/sport-analytics/Sports_Analytics`. Work exclusively on `Benchmarking`. Results checkpoint is `e8877b2`; this handoff adds documentation afterward. Reinspect actual HEAD/status. `main` must stay `301baf08be5e989dd0ed93cb885733c3cf6f356a`. Frozen baseline evidence commit: `b773e20c62d1c398cddc3d23510bd4adf823325b`. Best fresh inference used source `3653b0deee367297037de449d882e9945e6d9c28`, not the later report/handoff revision.

Read `AGENTS.md`, `CODEX.md`, `CLAUDE.md`; preserve their architecture/provenance/runtime rules. Their old instruction to work on main is superseded by the user's explicit Benchmarking-only direction. Preserve all newly found uncommitted/untracked work. Never reset/discard/overwrite it.

Startup:

```bash
cd /home/administrator/Desktop/sport-analytics/Sports_Analytics
git status --short --branch
git branch --show-current
git log -10 --oneline
git rev-parse main
source ../gpu-env.sh
```

Use existing server `.venv`/Pascal CUDA/FFmpeg environment. Recorded hardware was two GTX 1080 Ti GPUs, driver 580.178.04; verify current availability, do not assume an idle GPU. Do not replace environment, stop unrelated jobs, enable Cloudflare, restart/deploy the app or install large models for evaluator tests. Never store credentials in metadata/logs/code.

## Immutable dataset and comparison protocol

Original `data/benchmarking/test1/Test1_Full_rev.mp4`: 1920 × 1080, 30 FPS, 17,268 decoded frames, 575.6 seconds. The normal production proxy is 1280 × 720 CFR, with the same indices and zero-origin 30 FPS timeline. All 288 chunks cover indices 0..17267; effective HLS chunks are 60 frames (287 × 60 plus a 48-frame tail), despite configured chunk size 64.

GT:`Part2/dataset/Test1_Full/Test1_Full_rally.csv`, exactly 36 intervals. Related Part 2 outputs are diagnostic context only, never production input/calibration/predictions. Preserve original video/CSV, all files under `outputs/benchmarking/test1/`, and completed experiment outputs. Treat fresh v1 and its semantic check as historical references too.

`research/evidence_registry.json` pins 1,766 baseline files, original media/CSV and active weights. Its production hashes describe old production `301baf08`, not a request to undo later changes.

Exact primary CSV:

```csv
Start_Frame,End_Frame,Start_Time_sec,End_Time_sec,Duration_sec,Start_Time,End_Time
```

Use integer canonical frames, seconds=frame/actual FPS, duration=end−start, and MM:SS truncated to whole seconds. Keep `[start,end)` timestamp spans, without inclusive +1 or rounded inclusive event-payload duration. Human annotation-tool history is unavailable; possible ±1 physical-frame ambiguity does not justify fitted offsets.

Frozen `scripts/benchmarking/evaluate_rallies.py` policy: maximum-cardinality one-to-one matching, eligible IoU>=.5, then total IoU+1e−9/(1+boundary-distance-seconds), documented deterministic tie behavior. Signed error=prediction−GT. Report IoU strict-threshold `>` percentages and tolerance-inclusive equality; both matched-only/all GT denominators. Misses=null, never zero. Baseline GT29's 157/315 IoU<.5 was a valid miss; inclusive counting would manufacture a match.

No GT input to inference, forced count 36, manual boundary/contact edits, GT-conditioned unions, rowID exceptions, hidden backdating, removing difficult labels, FPS/offset fitting or altered matching. Test 1 is exposed development footage. Further tuning stays exploratory until match-disjoint reviewed validation exists.

## Required reading: reports, exact evidence and current source

Read in order:

1. `research/final_benchmark_report.md`: full actual fresh result, all experiment metrics/runtime/limits.
2. `research/regression_report.md`: errors for all 36 rows, common/new matches, genuine regressions, all 27 completed experiment runs and rejected/invalid candidates.
3. `research/remaining_failure_review.md`: original-frame GT22/23 edit, GT31 close-up/mixed visibility loss and GT27 static T reference.
4. `research/root_cause_analysis.md`: R1–R11, proofs/hypotheses/alternatives/source owners.
5. `research/component_test_report.md`: exact commands/test scopes,1895 passes/no skips, real inference versus replay/controlled tests.
6. `research/improvement_strategy.md`, `experiment_matrix.md`, `implementation_roadmap.md`, `experiment_results.json`, `evidence_registry.json`.
7. `scripts/benchmarking/README.md`, `scripts/benchmarking/PIPELINE_TRACE.md`: complete original production/export/evaluation path. Do not run examples that write an old report/output.
8. Specialist pairs in `research/`: `benchmark_audit.md`/`.json`; `temporal_alignment_audit.md`/`temporal_alignment_tests.md`; `shuttle_perception_audit.md`/`shuttle_model_comparison.md`; `player_court_pose_audit.md`/`player_tracking_experiments.md`; `contact_event_audit.md`/`contact_event_experiments.md`; `rally_segmentation_audit.md`/`rally_failure_taxonomy.md`; `production_architecture_audit.md`/`modularity_and_reliability_plan.md`.

Read artifacts, not report summaries alone:

- `outputs/benchmarking/test1/`: `BENCHMARK_REPORT.md`, `predicted_rallies.csv`, `rally_comparison.csv`, `metrics.json`, `benchmark_metadata.json`, `boundary_diagnostics.json`, `inference.json`, `execution.log`, `raw_events.jsonl`, `profiles/`, `runtime/`, `initial_evaluation/`, `executed_scripts/`, source/proxy provenance audits. NEVER WRITE HERE.
- Best fresh:`artifacts/benchmarking/experiments/fresh_image_exit_v1/`: `predicted_rallies.csv`, `rally_comparison.csv`, `metrics.json`, `comparison.json`, `comparison.md`, `benchmark_metadata.json`, `inference.json`, `execution.log`, `events.jsonl`, `resources.jsonl`, `source.diff`, `profiles/experiment.yaml`, `proxy_alignment.json`, `post_run_validation.json`, `failure_cases/index.json`, `runtime/sessions/Test1Experiment/perception/*.msgpack`, raw tracks/events/runtime.
- Fresh semantic check:`artifacts/benchmarking/experiments/fresh_image_exit_semantic_check/{replay_metadata.json,fsm_trace.jsonl,events.jsonl,predicted_rallies.csv}`. All 39 interval/end-reason pairs and 447 livecontact timestamps reproduce exactly. This is NOT a second GPU run.
- Original exact semantic trace:`artifacts/benchmarking/investigation/baseline_semantic_replay/`:49 interval/end-reason pairs and 432 livecontact/stroke timestamps.
- Original 55 diagnosticpackages:`artifacts/benchmarking/investigation/failure_cases/index.json` (36 GT+19 FP).
- Fresh 40 packages:`artifacts/benchmarking/experiments/fresh_image_exit_v1/failure_cases/` (36 GT+4 FP). Start with `gt_04`, `gt_22`, `gt_23`, `gt_27`, `gt_31`, `fp_23`, `fp_24`, `fp_29`, `fp_33`. Each has `case.json`, `observations.msgpack`, `events.jsonl`, `fsm_trace.jsonl`, `execution.log`, `boundary_overlay.jpg`. Logs are whole-session where per-frame timestamps do not exist; never fabricate precise log slices.
- Original-frame residual review:`artifacts/benchmarking/investigation/remaining_visual_review/{frame_evidence.json,gt22_23_break.jpg,gt22_23_possible_edit_pairs.jpg,gt22_23_frame_differences.json,same_camera_edit_cut_probe.json,gt31_early.jpg,gt31_gap.jpg,gt31_gap_upper_original_pixels.jpg}`. Use unoverlaid top crop for visibility claims; some montage headings obscure upper pixels.
- Specialist evidence under `artifacts/benchmarking/investigation/{audit_a_final,audit_b,audit_c,audit_d/final,audit_e_final,audit_f,audit_g}/`. Especially `audit_b/gt27_stationary_point.jpg`, `audit_e_final/{summary.json,boundary_contact_evidence.json}`, `audit_f/{fsm_probe_results.json,replay_transition_extracts.json}`, and upstream pinned documentation/licenses in `audit_c/external_sources/manifest.json`, `audit_g/external_sources/manifest.json`.

Ignored local media/runtime/caches/logs/images are not restored by Git clone. Check availability before promises. If original video is missing, exact authorized Drive file ID:`1vR71QTkUYEGWy4PjXa5vfMdJEXt_OwLn` in supplied folder's video_raw subfolder. Download only that one, verify hash, do not fetch other videos or bypass access restrictions.

## Reference performance and selected configuration

Compare future work against BOTH the frozen original and best fresh v1; do not replace the original baseline.

| Metric | Original | Fresh v1 |
| --- | --- | --- |
| GT/pred/matched |36/49/30|36/39/35|
| TP/FP/FN |30/19/6|35/4/1|
| Precision/recall/F1 |.612245/.833333/.705882|.897436/.972222/.933333|
| Mean/median/minimum IoU |.763315/.767948/.504|.817808/.842809/.532995|
| Start MAE/RMSE frames |49.433/75.253|45.771/72.400|
| Start median/P90/max frames |23/117.6/202|29/98.2/297|
| Start signed bias frames |+48.033|+39.2|
| End MAE/RMSE frames |40.400/96.463|16.314/39.530|
| End median/P90/max frames |7/103.8/442|6/27/218|
| End signed bias frames |−33.4|−8.4286|
| Start/end MAE seconds |1.647778/1.346667|1.525714/.543810|
| Duration MAE/RMSE/bias seconds |2.845556/4.346378/−2.714444|1.894286/2.784908/−1.587619|
| Multi-segment GT |11|3:23,27,31|
| Predictions with zero GT overlap |0|0|
| Worker elapsed/FPS |1469.237/11.753|1509.996/11.4358|

All 30 prior matches remain. Prior misses 5,25,28,29,31 now match;23 remains missed. Common 30 start/end MAE49.433/40.400→36.433/17.667 frames. Newly matched start MAE101.8 frames is poor. Preserve improvements:GT2/19 start+179/+202→+4/+4;GT20 end−442→−20;GT3 end−103→−5;GT35 end−92→+5. GT33 start+168→+72 still needs work.

Explicit selected provider:`rally-evidence-v2`, flags `use_reconstruction=false`, `motion_guard=false`, `use_exit_recovery=true`. Opt-in profile:`config/profiles/gpu-rtx4000-rally-evidence.yaml`; ordinary `gpu-rtx4000.yaml` unchanged. Provider defaults differ from selected flags: always set them explicitly.

Numeric FSM defaults unchanged:start 3 moving speed samples>3 px/frame or accepted contact; gap 10; stationary 7 of 10<3; lookahead 15 relative to backdated tentative end (not 15 more frames after trigger); resume>6; min 2 s; merge.75 s=22 frames at 30 FPS by Python rounding. Engine future 40/backward 45 frames. TrackNetV3 remains 512×288,8 framewindows,step 8,batch 4,threshold.5,CUDA FP16; RF-DETR Small, RTMPose M Body7, geometric racket/contact and other analytics continue.

## Every GT row: exact current and original errors

Signed error=prediction−GT; duration error in seconds. Null means missed. These are fixed-evaluator assignments, not new labels. Small nonzero errors inside unknown annotation convention are not automatically confirmed defects. Preserve all rows and good controls.

| GT | GT frames | Fresh selected interval | Original start/end error | Fresh start/end error | Duration error s | IoU | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
|1|243–715|339–717|+96/+2|+96/+2|-3.133333|0.793249|matched|
|2|887–1262|891–1255|+179/-7|+4/-7|-0.366667|0.970667|matched|
|3|1398–1664|1402–1659|+4/-103|+4/-5|-0.300000|0.966165|matched|
|4|1874–2161|1803–2167|+15/+6|-71/+6|+2.566667|0.788462|matched|
|5|2210–2500|2309–2496|null/null|+99/-4|-3.433333|0.644828|matched|
|6|2558–2806|2661–2799|+103/-7|+103/-7|-3.666667|0.556452|matched|
|7|2976–3377|2983–3377|+7/+0|+7/+0|-0.233333|0.982544|matched|
|8|3451–3695|3523–3699|+72/+3|+72/+4|-2.266667|0.693548|matched|
|9|3751–4073|3863–4059|+112/-14|+112/-14|-4.200000|0.608696|matched|
|10|4247–4839|4344–4804|+97/-111|+97/-35|-4.400000|0.777027|matched|
|11|4872–5045|4901–5027|+29/-18|+29/-18|-1.566667|0.728324|matched|
|12|5430–5871|5455–5887|+25/+16|+25/+16|-0.300000|0.910284|matched|
|13|5958–6312|5979–6315|+21/-2|+21/+3|-0.600000|0.932773|matched|
|14|6382–6656|6451–6639|+69/-17|+69/-17|-2.866667|0.686131|matched|
|15|6716–6913|6803–6908|+87/-5|+87/-5|-3.066667|0.532995|matched|
|16|6976–7458|7006–7499|+30/+39|+30/+41|+0.366667|0.864245|matched|
|17|7532–7741|7535–7731|+3/-10|+3/-10|-0.433333|0.937799|matched|
|18|7947–8053|7953–8052|+6/-1|+6/-1|-0.233333|0.933962|matched|
|19|8106–8628|8110–8627|+202/-1|+4/-1|-0.166667|0.990421|matched|
|20|8683–9967|8715–9947|+32/-442|+32/-20|-1.733333|0.959502|matched|
|21|10245–10563|10250–10539|+5/-24|+5/-24|-0.966667|0.908805|matched|
|22|10607–10708|10578–10737|-6/+29|-29/+29|+1.933333|0.635220|matched|
|23|10733–11078|unmatched|null/null|null/null|null|null|missed|
|24|11271–11392|11274–11397|+3/+5|+3/+5|+0.066667|0.936508|matched|
|25|11568–11865|11613–11867|null/null|+45/+2|-1.433333|0.842809|matched|
|26|11976–12197|12046–12196|+70/-1|+70/-1|-2.366667|0.678733|matched|
|27|12451–12966|12455–12748|+4/-218|+4/-218|-7.400000|0.568932|matched|
|28|13054–13442|13115–13439|null/null|+61/-3|-2.133333|0.835052|matched|
|29|13679–13994|13686–13982|null/null|+7/-12|-0.633333|0.939683|matched|
|30|14219–14335|14222–14331|+3/-4|+3/-4|-0.233333|0.939655|matched|
|31|14404–15151|14701–15171|null/null|+297/+20|-9.233333|0.586701|matched|
|32|15350–15535|15354–15529|+4/-6|+4/-6|-0.333333|0.945946|matched|
|33|15596–15946|15668–15951|+168/+5|+72/+5|-2.233333|0.783099|matched|
|34|15998–16387|15983–16385|-15/-2|-15/-2|+0.433333|0.957921|matched|
|35|16513–17026|16521–17031|+8/-92|+8/+5|-0.100000|0.974903|matched|
|36|17066–17226|17074–17207|+8/-22|+8/-19|-0.900000|0.831250|matched|

Four unmatched predictions remain policyFP; all overlapGT, none is a zero-overlap hallucination. GT-dependent coverage unions never generate intervals.

| Prediction/package | Frames | Originalseconds | Context |
| --- | --- | --- | --- |
|23/fp_23|10769–10908|358.966667–363.600000|GT23 first substantial fragment|
|24/fp_24|10949–11085|364.966667–369.500000|GT23 later fragment|
|29/fp_29|12771–12954|425.700000–431.800000|GT27 later fragment|
|33/fp_33|14430–14646|481.000000–488.200000|GT31 early fragment|

## Complete issue register

P0:review severe failures/regressions first. P1:accuracy/validation work. P2:targeted reliability/measurement. P3:non-causal maintenance/warnings. Reprioritize only with evidence. These are not all established algorithmic bugs.

### H01 — P0: GT23 remains missed; fragmentation and an unflagged same-camera edit

**Status:** Measured failure; edit has strong visual evidence; intended human onset remains unknown.

**Evidence:** GT10733–11078 has unmatched fresh pieces 10769–10908 and 10949–11085 plus preceding spillover. Original 10769→10770 jumps player positions; histogram correlation.9959220991>.55 leaves CutDetector false and shotID25. Label starts 37 frames before edit during preparation.

**Owner files:** `sports/badminton/src/bai_badminton/perception/scene.py`, `sports/badminton/src/bai_badminton/perception/pipeline.py`, `sports/badminton/src/bai_badminton/events/rally_evidence.py`, `sports/badminton/src/bai_badminton/engine.py`.

**Next experiment/action:** Review 10680–11090 with fresh gt_23/fp_23/fp_24 and exact transitions. Separate true break/preparation, edit detection and 10909–10947 loss. Test a reviewed foreground-continuity/cut cue separately from recovery; better cut detection is not automatically better rally IoU.

**Controls/risks:** Preserve GT22/23 as separate labels. Do not join all overlapping pieces, fit a cut threshold to this pair, or change GT10733.

### H02 — P0: GT27 ends 218 frames early; static court-line peak is a likely attractor

**Status:** Measured failure and proven state chain; model localization diagnosis is not pixel ground truth.

**Evidence:** GT12451–12966 matches 12455–12748; extra 12771–12954 remains FP. End−218 frames/−7.2667 s; duration−7.4 s. Baseline points 12748–12768 stick near proxy(645,393), support.51–.58 on painted serviceT during overhead action. Accepted contact 12771 is 23 frames beyond endpoint, outside 22 frame budget.

**Owner files:** `sports/badminton/src/bai_badminton/perception/tracknet.py`, `sports/badminton/src/bai_badminton/perception/shuttle_post.py`, `sports/badminton/src/bai_badminton/events/contact.py`, `sports/badminton/src/bai_badminton/events/rally_fsm.py`.

**Next experiment/action:** Retain top-k peak/rejection diagnostics; inspect 12735–12790/fullGT27. Isolate background/context and temporal candidate association. Separately inspect suspicious contact impulse and terminal stationarity validity.

**Controls/risks:** Test real floor/spare shuttles, static lines, slow flight, apexes, launches and landings. Player-motion guarding failed; do not increase merge budget by one frame just for this case.

### H03 — P0: GT31 becomes matched but starts 297 frames/9.9 seconds late

**Status:** Measured severe residual; view exclusion and mixed physical/model loss evidenced.

**Evidence:** GT14404–15151 matches 14701–15171 (+297,+20; duration−9.2333 s); extra 14430–14646 remains. Source 14404–14420 is pickup close-up; wide around 14425. Baseline provisional 14430 cancelled 14467 then 14491 starts; verify fresh history separately. Model loss 14647–14694 spans observed endpoints(879.22,87.84)→(936.07,240.61). Source streaks visible 14648,14684/88/90 before reacquisition 14695.

**Owner files:** `sports/badminton/src/bai_badminton/perception/scene.py`, `sports/badminton/src/bai_badminton/perception/tracknet.py`, `sports/badminton/src/bai_badminton/events/rally_motion.py`, `sports/badminton/src/bai_badminton/events/rally_evidence.py`, `sports/badminton/src/bai_badminton/engine.py`.

**Next experiment/action:** Review 14390–14710, original unoverlaid top crops and fresh cancellation/recovery. Separate close-up observability from recoverable post-cut onset; test trajectory uncertainty/candidate association with independent anchors.

**Controls/risks:** Do not backdate into close-up, call excluded frames verified replay, widen top band to fit 240.61, or merge every 48 frame gap.

### H04 — P0: New early starts at GT4 and GT22

**Status:** Measured genuine common-row regressions; exact cause still needs trace isolation.

**Evidence:** GT4 label 1874–2161: baseline 1889–2167 becomes 1803–2167, start+15→−71 frames/−2.3667 s. GT22 start 10607:10601→10578, error−6→−29. These are not effects of adding new matches.

**Owner files:** `sports/badminton/src/bai_badminton/events/rally_evidence.py`, `sports/badminton/src/bai_badminton/events/rally_motion.py`, `sports/badminton/src/bai_badminton/events/rally_fsm.py`, `sports/badminton/src/bai_badminton/engine.py`.

**Next experiment/action:** Review source/fresh gt_04 and gt_22, early provisional starts/contacts and exact support flags. Determine which intervention retains or joins an earlier candidate; create a source-supported negative control before changing rules.

**Controls/risks:** Retain recovered GT2/19/20 and legitimate short breaks. Report both baseline and fresh-v1 comparisons.

### H05 — P1: Persistent multi-second starts and cancelled initial candidates

**Status:** Measured failures; per-case roots not all established.

**Evidence:** Fresh starts: GT1+96,5+99,6+103,8+72,9+112,10+97,14+69,15+87,20+32,25+45,26+70,28+61,33+72,31+297 frames. GT6/8/9 have localized excluded views. Baseline GT5 detects 2210 then cancels a 45 frame candidate under 60 frame minimum. Three speed samples normally require four adjacent observed positions.

**Owner files:** `sports/badminton/src/bai_badminton/engine.py`, `sports/badminton/src/bai_badminton/events/rally_fsm.py`, `sports/badminton/src/bai_badminton/events/contact.py`, `sports/badminton/src/bai_badminton/perception/pipeline.py`, `sports/badminton/src/bai_badminton/perception/tracknet.py`.

**Next experiment/action:** Classify every delayed row: first raw observation, adjacent processed motion, contact, provisional start, cancellation, discontinuity and surviving start. Investigate independent start evidence or event-triggered fresh pose without collapsing all into fragmentation.

**Controls/risks:** Do not subtract an average delay or lower minimum duration to fit labels. Keep short genuine rallies, break noise and weak launches as separate controls.

### H06 — P1: Residual end errors and truncated durations

**Status:** Measured failures; verified general end/landing evidence absent.

**Evidence:** Fresh ends GT10−35,16+41,20−20,21−24,22+29,31+20,36−19. Genuine end regressions: GT8+3→+4,13−2→+3,16+39→+41. Duration MAE1.894286 s,RMSE2.784908 s,bias−1.587619 s. Start/end signed biases+39.2/−8.4286 frames.

**Owner files:** `sports/badminton/src/bai_badminton/events/rally_fsm.py`, `sports/badminton/src/bai_badminton/events/rally_evidence.py`, `sports/badminton/src/bai_badminton/events/rally_motion.py`, `sports/badminton/src/bai_badminton/engine.py`, `sports/badminton/src/bai_badminton/events/rally_outcome.py`.

**Next experiment/action:** Investigate end independently of start; separate observed terminal support, temporary missingness and ambiguous/static position. Evaluate endpoint refinement from production evidence only.

**Controls/risks:** Slow position is not confirmed landing; score/winner confidence cannot validate a boundary. Preserve nearby legitimate breaks and all duration/outlier metrics.

### H07 — P1: Fine boundary accuracy remains poor

**Status:** Measured quality limitation.

**Evidence:** No start within±1 frame; only 3/36 within±3. At±30 start 20/36,end 32/36. Start median worsens 23→29 frames and max 202→297; matched-only±30 falls 60%→57.14% as coverage increases, while all GT improves 50%→55.56%.

**Owner files:** `scripts/benchmarking/evaluate_rallies.py`, `research/compare_rally_experiments.py`.

**Next experiment/action:** Track common/new matches, both tolerance denominators, signed bias and every severe error; obtain reviewed onset/offset convention evidence before one-frame claims.

**Controls/risks:** Never use F1/IoU alone, replace null misses with zero, or choose easier matches to hide outliers.

### H08 — P1: Shuttle rejection reasons/weak competing peaks are discarded

**Status:** Proven observability gap.

**Evidence:** heatmap_to_point/pipeline reduce distinct low peak, competing component, mask rejection and absence to(None,0). Caches lack subthreshold/top-k peaks or heatmaps. Baseline 11767/17268 accepted outputs and 107 missing runs≥10 frames measure coverage, not visibility recall.

**Owner files:** `sports/badminton/src/bai_badminton/perception/tracknet.py`, `sports/badminton/src/bai_badminton/perception/pipeline.py`, `sports/badminton/src/bai_badminton/perception_types.py`, `sports/badminton/src/bai_badminton/plugin.py`.

**Next experiment/action:** Add bounded opt-in candidate/peak/mask/rejection/vote metadata with provenance. First prove numerical prediction parity; version relevant cache/schema identities.

**Controls/risks:** No full-video heatmap dump, invented coordinates/confidence or broken independent shuttle provider. Keep diagnostics bounded.

### H09 — P1: Background/resize/peak selection/chunk effects remain confounded

**Status:** Implementation differences proven; accuracy causes unmeasured.

**Evidence:** INTER_AREA differs from referencePIL; rolling per-shot median differs from fixed/rally median; global-max component lacks multi-hypothesis association. VOD effective 60 differs from profile 64, causing step 8 tail overlap. Both step 8/4 remove static T accepted peaks under fixed background/180 frame context; cannot credit step 4.

**Owner files:** `sports/badminton/src/bai_badminton/perception/tracknet.py`, `sports/badminton/src/bai_badminton/perception/pipeline.py`, `engine/src/bai_engine/runtime/runner.py`, `engine/src/bai_engine/media/proxy.py`.

**Next experiment/action:** Separate background-only, resize-only, context-only and temporal association trials; use factorials for interactions. Pin images/masks/checkpoint/precision; compare localization only with labels and downstream intervals separately.

**Controls/risks:** Step 8 emits every frame; not seven-of-eight skipping. Missing an old distractor is not recovered correct shuttle localization.

### H10 — P1: Near-zero velocity can saturate contact impulse/redirect

**Status:** Proven numerical sensitivity; real contact-error rate unknown.

**Evidence:** ratio=post/max(pre,1e−6), rejection only if both speeds<.5. GT27 contact 12748: .0228→1.1602 px/frame, redirect 1,impulse 1, proximity.0656,score.7297. Controlled 2.4 px turn near 100 px body yields.977989 without pose/racket; not a human-labeled false hit.

**Owner files:** `sports/badminton/src/bai_badminton/events/contact.py`, `sports/badminton/src/bai_badminton/participant_contact.py`, `sports/badminton/src/bai_badminton/engine.py`.

**Next experiment/action:** Expose velocity reliability; compare absolute motion/acceleration against relative ratio in opt-in contact provider. Review contact timing before calibration or weight changes; isolate from segmentation.

**Controls/risks:** Blunt incoming-speed floor suppresses valid low-speed serve launches. Include apexes, quantization, occlusion and boundary hits.

### H11 — P1: Sparse direct racket evidence and sparse pose cadence

**Status:** Measured baseline availability; causal accuracy loss unproven.

**Evidence:** Baseline 432 contacts:83 geometric racket cues,6 ellipse overlaps,0 observed physical impacts;55 lack two same-frame poses;330 positive swing. Racket acquisition requires fresh matched player/wrist. Fresh 447 contacts are a separate stream.

**Owner files:** `sports/badminton/src/bai_badminton/perception/racket.py`, `sports/badminton/src/bai_badminton/perception/players.py`, `sports/badminton/src/bai_badminton/perception/pipeline.py`, `sports/badminton/src/bai_badminton/events/contact.py`.

**Next experiment/action:** Test event-triggered current-frame pose/racket around uncertain onsets; ablate trajectory/body/pose/racket coverage and reviewed timing, then rally metrics/runtime.

**Controls/risks:** Do not require overlap for every real hit, invent skipped poses or call confirmed ledger entries physical impacts. Counts alone are not accuracy.

### H12 — P2: Player rejection and association quality cannot be diagnosed fully from existing caches

**Status:** Proven telemetry/label gap.

**Evidence:** Baseline 19947/33550 returned rows are carried/tracker-only;126 main-view frames have no people. Rejected detector boxes/reasons absent. Raw IDs 0..10 and 37 reset events are not eleven athletes or measured identity errors.

**Owner files:** `sports/badminton/src/bai_badminton/perception/players.py`, `sports/badminton/src/bai_badminton/perception/player_association.py`, `sports/badminton/src/bai_badminton/perception/isolation.py`, `sports/badminton/src/bai_badminton/participant_contact.py`.

**Next experiment/action:** Add compact pre/post-ROI/admission/capacity counters and provenance; obtain reviewed track episodes for association claims.

**Controls/risks:** Preserve fresh-versus-carried flags, four-person retention, jumps/runoff, spectators/adjacent courts, cut epochs and unnamed actors.

### H13 — P2: Geometry confidence is not independent physical accuracy

**Status:** Validation limit; not universal court failure.

**Evidence:** Baseline 16941 valid-geometry frames/RMS≈1.137 proxy pixels measure line agreement. GT2/5/27 full geometry still fail. Fresh 285 camera-lost frames are present frames, not dropped video. Floor homography is not airborne 3 D trajectory or contact measurement.

**Owner files:** `sports/badminton/src/bai_badminton/court.py`, `sports/badminton/src/bai_badminton/perception/court_lines.py`, `sports/badminton/src/bai_badminton/perception/calibration_state.py`, `sports/badminton/src/bai_badminton/perception/camera.py`, `sports/badminton/src/bai_badminton/participant_geometry.py`.

**Next experiment/action:** Inspect localized lost/reacquiring windows; require reviewed landmarks before geometry-quality claims. Keep image-space support separate from grounded feet and airborne physics.

**Controls/risks:** Do not relax invalid-view gates globally or blame GT20 end 9525 on unrelated view loss near 8697.

### H14 — P2: OSNet/ReID unavailable; named actors intentionally unknown

**Status:** Known degradation; not proven universal boundary cause.

**Evidence:** Both runs explicitly record missing osnet_ain_x 0_25 and unavailable player_reid. Unknown format becomes singles at 120. Detector/pose/anonymous contacts still work; all 432 baselinecontact frames have two people. No restored-weight ablation or identity GT.

**Owner files:** `sports/badminton/src/bai_badminton/perception/pipeline.py`, `sports/badminton/src/bai_badminton/perception/players.py`, `sports/badminton/src/bai_badminton/perception/player_association.py`, `sports/badminton/src/bai_badminton/identity.py`, `sports/badminton/src/bai_badminton/format_understanding.py`.

**Next experiment/action:** Restore pinned provider only as separate justified experiment with identity labels/license/device/hash, preserving explicit failure states.

**Controls/risks:** Never fabricate embeddings/names, equate track/person/team/scoring slot, silently force singles or claim restoring ReID necessarily fixes rallies.

### H15 — P2: Uncalibrated scores and requested backend labels can mislead

**Status:** Proven confidence semantics/measurement limitation.

**Evidence:** 894 baselinepose keypoint scores>1 (max 1.2037). Shuttle/contact support is uncalibrated. RequestedFP16/CUDA-firstORT does not prove every tensor/nodeCUDA FP16. gpu-rtx 4000 description namesRTX/TensorRT; actual server is Pascal torch/ORT CUDA.

**Owner files:** `sports/badminton/src/bai_badminton/perception/components.py`, `sports/badminton/src/bai_badminton/perception/pipeline.py`, `sports/badminton/src/bai_badminton/events/contact.py`, `sports/badminton/src/bai_badminton/events/rally_evidence.py`, `research/run_pipeline_experiment.py`.

**Next experiment/action:** Preserve raw support; calibrate only on reviewed held-out labels. Read actual execution_backends/artifact hashes; profile per-node precision only if needed.

**Controls/risks:** Do not clip scores and rename probabilities, infer active optional models from config names or replace runtime because of a misleading description.

### H16 — P1: Segmentation changes upstream cadence; naive fusion reads future activity

**Status:** Proven dependency/synchronization risk; current aligned helper is intentional.

**Evidence:** Rally state controls later player/pose stride; fresh contacts 447 vs baseline 432. Semantic frontier trails 40 frames; current self.activity can be ahead of decision frame. Correct adapter uses episode_window/aligned snapshots.

**Owner files:** `sports/badminton/src/bai_badminton/plugin.py`, `sports/badminton/src/bai_badminton/engine.py`, `sports/badminton/src/bai_badminton/observations.py`, `sports/badminton/src/bai_badminton/events/rally_motion.py`, `sports/badminton/src/bai_badminton/perception/pipeline.py`.

**Next experiment/action:** Keep exact frame/episode/cadence alignment; use cache replay for conditional diagnosis then fresh inference. Compare each run’s own observations/contact stream.

**Controls/risks:** No future activity as historical evidence, no restoring private tracker/cut/background state from diagnostic caches, no replay-as-inference claims.

### H17 — P1: Top-exit cue has designed coverage limits

**Status:** Conservative applicability limit; GT31 supports one false-negative mechanism.

**Evidence:** Requires observed moving brackets within 5 frame anchors, upward/downward motion, both endpoints in actual top 10%image, gap≤2 s, same context and 3..120 px/frame. Needs after-anchors already available. Cannot recover stationary CLOSED/published/IDLE/cut contexts.

**Owner files:** `sports/badminton/src/bai_badminton/events/rally_motion.py`, `sports/badminton/src/bai_badminton/events/rally_evidence.py`, `sports/badminton/src/bai_badminton/engine.py`.

**Next experiment/action:** Evaluate uncertainty/other exit patterns or provisional retention only with supported evidence and prespecified break controls. Keep support basis/rejection reasons visible.

**Controls/risks:** No GT-fitted band, hidden extra lookahead, coordinates/contacts/idle starts from interpolation or body movement.

### H18 — P2: VOD behavior is not validated as causal live behavior

**Status:** Mode limitation; not offline timing defect.

**Evidence:** Background preparation observes whole chunk; semantics use 40 future/45 past frames; exit cue may use future anchors. Publication latency is not a shift of canonical event time.

**Owner files:** `sports/badminton/src/bai_badminton/perception/tracknet.py`, `sports/badminton/src/bai_badminton/perception/pipeline.py`, `sports/badminton/src/bai_badminton/engine.py`, `engine/src/bai_engine/runtime/runner.py`.

**Next experiment/action:** Declare VOD/live capabilities and causal latency; test streaming/chunk edges if exposing live mode.

**Controls/risks:** No unavailable future anchors or zero-latency claim; preserve VOD benchmark and canonical times.

### H19 — P2: VFR/unsupported/high-FPS generic ingestion needs explicit mappings

**Status:** Source-supported risk not triggered by CFR30 Test 1.

**Evidence:** plan_proxy maps unsupported rates to 30 and>60 to 60; VFR probe compares aggregate rates, not everyPTS. Proxy/source frame index equality need not hold for future inputs.

**Owner files:** `engine/src/bai_engine/media/probe.py`, `engine/src/bai_engine/media/proxy.py`, `engine/src/bai_engine/decode.py`.

**Next experiment/action:** Use synthetic VFR/high-rate fixtures and explicit original↔canonical mappings for justified generic hardening.

**Controls/risks:** No fitted Test 1 offsets, silent FPS changes/source alteration or badminton logic in generic media.

### H20 — P2: Browser HLS seek/callback alignment remains untested

**Status:** Playback hypothesis, not proven UI defect or offline root cause.

**Evidence:** Raw HLS origin 323/15360 s=.630859 frame. Canonical decoder correct; frameClock floors mediaTime; VideoStage seeks(frame+.5)/fps, possibly before raw PTS if browser retains origin.

**Owner files:** `apps/web/src/lib/frameClock.ts`, `apps/web/src/features/player/VideoStage.tsx`, `engine/src/bai_engine/decode.py`.

**Next experiment/action:** Run real browser HLS frame-seek/callback checks against canonical images; separately testMP4/HLS/live normalization.

**Controls/risks:** Do not subtract HLS mux origin from benchmark CSVs or attribute hundred-frame errors to this untested sub-frame hypothesis.

### H21 — P2: Runtime cost increase and growing rollback history need isolated profiling

**Status:** Measured walltime difference; algorithmic cost/rollback bottleneck unproven.

**Evidence:** 1509.996 s vs 1469.237 s (+2.774%); CPU regression tests overlapped fresh startup. Semantic 83.729 s, parent perception 1302.995 s,players 529.960 s,OCR345.601 s,shuttle 216.652 s have overlapping scopes. TransactionalAnalytics.checkpoint deepcopies accumulated operations: source hypothesis, not measured leak.

**Owner files:** `sports/badminton/src/bai_badminton/engine.py`, `sports/badminton/src/bai_badminton/components.py`, `sports/badminton/src/bai_badminton/analytics/match.py`, `research/run_pipeline_experiment.py`.

**Next experiment/action:** Profile isolated stage/transaction cost versus operation/frame count; persist decode/init/inference/export and resource cadence before smallest justified optimization.

**Controls/risks:** Never remove analytics/rollback/accepted evidence for speed. Baseline per-stage/CPU/RSS/GPUpeaks unavailable; allocator/PID/device scopes differ.

### H22 — P1: Only one independent fresh candidate GPU run exists

**Status:** Validation gap, not failed repeat.

**Evidence:** Exact 39 interval/end-reason and 447 contact parity comes from replaying new caches, not another neural-model run.1895 software passes do not establish neural accuracy/determinism.

**Owner files:** `research/run_pipeline_experiment.py`, `research/replay_rally_evidence.py`, `research/component_test_report.md`.

**Next experiment/action:** Repeat frozen source/environment into a new directory under isolated load; compare hashes, observations, contacts, all boundary metrics and resources. Report actual nondeterminism if any.

**Controls/risks:** Do not count semantic replay or mocked tests as new GPU inference.

### H23 — P1: Independent labels/generalization and alternative-model validation are missing

**Status:** Dataset/adoption gap; candidate stays exploratory opt-in.

**Evidence:** Only 36 intervals from one exposed broadcast singles video. No reviewed pixel visibility/location, contact/hitter/identity/courtGT or real annotated doubles/amateur evaluation. Training overlap unknown. No alternative weights run.

**Owner files:** `research/shuttle_model_comparison.md`, `research/modularity_and_reliability_plan.md`, `research/implementation_roadmap.md`.

**Next experiment/action:** Collect reviewed component evidence and match-disjoint boundary videos. Screen model task-fit, compatible weights, latency/VRAM and separate code/weight/data rights. RacketVision 4 frame is not 8 frame drop-in; MS-TCN has CommonsClause; ActionFormer lacks domain labels/frame-boundary guarantees.

**Controls/risks:** No generalization or calibration claim from Test 1; synthetic doubles tests are contract coverage only.

### H24 — P2: Empty-GT comparison output has no CSV header

**Status:** Proven general export defect; no Test 1 score defect.

**Evidence:** save_evaluation constructs comparison writer/header only inside if rows.36 row Test 1 arithmetic/matching independently verified.

**Owner files:** `scripts/benchmarking/evaluate_rallies.py`, `tests/benchmarking/test_prediction_schema.py`.

**Next experiment/action:** If addressed, add focused empty-input schema/header test and fix export only, separately from detector work.

**Controls/risks:** Keep exact primary schema/matching/IoU threshold/endpoints/tolerance denominators and frozen artifacts unchanged.

### H25 — P2: Factorial executor provenance and fixed Test 1 assumptions need hardening

**Status:** Confirmed source-level tooling limitation; fresh-run source provenance valid.

**Evidence:** run_evidence_ablations spreads replay metadata: verified repeats fix actual switches and FSM-only timing, but inherited git_commit/source identify source replay, not necessarily later executor. Older elapsed/overrides misleading. Ablation harnesses hardcode recorded format-reset at 119, not a rally label.

**Owner files:** `research/run_evidence_ablations.py`, `research/run_fsm_ablations.py`, `research/replay_rally_evidence.py`.

**Next experiment/action:** New runs should record executor SHA/dirty diff/harness hash separately from trace-generator/source metadata. Derive format epochs from recorded events for other datasets; preserve historical limitations.

**Controls/risks:** Inherited source_unchanged is not a fresh executor validation. Separate FSM-loop/semantic/neural timing; never edit old manifests to imply better provenance.

### H26 — P2: Ignored evidence and fixed finalizers can invalidate next-session workflows

**Status:** Workflow risk, not prediction failure.

**Evidence:** artifacts/benchmarking and original media are ignored; a clone lacks caches/logs/images. finalize_pipeline_investigation is hardcoded to v1/counts/measured source and writes historical reports. Some audits have fixed output defaults; comparator refuses overwrites.

**Owner files:** `research/finalize_pipeline_investigation.py`, `research/build_failure_cases.py`, `research/compare_rally_experiments.py`, `scripts/benchmarking/README.md`, `.gitignore`.

**Next experiment/action:** Check local evidence availability, back it up outsideGit if moving, and use new experiment/report IDs. Do not run old finalizer after source edits as generic validator.

**Controls/risks:** No deleting evidence to bypass refusals, historical regeneration, or large media/checkpoint/raw cache commits.

### H27 — P3: RapidOCR empty-result warnings remain

**Status:** Observed warning; direct boundary causality not established.

**Evidence:** Both execution logs warn text detection result empty. OCR executes/costs time; final rally export does not require score/winner/official status.

**Owner files:** `sports/badminton/src/bai_badminton/perception/scoreboard.py`, `sports/badminton/src/bai_badminton/score_ocr.py`, `sports/badminton/src/bai_badminton/engine.py`.

**Next experiment/action:** Preserve warnings/unknown score evidence; investigate only if real boundary dependency or separately authorized analytics work warrants it.

**Controls/risks:** No invented scores or removing OCR/other analytics to improve benchmark cost/F1.

### H28 — P3: Pre-existing formatting/deprecation warnings

**Status:** Non-causal maintenance debt.

**Evidence:** Historical full suite 1895 passed/no skips/19 HTTP422 Starlette-FastAPI deprecations. Rufflint 27 files passed; format 26 passed with unchanged plugin review_action string issue also present onmain.

**Owner files:** `sports/badminton/src/bai_badminton/plugin.py`, `research/component_test_report.md`.

**Next experiment/action:** Keep cosmetic/compatibility maintenance separate from algorithmic experiments.

**Controls/risks:** Do not call warnings segmentation failures or reformat measured production source merely to change identity.

## Already fixed: preserve these changes

| Commit | Completed work | Caveat |
| --- | --- | --- |
|3859f83|Seven audits/diagnosis/prespecified plan before production edits|Old audit future tense must be reconciled with later source|
|6aa79ac|Configured stationary-buffer sizing; contact-history rebasing; CLOSED recovery uses motion-run onset, retains in-budget candidate until confirmation|11 intended red cases fixed; contact-only does not improve accuracy; onset-only recoversGT28|
|b60f114|Injected registry.models_dir used instead of global settings for derived caches|Constructor regression tests for unknown/singles/doubles; no weight migration|
|af70da7|Optional typed observed/reconstructed/missing/invalid port/provider; aligned motion/reconstruction helpers; isolated experiment observer|Legacy public port and non-badminton host remain valid|
|7c83b00|Bounded observed image-exit/return with negative controls|No IDLE start, invented coordinate/contact, cut crossing or reopening published interval|
|3653b0d|Explicit opt-in profile and frozen extended factorial|Actual fresh measured source|
|e8877b2|Actual fresh result/reports/all 27 experiment evaluations; verified factorial timing/provenance repeat|No independent held-out/generalization claim|

Keep `_EvidenceRally`/`_Rally` reset/checkpoint behavior, versions/cache invalidation and participant provenance. Do not read baseline-private FSM internals from arbitrary independent providers.

## Rejected experiments and result traps

Paths relative to `artifacts/benchmarking/experiments/`:

- `fsm_correctness/{control,contact_history_only,motion_onset_clock_only,combined}`:F1.705882/.705882/.738095/.738095. Combined start MAE50.548 frames; correctness is not an automatic accuracy gain.
- `reconstruction_semantic`:44 pred/32 TP/12 FP/4 FN,F1.8,start MAE62.906; wronglyjoinsGT33/34. Input validation changed during run; preserved diagnostic pilot explicitly invalid for acceptance.
- `evidence_ablations/reconstruction_only`:44/32/12/4,F1.8,start MAE55.25. Strict bracket version fixes pilot quality issue but is still not preferred.
- `evidence_ablations/motion_only`:27 TP/9 FN,F1.650602; combined 28 TP/8 FN,F1.708861 despite meanIoU.801974. `evidence_feature_replay_v1` is completed semantic combined replay, not fresh inference. Player-motion guard rejected.
- `image_exit_factorial/{exit_only,exit_reconstruction}`:39 pred/35 TP/4 FP/1 FN,F1.933333; byte-identical CSVs. Select exit-only; generic reconstruction adds no gain here.
- `image_exit_factorial/{exit_motion,all_signals}`:exactly 36 predictions but 32 TP/4 FN,F1.888889. Count 36 is not success; motion loses 3 matches.
- `image_exit_factorial_verified/*`:8 settings reproduce earlier predictions/metrics byte-for-byte with explicit actual overrides/config and measured FSM-only.1313–.1381 s. Inherited old semanticelapsed is not per-variant time. Repeats are not independent datasets or GPU inference.
- `image_exit_feature_replay_v1`:partial artifacts, no completed metrics/manifest; never count it completed or use as sole evidence.
- `tracknet_window_pair`:actual CUDA FP16 at same checkpoint on 12×180=2160 frames/strategy; step 8/4 accepted 1582/1567 in 20.355/29.722 s,1.46×cost. Both 0/17 during 9526–9542 and 0/21 at original static T under fixed background/180 frame context, which differs from rolling 60 frame production. No localization labels or full-rally F1 gain; keepstep 8.

Activity is not a standalone oracle:1625 baselineactive-play frames outsideGT, zero inactive decisions, GT24 goodmatch despite zeroactive-playactivity. Player stationarity is not old FSM input. OSNet absence does not erase anonymous contact evidence. Correct offline timebase/evaluator are already falsification controls.

## Source and test ownership map

Use actual repo-relative paths below; shorter names after a full prefix share that directory.

- Generic ingestion:`engine/src/bai_engine/media/{probe,proxy,ffmpeg}.py`; `engine/src/bai_engine/decode.py` (`SegmentDecoder`).
- Generic scheduling/runtime:`engine/src/bai_engine/runtime/runner.py` (`SessionRunner._ensure_media`, `_perceive`, `_analyse`); `engine/src/bai_engine/config.py`, `sport.py`, `components.py`, `runtime/registry.py` (`ModelRegistry.open_verified`), `schema.py`, `store/events.py` (`EventStore.query`).
- Sport orchestration:`sports/badminton/src/bai_badminton/plugin.py` (`BadmintonSession`, sequential-perception/cache codec/isolation identity), `components.py` (`RallySegmentation`, `EvidenceRallySegmentation`, `_Rally`, `_EvidenceRally`, registration, `TransactionalAnalytics`).
- Sport perception:`sports/badminton/src/bai_badminton/perception/pipeline.py` (`process`, `_scene`, `_degrade`, `seed_background`), `scene.py` (`CutDetector`), `tracknet.py` (`TrackNetV3._prep/_forward/detect`, `BackgroundModel`, `heatmap_to_point`), `shuttle_post.py` (`remove_spikes`, `fill_gaps`, `process`), `players.py` (`PlayerDetector`, `PlayerPerception`, `_carry`, `_attach`), `components.py`, `player_association.py`, `racket.py`, `keypoints.py`, `isolation.py` (`flight_mask`), `calibration_state.py`, `court_lines.py`, `camera.py`.
- Sport aligned evidence:`sports/badminton/src/bai_badminton/{court,observations,perception_types,participant_contact,participant_geometry,identity,format_understanding}.py`; `participant_window` creates aligned target-court episodes.
- Sport events:`sports/badminton/src/bai_badminton/events/contact.py` (`score_frame`, `detect_contacts`, contextual velocities/NMS), `activity.py`, `rally_fsm.py`, `rally_evidence.py` (`RallyObservation`, `ObservationKind`, `EvidenceRallyFSM.step_evidence`), `rally_motion.py` (participant motion, strict reconstruction and image-exit helpers).
- Semantic interval ownership:`sports/badminton/src/bai_badminton/engine.py` (`_append`, `_window`, `_advance`, `_handle_fsm`, `_finalize_pending`, `_finalize_rally_once`, `_score_transaction`).
- Preserve unrelated capabilities:`events/rally_outcome.py`, `events/stroke.py`, `rules/`, team/scoring/identityreview and `analytics/match.py`. No class/score/winner accuracy claim without correspondingGT.
- Export/evaluation:`scripts/benchmarking/{evaluate_rallies,production_inference,run_test1_benchmark,report_test1_benchmark}.py`. Primary evaluator and seven-column export remain the comparable contract.

Research tools and cautions:

- `research/run_pipeline_experiment.py`:isolated REAL production worker; labels read by parent only after prediction export. Builds profile from frozen baseline plus explicit rally/step overrides. `--video` still enforcesTest 1 hash/frontier 17267; not generic new-video harness. Worker/source fingerprints/dirty diff/logs captured.
- `research/replay_rally_evidence.py`:actual decoder/semantic engine consuming cached perception, no annotation values; saves exact trace/parity/source/cache hashes. Nonempty overrides and candidate mode bypass default parity assertion: manually assert parity for reproduction claims.
- `research/run_fsm_ablations.py`, `run_evidence_ablations.py`:conditional fixed-input comparisons; fixed output/default/epoch assumptions require adaptation for new runs/datasets.
- `research/compare_rally_experiments.py`:unchanged evaluator plus full-row distributions/coverage/fragmentation/topology; refuses old comparison files.
- `research/build_failure_cases.py`:new run requires explicit interval-parity trace; uses GT only for diagnostic grouping. External cache reuse remains conditional and must be disclosed.
- `research/audit_a_benchmark.py`, `audit_b_temporal.py`, `audit_c_observations.py`, `audit_c_window_contract.py`, `audit_c_paired_inference.py`, `audit_d_player_observations.py`, `audit_e_contacts.py`, `audit_f_fsm_probes.py`:check fixed default outputs first; some can overwrite their own diagnostics. Old-class probes must target intended historical source rather than blindly assert old bugs against fixed code.
- `research/finalize_pipeline_investigation.py`:hardcoded v1 publisher/verifier/counts/source; DO NOT use after source edits as generic validator or overwrite historical reports.

## Next-session sequence and acceptance

1. Inspect status/runtime/evidence and freeze current references. Reproduce existing metrics read-only, verify input/checkpoint hashes, check local ignored artifacts. Do not regenerate baseline.
2. Diagnose H01–H07 using fresh trace/source frames and all 36 comparisons; review new GT4/22 regressions as well asGT23/27/31. Classify every late onset, not only worst three. Visual/model evidence remains diagnostic until reviewed.
3. Write targeted experiment plan and falsifying controls. Start with parity-preserving candidate/rejection telemetry, then independently test justified background/context/association/contact/start/end interventions. One variable per trial; factorial for interacting changes. Challenge all proposed remedies.
4. Add meaningful failing regression for a proven owning-module issue; implement smallest modular fix. Preserve typed independent providers, generic non-badminton host, lifecycle/checkpoint/cache invalidation, singles/four-player and other analytics. Change contract versions when required.
5. Freeze/commit code before expensive inference or record exact dirty source/harness fingerprints. No production edits during worker/replay. Every experiment gets a new directory and retains failures/logs/rejected results.
6. Run appropriate component/semantic tests then fresh original-video production inference for accepted behavior. Cached replay cannot include cadence feedback. Compare against both original and fresh v1 in separate comparison outputs.
7. Use new run’s own observations/caches and an interval-exact semantic trace to package everyGT and FP. Verify all frames/source/proxy alignment, current event folding, sevenfields, ordering, positivity, no duplicates, actual providers/weights/fallback status.
8. Report TP/FP/FN/precision/recall/F1; separate start/end MAE/RMSE/median/bias/P90/max; duration/errors/distributions; IoU distributions/thresholds; both tolerance denominators; misses/extras; fragmentation/partialcoverage/no-overlapFP/merge-splittopology; per-stage/runtime/resources; all common/new/worsenedrows. Preserve earlier recovered controls. No opaque aggregate hides a regression.
9. Validate repeated new GPU inference and reviewed match-disjoint footage before default promotion. Keep any separately authorized held-out evaluation separate from the one-video Test 1 benchmark. If reviewed semantic/pixel/contact labels or runtime access are absent, finish independent work and state the exact limit; never fabricate labels or success.

Re-evaluate current v1 into a NEW directory (not inference):

```bash
python scripts/benchmarking/evaluate_rallies.py \
  --ground-truth Part2/dataset/Test1_Full/Test1_Full_rally.csv \
  --predictions artifacts/benchmarking/experiments/fresh_image_exit_v1/predicted_rallies.csv \
  --fps 30 --output artifacts/benchmarking/experiments/NEXT_v1_evaluation_check
```

Fresh full-production control:

```bash
python research/run_pipeline_experiment.py \
  --output artifacts/benchmarking/experiments/NEXT_fresh_control \
  --rally-implementation rally-evidence-v2 \
  --rally-params '{"use_reconstruction":false,"motion_guard":false,"use_exit_recovery":true}'
```

Set flags explicitly: wrapper defaults to legacy rally-fsm-v1. For detector/contact experiments extend only explicit supported config/override paths in a new run; existingCLI exposes rally implementation/params and shuttle step.

Semantic reproduction of current v1 (not neural inference):

```bash
python research/replay_rally_evidence.py \
  --baseline artifacts/benchmarking/experiments/fresh_image_exit_v1 \
  --output artifacts/benchmarking/experiments/NEXT_v1_semantic_check \
  --rally-implementation rally-evidence-v2 \
  --rally-params '{"use_reconstruction":false,"motion_guard":false,"use_exit_recovery":true}'
```

For unchanged code, assert `baseline_interval_parity:true`, all 39 `(start,end,end_reason)` and 447 livecontacttimestamps equal. For changed candidate use `--candidate`, expect possible parityfalse, and label replay conditional on cached perception. Fold supersedes/retractions before counting events; append-only versions are not distinct physical hits.

Historical baseline semantic reproduction needs the original `301baf08` source in an isolated checkout/worktree or the retained source-pinned replay evidence. The current implementation still has the name `rally-fsm-v1`, but its behavior/contract was corrected and versioned. Running today's default class against old caches does not reproduce the original 49 intervals. A failed parity assertion in that configuration must not be hidden or treated as evidence corruption.

New diagnostic packages AFTER new fresh inference and its matching semantic trace:

```bash
python research/build_failure_cases.py \
  --run artifacts/benchmarking/experiments/NEXT_fresh_run \
  --output artifacts/benchmarking/experiments/NEXT_fresh_run/failure_cases \
  --trace artifacts/benchmarking/experiments/NEXT_fresh_semantic_check/fsm_trace.jsonl \
  --overlays
```

## Tests to preserve/extend

Historical full suite at `3653b0d`:

```bash
pytest -q engine/tests sports/badminton/tests agents/tests apps/api/tests tests/benchmarking
```

Actual 1895 passed,19 deprecation warnings,no skips,283.02 s. Log:`artifacts/benchmarking/experiments/full_regression_final.log`. Baseline 1725 and intermediate 1846 passes are separate checkpoints; overlapping subsets must not be summed. Documentation handoff rechecked existing evaluator metrics but did not rerun expensive inference or software suite.

Focused:

```bash
pytest -q \
  sports/badminton/tests/test_rally_temporal_correctness.py \
  sports/badminton/tests/test_rally_evidence_v2.py \
  sports/badminton/tests/test_rally_motion_evidence.py \
  sports/badminton/tests/test_rally_image_exit_evidence.py \
  sports/badminton/tests/test_rally_port_independence.py \
  sports/badminton/tests/test_injected_model_root.py \
  tests/benchmarking
```

Additional important files in `sports/badminton/tests/`: `test_tracknet_background_retention.py`, `test_tracknet_cache_lifecycle.py`, `test_shuttle_scene_boundaries.py`, `test_shuttle_post_segmentation.py`, `test_perception_verified_shuttle.py`, `test_scene.py`, `test_streaming_contact_integrity.py`, `test_contact_scene_boundaries.py`, `test_contact_pose_sampling.py`, `test_contact_event_evidence.py`, `test_singles_contact_fusion.py`, `test_doubles_contact_fusion.py`, `test_racket_evidence.py`, `test_player_roi_continuity.py`, `test_four_player_retention.py`, `test_player_identity_provenance.py`, `test_pose_schedule_provenance.py`, `test_participant_activity_integration.py`, `test_activity_false_evidence.py`, `test_invalid_court_projection.py`, `test_locked_court_visibility.py`, `test_engine_format_boundary.py`, `test_semantic_transaction_state.py`, `test_stateful_perception_cache.py`.

Generic `engine/tests/`: `test_component_registry.py`, `test_component_declarations.py`, `test_independent_pipeline_plugin.py`, `test_pipeline_component_lifecycle.py`, `test_event_transactions.py`, `test_timeline.py`, `test_media.py`, `test_media_stream_selection.py`, `test_ffmpeg_probe_isolation.py`, `test_shared_media_preparation.py`.

Required controls:temporary loss and multiple misses; stationary players with a moving shuttle; moving players during breaks; static lines/spare shuttles; fast flight; weak launch/apex; real/false contacts near a boundary; pose/detector dropouts and carried rows; view/context changes; short legitimate rallies; long intermittent loss; closely spaced separate rallies; fragment recovery; EOF; provider reset/rollback/cache lifecycle. Synthetic tests establish software contracts, not real sporting labels/doubles quality.

## Required next-session outputs

- Status for every H01–H28:verified fixed, reproduced/open, rejected hypothesis or blocked by exact missing evidence/access. Do not call uncertainty fixed.
- New source-bound diagnostics and all 36 rows/FP comparisons against original/v1/each candidate.
- New experiment matrix and per-run source/config/checkpoint/runtime/input hashes, predictions/comparisons/metrics/logs/resources; preserve severe and new regressions.
- Focused tests, appropriate integration suite, actual fresh full video and reproducibility checks for accepted behavior; truthful skipped/unavailable reporting.
- Updated modular plan and held-out/promotion decision. Add dated/new reports rather than rewrite history.
- Finaldiff/status review and scoped Benchmarking commits only. No main edit, deployed default, secrets or large media/weights/raw artifacts inGit.

Begin with report/source/result identity and residual trace inspection, then propose and execute the next discriminating experiment. Do not stop at threshold proposals or optimize CSV agreement through GT-conditioned merges.

## Identity and tolerance appendix

- Original videoSHA256: `877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6`.
- GroundtruthSHA256: `30651cf7238924d6a5072b1dd71d34ca5839cd5b842f696e745229033ae4f887`.
- Fresh predictionSHA256: `1e227c47b112ce385599f95c3e31e5379dface463aadbc3388346d1c4fd29bc6`.
- ProxySHA256: `d352d684fb5399d804b8f50c785a3605346e7f03987ecb1d9a73ef3482535a97`.
- `models/cache/tracknetv3/TrackNet_best.pt`: `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a`.
- `models/cache/rfdetr_small/rfdetr_s_v142_512x512.onnx`: `fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e`.
- `models/cache/rtmpose_m_body7/rtmpose-m_simcc-body7_pt-body7_420e-256x192-e48f03d0_20230504.zip`: `f7fbb6c5c11a1bb70f3d445e4ddec5d144ea89ad5649c081ef976f9b24a0b741`.

FreshIoU thresholds (35 matches):>.5=100%;>.75=68.5714%;>.9=45.7143%;>.95=20%. Full IoU/duration distributions in comparison.json.

| Tolerance | Seconds | Start matched / all GT | End matched / all GT |
| --- | --- | --- | --- |
|±1 frames|0.033333|0/35 (0.00%) / 0/36 (0.00%)|4/35 (11.43%) / 4/36 (11.11%)|
|±3 frames|0.100000|3/35 (8.57%) / 3/36 (8.33%)|9/35 (25.71%) / 9/36 (25.00%)|
|±5 frames|0.166667|9/35 (25.71%) / 9/36 (25.00%)|17/35 (48.57%) / 17/36 (47.22%)|
|±10 frames|0.333333|14/35 (40.00%) / 14/36 (38.89%)|22/35 (62.86%) / 22/36 (61.11%)|
|±15 frames|0.500000|15/35 (42.86%) / 15/36 (41.67%)|24/35 (68.57%) / 24/36 (66.67%)|
|±30 frames|1.000000|20/35 (57.14%) / 20/36 (55.56%)|32/35 (91.43%) / 32/36 (88.89%)|

Fresh 741 samples/nominal 2 s cadence; RSS peak 2,945,028,096 bytes; CPU mean 442.939% across cores; sampled current-PID GPU peak 2890 MiB; Torch allocated peak 1,133,421,056 bytes excludes ORT/FFmpeg. CPU regression co-run confounds latency comparison; never sum overlapping stage aggregates or invent baseline peaks.
