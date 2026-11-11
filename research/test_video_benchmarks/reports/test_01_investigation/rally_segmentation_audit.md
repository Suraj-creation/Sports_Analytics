# Rally segmentation and temporal reasoning audit

Auditor F. Investigation only: production source, original video, ground truth and frozen baseline outputs were not modified. Production reference is `301baf08be5e989dd0ed93cb885733c3cf6f356a`; the retained benchmark commit is `b773e20`.

## Evidence and reproduction

Read the complete `events/rally_fsm.py`, `BadmintonMatchEngine._window`, `_advance`, `_handle_fsm`, `_finalize_pending`, `_finalize_rally_once`, `_outcome`, the rally component contract/provider, existing rally evidence/independent-port tests, frozen comparison/diagnostic/inference files, and the complete raw event ledger.

Run the auditor's controlled software probes with:

```bash
source ../gpu-env.sh
python research/audit_f_fsm_probes.py
```

Output: `artifacts/benchmarking/investigation/audit_f/fsm_probe_results.json`. The command completed successfully with ten actual-production-FSM probes and 36 ground-truth ledger analyses. It records source and evidence hashes. These are controlled synthetic software cases and read-only ledger analyses, **not** new full-video inference, model accuracy measurements or independent annotations. The orchestrator owns exact cached-perception engine replay; any attribution requiring its processed per-frame inputs remains conditional here.

An exact orchestrator semantic replay subsequently became available at `artifacts/benchmarking/investigation/baseline_semantic_replay/fsm_trace.jsonl`. Independent comparison confirmed all49 `(start,end,end_reason)` triples match the frozen49 intervals, including26 gap/23 stationary endings. Selected actual transitions and a zero-mismatch result are retained in `artifacts/benchmarking/investigation/audit_f/replay_transition_extracts.json`. This establishes actual FSM gate causality; it does not establish visual correctness of its input observations.

Specific real transition evidence: GT2 enters ENDING at1033 after ten unobserved frames, closes at1038 with end1023, finalizes at1046 and restarts1066 (confirmed1068). GT19 repeats that chain at8276/8281/8289 with end8266, then restarts8308 (confirmed8310). GT20 enters ENDING at9535/end9525, closes9540 and finalizes9548; its region9526–9547 contains19 interpolated samples and only3 independently observed samples. The pipeline therefore reconstructs part of this path yet still terminates continuity because interpolation is not observation. That is a proven real gate interaction, not a claim that every interpolated point is physically correct. GT27 enters stationary ENDING at12753/end12748, closes12763 and opens a distinct interval at accepted contact12771 because23>22. The new contact's same-frame step immediately re-enters ENDING from retained stationary history; speed376 at12772 then resumes it. GT5's detected onset2210 survives several candidate-end cancellations, but a ten-frame gap triggers at2264/end2254, closes2269 and cancels at2277 because length45<60; new exported onset2309 is confirmed2311.

## What the current segmenter actually observes

`sports/badminton/src/bai_badminton/engine.py:_window` (approximately lines 1344–1385) transforms retained observations into a postprocessed shuttle track. `_advance` lines 1463–1473 computes `observed = t.vis & ~t.interp`, and instantaneous speed only when two adjacent frames are independently observed. The first observed sample after a missing frame has NaN speed. Camera/coordinate/replay discontinuities also have NaN speed.

The FSM is called once per final frame, in this order: context discontinuity, accepted contact, shuttle observation. Its `step(frame, visible, speed, replay)` receives **no player-motion, pose-motion, activity-estimate, court-quality or confidence value**. Player/court/pose evidence can affect accepted contacts and upstream observation eligibility, but cannot directly cause the stationary rule. Player inactivity and stationary shuttle evidence are different hypotheses.

Gap filling may interpolate up to 25 missing frames with plausible anchors. Those positions remain marked `interp`, so the FSM still counts them as unobserved. This preserves provenance and prevents an interpolated point becoming a verified contact or start, but means trajectory reconstruction does not currently help rally continuation.

## Complete interval-producing path

| Entry/state | Condition | Consequence |
| --- | --- | --- |
| IDLE / `step` | Three consecutive independently observed moving speed samples >3 px/frame | Open at the first speed sample in the run. Because speed requires a prior observed frame, this normally needs four consecutive observed positions. |
| IDLE / `on_contact` | Upstream accepted contact | Open at the contact frame. Contact remains inferred evidence; a finalized contact ledger status is not visual proof. |
| IN_PLAY / `step` | Ten consecutive unobserved frames | Candidate end at `current_frame-10`, clamped no earlier than start/last accepted contact. Missingness itself supplies this candidate. |
| IN_PLAY / `step` | Seven observed speeds <3 among the last ten frames | Candidate end at `current_frame-9`, with the same clamp. It is shuttle stationarity, not player stationarity. |
| ENDING / `step` | An observed speed >6 | Cancel candidate end and return to play. |
| ENDING / `on_contact` | Accepted contact | Cancel candidate end. The same frame is then stepped and can re-enter ENDING if retained stationary history still qualifies. |
| ENDING / `step` | Current frame minus the backdated candidate end reaches 15 | Close interval. This is not 15 new frames after the end-condition trigger: an invisible-gap trigger ordinarily gets only five additional frames. |
| CLOSED / `step` | Three moving speed samples and current confirmation frame is within the 22-frame merge window | Reopen old interval. |
| CLOSED / `on_contact` | Accepted contact is within the merge window | Reopen old interval without waiting for a three-sample motion run. |
| CLOSED / either call | Current/contact frame exceeds merge window | Finalize old interval; a motion run/contact can open a new one. |
| Discontinuity/replay | View/shot/coordinate context changes | Finalize preceding evidence as a cut or cancel a zero-length/short candidate, clear histories and prevent cross-context merges. |
| EOF / `flush` | Open or candidate interval remains | Close/finalize; it does not establish a sporting outcome. |
| `_finalize` | Inclusive segment length <round(2*FPS) | Cancel provisional start instead of exporting an interval. |
| Engine pending/final outcome | Final FSM segment becomes ready after optional OCR wait | Publish `rally_end` with the same start/end; official-point acceptance does not filter this benchmark. |

Normal `_finalize` preserves recent motion/missingness history; discontinuity explicitly clears it. `_handle_fsm` handles old cancellation/finalization before assigning a new provisional start, preventing a known reference-ordering problem. `_finalize_pending` can delay publication but does not merge segments or repair their boundaries. Output serialization recomputes endpoint-span duration and cannot explain multi-second fragmentation.

## Ranked findings

### F-R01 — Severe matched boundary outliers partly measure fragmentation, not initial detection latency

- **Symptom:** GT2/19 have matched starts +179/+202 frames; GT20/27 matched ends −442/−218.
- **Evidence:** Immutable raw ledger and `inference.json` contain earlier/later fragments. GT2 begins at891 (+4) but its matched second fragment begins1066. GT19 begins8110 (+4) but its matched second fragment begins8308. GT20 has last fragment9685–9947 (last end −20), while the assigned fragment8715–9525 ends −442. GT27 has final fragment12771–12954 (last end −12), while assigned12455–12748 ends −218.
- **Source:** `rally_fsm.py:step/_finalize`; `engine.py:_handle_fsm`; unchanged evaluator one-to-one assignment.
- **Diagnosis/confidence:** Proven segmentation/assignment decomposition. The matching policy is behaving as specified; these fragments must not be silently stitched in the evaluator.
- **Alternatives:** Some genuine onset delay remains, and fragments could include false shuttle tracks. Earliest/latest overlap is a diagnostic envelope, not a corrected prediction or accepted union.
- **Causal experiment:** Replay exact processed observations with transition capture. Determine which missing/stationary decisions split each interval; test one continuation rule at a time and retain legitimate between-rally breaks as controls.
- **Corrective action:** Improve evidence-supported continuity inside the sport segmenter/provider. Keep matcher and CSV untouched.
- **Expected metric effect:** If independently justified continuity is recovered, FP/FN, matched-boundary outliers, duration bias and fragmentation can improve together; the degree is unmeasured here.
- **Regression risk:** Merging separate exchanges can inflate IoU while harming count, score/outcome evidence and legitimate short breaks.

### F-R02 — Provisional-start cancellation is another source of delayed exported starts

- **Symptom/evidence:** The raw ledger has 83 provisional rally starts, 34 retracted starts and 49 finalized rallies. GT5 has a provisional start exactly2210, equal to its label, but exports only2309–2423. Cancelled starts inside other difficult labels include GT1:264; GT25:11570/11613; GT28:13115/13151; GT31:14430. GT1's final start is339.
- **Source:** `rally_fsm.py:_finalize` lines237–245; `engine.py:_handle_fsm` lines1525–1530. Cancellation retracts contacts/strokes belonging to the failed short interval as well.
- **Diagnosis/confidence:** Proven event lifecycle contribution to lost onset evidence. It is incorrect to treat every delayed CSV start as the model never noticing the first motion/contact.
- **Alternatives:** Short provisional exchanges can be genuine noise/floor pickups; GT onset itself may precede visible shuttle evidence. Their cancellation is not automatically a detector defect.
- **Causal experiment:** Capture the end condition and duration for each cancelled candidate. Check trajectory/contact/player/court evidence across reacquisition before any reconstruction. Include cancelled between-rally noise controls.
- **Corrective action:** Retain cancelled-candidate provenance for explicit continuation decisions rather than blindly lowering the minimum duration or emitting every short candidate.
- **Expected effect:** Potentially reduce start bias and misses while preserving short-noise rejection.
- **Regression risk:** False contacts and player movement during breaks can become exported false rallies if cancellation is weakened indiscriminately.

### F-R03 — Merge-window confirmation bias is a proven software edge case

- **Symptom:** A motion run that begins inside the declared merge window can fail to merge because its confirmation is outside the window.
- **Evidence:** Actual-FSM probes: an 18-frame observation loss produces one interval; a 19-frame loss produces `(1,99)` and `(120,219)`. The latter run begins at120, so `120−99=21 <=22`, but confirmation at122 fails `122−99<=22`. A synthetic accepted contact at119 recovers one interval using the same missing samples. Source condition is `frame - self.closed.end`, not `_run_start - self.closed.end`, at `rally_fsm.py:156`.
- **Diagnosis/confidence:** Proven gap-definition/confirmation-latency inconsistency relative to a boundary-gap interpretation. Baseline impact is **not yet quantified**. It cannot explain GT2/19's 43/42-frame inter-fragment gaps by itself.
- **Related real evidence:** GT27 ends at accepted contact12748, and its next interval starts at accepted contact12771: a23-frame gap versus `round(.75*30)=22`. That case is a direct merge-threshold exclusion, not proof of the two-frame motion confirmation bug; contacts bypass the motion-run confirmation.
- **Alternatives:** The intended policy might deliberately define the window using decision time. In that case the contract/documentation should explicitly state its shorter effective motion-recovery period.
- **Causal experiment:** A/B only candidate-start-versus-confirmation-time accounting, with unchanged numeric thresholds. Include repeated false motion and closely spaced real breaks. Count affected real transitions from exact replay before adoption.
- **Corrective action:** Explicitly define gap semantics. If using candidate onset, preserve a bounded candidate while awaiting confirmation; do not extend the window indefinitely.
- **Expected effect:** Recover only near-window motion continuations; not a complete solution for longer dropouts or false stationarity.
- **Regression risk:** Extra two-frame bridges can still combine separate legitimate exchanges; retain independent evidence gates and exact regression cases.

### F-R04 — Observation loss is currently sufficient to terminate an exchange

- **Symptom:** Accepted gap reconstruction can coexist with exported fragmentation.
- **Evidence/source:** `shuttle_post.py:fill_gaps` uses bounded anchors and marks interpolation; `engine.py:1464` removes all interpolated samples from the observed mask; `rally_fsm.py:144–145` converts ten such samples into an end candidate. The 25-frame-loss actual-FSM probe splits even when positions could be reconstructed. Baseline final reasons are26 gap and23 stationary; all six unmatched labels have partial predicted coverage.
- **Diagnosis/confidence:** Proven architecture/policy behavior; attribution of each real gap to occlusion, low confidence, outlier removal, invalid court context or genuine absence requires processed-input replay and frame inspection. No causal visual claim is made here.
- **Alternatives:** Preserving unknowns rather than treating reconstructed positions as real observations is correct. Some missing runs are actual rally endings and must remain endings.
- **Causal experiment:** Distinguish independently observed motion, observed rest, temporarily unobserved, invalid context and corroborated termination. Test a continuation-only bridge gated by compatible observed anchors/context/contact support. Do not allow interpolation to start a rally, establish contact or prove a landing.
- **Corrective action:** A typed, inspectable continuation-evidence adapter/provider with explicit unknown handling; preserve the legacy provider as an ablation baseline.
- **Expected effect:** Potential reduction in fragmentation and large end errors with controlled recall/precision trade-offs.
- **Regression risk:** False interpolated trajectories, spectator motion and separate rallies can become false continuity if evidence provenance is collapsed.

### F-R05 — Stationarity has finite-confidence and backdating limitations; player inactivity is not its input

- **Symptom:**23 baseline intervals end by stationarity. Seven low-speed observed positions in ten frames can defeat other motion in that same window.
- **Evidence:** `_stationary` counts observed shuttle speeds below3 and has no confidence, landing, player recovery or contact-distance test. The controlled seven-low-speed probe ends at67 although the previous moving samples included67–69; the end is dated to the **beginning of the ten-frame window**, not the first slow sample70. This produces up to several frames of deterministic early bias before any larger fragmentation effect. NaN speeds do not count as zero, which is correct.
- **Source:** `rally_fsm.py:146–147,206–211`; `engine.py:1463–1518`.
- **Diagnosis/confidence:** Proven mechanics. Whether the real stationary positions are the shuttle resting, a stuck heatmap/background false positive, a slow apex, camera compensation artifacts or a valid ending remains a perception/frame-review question.
- **Alternative hypothesis rejected for direct causality:** Stationary **players** cannot directly trigger this rule because their motion is not passed to `step`. Player evidence can indirectly change contacts/eligibility.
- **Causal experiment:** Inspect raw peaks and stabilized observed positions around the23 stationary endings. Independently test first-slow-sample boundary localization and contradictory observed-flight/contact evidence; keep between-rally stationary-object controls.
- **Corrective action:** Preserve per-sample quality and define a distinct observed-rest candidate; do not call absence or stationary players proof of termination.
- **Expected effect:** Better end localization and fewer false stationary splits if perception confirms the hypothesis.
- **Regression risk:** A slow/landed shuttle must still terminate promptly; extra delay can contaminate score/outcome context and merge separate exchanges.

### F-R06 — Configurable stationary window is implemented with a fixed ten-frame deque

- **Symptom/evidence:** `RallyParams.stationary_window` is configurable through the component factory, but `_recent` is always `deque(maxlen=10)` (line89). `_stationary` requires exact `len(_recent)==stationary_window` (line210). Actual-FSM probes with window15 never trigger; window5 cannot trigger after warmup either. The default10 control does trigger.
- **Diagnosis/confidence:** Proven configuration/replaceability defect, **not a cause of this baseline** because its window is10.
- **Alternatives:** None for the observed contract mismatch. A fixed10-only supported contract would require validation rejecting other values instead of silently accepting them.
- **Causal experiment:** Focused public-provider tests with windows5,10,15, parameter validation and reset/checkpoint round-trip.
- **Corrective action:** Size state from validated parameters in the owning provider, or explicitly reject unsupported configurations. Version/cache identity must reflect behavior.
- **Expected effect:** No promised Test1 improvement; correct future experiments and avoid misleading tuning results.
- **Regression risk:** Changing history allocation/reset must preserve checkpoint/restore and independent rally-port behavior.

## Confidence, lifecycle and architecture limits

The default provisional start event has fixed confidence0.6; the segmenter receives no calibrated per-frame uncertainty. Final `rally_end` confidence is tied to outcome/winner reasoning and is not a calibrated probability that its boundaries are correct. Filtering rallies by it would mix unrelated quality dimensions and can hide real exchanges.

The current rally port exposes `RallyState`, `params`, tentative/closed segment state plus callbacks. A richer observation contract must remain sport-owned, typed and replaceable, with compatibility/adaptation for the independent-port test. Do not add player/shuttle assumptions to the generic host. Retain replay/cut barriers: missing observations in a valid court context and invalid/replay contexts are not interchangeable.

## Acceptance and regression requirements

Before implementation, exact replay must reproduce all49 baseline intervals and83/34 start/cancellation ledger counts or explain a documented source/serialization difference. For a candidate: unchanged matcher/CSV and full-video source mapping; no extra invalid intervals; independently report TP/FP/FN, fragmentation, start/end MAE/RMSE/bias/P90/max, duration and tolerance accuracy. Improvements in one large outlier must not hide worse recall or legitimate-break merges. Replay-only improvements remain exploratory until fresh production inference confirms them. Test1 is development footage; no generalization claim is supported.

Focused software scenarios: temporary missing runs around the true boundary of recovery; moving shuttle with stationary players; NaN/invalid observation quality; accepted contact near tentative/closed boundaries; contacts at merge22/23; fast false detections; singles/doubles without forced identity; camera cuts; short real exchanges versus floor pickups; long intermittent losses; close separate exchanges; bounded continuation without fabricated observed contact/landing evidence. This audit supplies ten controlled probes; it does not claim coverage of unannotated doubles footage or all those future regressions.
