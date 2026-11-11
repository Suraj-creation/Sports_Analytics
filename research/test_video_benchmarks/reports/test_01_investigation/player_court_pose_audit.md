# Player, court and pose audit — Test 1

Audit D inspected the frozen production source at `301baf08be5e989dd0ed93cb885733c3cf6f356a`
and benchmark evidence at `b773e20c62d1c398cddc3d23510bd4adf823325b`.
No production interface, original media, ground-truth annotation, or frozen
benchmark artifact was modified. This is a cached-observation/source audit, not
fresh perception inference or a new player/pose accuracy benchmark.

## Reproducible evidence

```bash
source ../gpu-env.sh
python research/audit_d_player_observations.py \
  --output artifacts/benchmarking/investigation/audit_d/final
```

That directory already exists for this audit; use a new output path for a repeat.
The helper rejects overwriting an existing output. Its `observations.json`
contains all 36 per-rally records, raw-cache hashes and global counts. The
component-test command and interpretation are recorded in
`research/player_tracking_experiments.md`; its log is
`artifacts/benchmarking/investigation/audit_d/component_tests.log`.

## Actual dependency path

1. `BadmintonPerception.process` in `perception/pipeline.py` computes cuts,
   court/camera state, per-frame calibration lifecycle, and main-view exclusion.
2. `PlayerDetector._rfdetr` in `perception/players.py` explicitly handles BGR
   input according to the checkpoint preprocessing contract, validates decoded
   boxes/logits, retains person queries above the configured 0.35 threshold,
   converts normalized boxes to the cropped image, and applies NMS 0.6.
3. `PlayerPerception.process` crops around the current court, restores crop
   offsets, gates feet through court-plus-runoff geometry, updates ByteTrack,
   and records whether each returned track uniquely matches a current detection.
   Already admitted tracks can remain through a uniquely overlapping jump or
   runoff observation. This avoids interpreting an airborne box bottom as a
   reliably grounded foot.
4. `_carry` returns previous boxes on unscheduled detector frames, explicitly
   marks `detector_matched=False`, and never revives them after an excessive
   detection gap. These are carried estimates, not new detections.
5. `_attach` runs RTMPose on the **current image** when that exact frame is
   scheduled. It creates no pose for unscheduled frames. BGR-to-RGB conversion
   is explicit before RTMPose; pose coordinates are in the analysis image.
6. `BadmintonMatchEngine._append` stabilizes boxes and poses through the current
   camera transform, computes court feet when geometry is usable, and records
   geometry validity, participant snapshots and actual pose cadence.
7. `_advance` constructs a frame-aligned `episode_window` through
   `participant_window(..., restrict_target_court=True)`. Contact detection uses
   track episodes and current selected-court provenance even when named player
   identity is unverified. Only afterwards are contacts passed to the rally port.

The recorded runtime identifies RF-DETR Small `1.4.2`, RTMPose M Body7 `1.0`
and `court-player-episodes-v1`. Both model sessions recorded CUDA and CPU
providers with `actual_backend=onnx-cuda`, `backend_fallback=false`. TrackNet's
CUDA FP16 status is separately evidenced by its runtime record. An ONNX profile
field requesting FP16 is not, by itself, proof that every detector/pose graph
tensor is FP16; actual graph/runtime tensor precision needs separate telemetry.

## Measured coverage and synchronization

The 288 perception chunks cover exactly every frame 0..17,267 in order.

| Recorded observation | Count |
| --- | ---: |
| Main-view / excluded-view frames | 16,983 / 285 |
| VALID / REACQUIRING / LOST calibration frames | 16,941 / 42 / 285 |
| Geometry-usable frames under engine eligibility | 16,941 |
| Frames with 2 / 1 / 0 returned people | 16,693 / 164 / 411 |
| Main-view frames with no returned people | 126 |
| Usable-geometry frames with no / one person | 84 / 164 |
| Frames executing the detector | 6,851 |
| Detector-executed frames with 2 / 1 / 0 people | 6,787 / 30 / 34 |
| Returned person rows | 33,550 |
| Uniquely detector-matched / carried-or-tracker-only person rows | 13,603 / 19,947 |
| Negative/unresolved track-ID rows | 0 |
| Actual RTMPose rows | 25,594 |
| Posed rows with at least one wrist score >=0.3 | 25,586 |
| Off-schedule pose rows / detector cadence mismatches | 0 / 0 |
| Observed geometric-racket rows | 10,974 |
| Live estimated contacts | 432 |
| Live contact frames with 2 people / 2 poses | 432 / 377 |

The actual pose-stride histogram is 12,060 frames at stride 1, 4,923 at stride 6,
and 285 at stride 0. Detector cadence agrees with stride 2 for the former and 6
for the latter. Fifty-five live contacts occur without two pose rows on that
exact frame; sparse idle pose scheduling is a possible limitation of contact
evidence, not proof of a missed model execution or a mislabeled contact.

Returned-person confidence quantiles min/p10/median/p90/max are
0.3572/0.8658/0.9054/0.9303/0.9559. Pose-keypoint scores are
0.0505/0.6281/0.7702/0.8708/1.2037; **894 keypoint scores exceed one**.
Those scores are model support values, not calibrated probabilities. The
current threshold use does not establish probability calibration. Any fusion
layer must preserve this distinction rather than silently clipping and claiming
calibration.

The VALID-frame court-quality quantiles are 0.955/0.980/0.988/0.994/1.000.
These measure detected line agreement, not independently labeled geometric
accuracy. The stored automatic calibration used 24/24 samples, twelve landmarks,
line precision 0.9934 and fit RMS about 1.137 analysis pixels. No independent
court-landmark labels are provided, so a small RMS cannot establish true camera
pose, net height, airborne shuttle position or physical contact accuracy.

## Identity degradation: actual effect and limits

`BadmintonPerception.__init__` attempts the optional player-ReID component when
format is unknown/doubles, or when explicitly selected for singles. Acquisition
starts unknown and confirms singles at frame 120. Therefore the initial attempt
to load missing `osnet_ain_x0_25` is expected under this configuration.
`_load_reid` uses `registry.path(..., fetch=False)` and explicitly degrades when
the checkpoint is absent; it does not fabricate embeddings or silently download
weights. `PlayerPerception` then has no learned associator and uses ByteTrack.

All 33,550 cached rows explicitly report `identity_method=bytetrack_v1`. The
eleven raw ID values 0..10 are not eleven physical athletes. There are 37
`identity_ambiguity` events with reason `visual_tracker_reset`; track IDs can be
reused after cuts and format/calibration epochs. Participant episode birth IDs
prevent that reuse from becoming a durable named-person assertion. Raw ID count,
episode churn and reset count cannot be reported as identity-switch accuracy
without participant identity ground truth.

All 432 live contacts are anonymous named actors, while 156 contain a provisional
participant hypothesis. The existing contact path therefore demonstrably runs
without accepted names or OSNet. Restoring OSNet could improve association after
occlusion/cuts, but this audit supplies no controlled restored-weight run and no
identity labels. It is **not established** that missing OSNet caused the severe
Test 1 segmentation errors.

## Activity is supporting evidence, not a termination signal

The baseline contains 9,670 `active_play`, 7,271 `unknown`, 327 `reacquiring`,
and **zero `inactive`** activity frames. Thus there is no recorded inactive
activity decision to blame for these boundaries. The engine's rally call is
`fsm.step(f, observed_shuttle, shuttle_speed, replay)`; player movement is not an
argument. Its stationary rule concerns processed shuttle speed, not a stationary
player. This directly rejects that proposed explanation of baseline termination.

Activity uses several independent body observations plus a moving shuttle
trajectory; missing evidence is not asserted absence. The engine never supplies
the independent `absence_verified=True` required to classify inactivity.
`active_play` does feed doubles team hypotheses and match-phase evidence, but
does not directly keep the rally FSM active.

There are 8,045 active-play frames inside labeled rally intervals and **1,625
outside** them. Outside-GT activity is not necessarily visually false—the labels
cover rally spans, not every exercise or between-rally movement—but it proves
that this existing signal cannot safely serve as an independent rally-continuation
oracle. Conversely, GT24 has zero active-play activity frames yet a correctly
matched interval. Never make a positive activity label mandatory for a rally.

## Failure-specific evidence

| GT | Returned people over inclusive GT span | Camera-lost frames | Geometry-valid frames | Live contacts |
| --- | --- | ---: | ---: | ---: |
| 2 | 376 frames with 2 | 0 | 376 / 376 | 17 |
| 5 | 291 frames with 2 | 0 | 291 / 291 | 7 |
| 19 | 521 frames with 2, 2 with 0 | 0 | 523 / 523 | 22 |
| 20 | 1,256 with 2, 12 with 1, 17 with 0 | 14 | 1,269 / 1,285 | 46 |
| 23 | 338 with 2, 8 with 1 | 0 | 346 / 346 | 17 |
| 25 | 286 with 2, 12 with 1 | 0 | 298 / 298 | 9 |
| 27 | 510 with 2, 6 with 1 | 0 | 516 / 516 | 23 |
| 28 | 381 with 2, 8 with 0 | 0 | 387 / 389 | 6 |
| 29 | 304 with 2, 12 with 1 | 0 | 316 / 316 | 9 |
| 31 | 704 with 2, 12 with 1, 32 with 0 | 21 | 725 / 748 | 21 |

Camera loss is therefore a localized risk, particularly GT31; it cannot explain
all six policy misses. Complete two-player and valid-geometry coverage in GT2,
GT5 and GT27 also rules out a universal missing-player/calibration explanation.
GT20's brief lost-view region begins near frame 8697; its large matched ending
error occurs much later at frame 9525. It would be incorrect to equate those
timestamps and assert direct causation.

The cache has 38 shot IDs, but a shot-ID transition is an algorithmic cut/reset
decision, not independent evidence of a real camera cut. The broad `replay`
flag means analysis-excluded view in this path; it is not a manually verified
broadcast-replay label. Preserve those semantics in diagnostics and fusion.

## Ranked findings and causal experiments

| Finding | Evidence and cause status | Alternative / uncertainty | Experiment and smallest action | Expected effect / regression risk |
| --- | --- | --- | --- | --- |
| Stationary-player termination is not a baseline cause | Proven data flow: only shuttle speed enters FSM; zero inactive activity frames | Indirect phase/team interpretation exists | Keep movement a separately inspectable supporting cue; do not wire inactivity to end decisions | Avoids a false diagnosis; movement-only continuation would bridge breaks |
| ReID missing does not disable detector, pose or anonymous contacts | Proven loaded models, explicit ByteTrack rows and 432 contacts | Association after occlusion may still worsen | Separate restored-OSNet ablation using same images/model hashes plus reviewed track episodes; do not adopt by assumption | Possible contact-context continuity; embedding latency and wrong associations can regress doubles |
| Actual sparse pose/box evidence can limit contact support | Proven cadence and carried flags; no schedule mismatch | No contact ground truth establishes which absent pose caused a miss | Event-triggered short-window fresh poses around uncertain starts; compare contact timing and rally metrics independently | Could reduce onset delay; extra compute and false contact starts are risks |
| Camera loss is local, not universal | Exact per-GT coverage above | Geometry-quality scores can remain high for a wrong fit | Inspect lost/reacquiring boundaries on original frames and retain explicit validity; never infer a floor mapping from an invalid view | May reduce canceled/reacquired exchanges; relaxing invalid-view gates risks cross-camera tracks |
| Activity cannot be a standalone rally oracle | 1,625 active-play frames outside GT, zero active GT24 | Outside-GT visual activity is unlabeled | Test bounded, frame-aligned movement only as a veto on a dubious stationary-shuttle end, with no start/merge authority | Could help GT27; retrieval/walking during breaks remains a major false-positive risk |
| Scores are uncalibrated | 894 pose scores >1, support-only source semantics | A probability calibration dataset is absent | Preserve raw support; add calibration only with reviewed labels and held-out validation | Prevents misleading confidence fusion; arbitrary clipping destroys useful raw evidence |

## Safe evidence reuse for a future temporal component

Do not read `self.activity`'s current state while advancing an older frame: the
engine has already appended future context and its temporal frontier trails by
40 frames. That creates a synchronization error in a naïve fusion implementation.
Instead, `_advance` already has aligned `ParticipantSnapshot` frames and an
`episode_window`. The snapshots retain detector-observed/matched status, stable
track ID, birth observation ID, current pose and court coordinates. Use those
at the decision frame and within `window.segment_bounds(i)`.

For a conservative movement-support experiment, require the same episode/track
and coordinate segment, finite selected-court geometry, two credible visible
participants, and fresh matched boxes or actual scheduled confident poses at
both comparison endpoints. Compare stabilized torso/wrist/body movement using
time-based windows; carried boxes alone are not fresh observed movement. Missing
pose/court evidence must produce unknown, not stationary. Such support may veto
a doubtful end for a bounded period; it must not independently create a start,
bridge arbitrary shuttle absence, identify a winner, or infer a named player.

## Singles/doubles and remaining limitations

Test 1 provides no four-player frames or independently annotated player/pose
labels. Actual detection, pose and identity accuracy for doubles remains
unmeasured. Existing controlled four-player, target-court, identity-epoch and
pose-schedule tests pass, which checks contracts rather than real doubles quality.
Preserve all four participants, explicit capacity-withheld states, and uncertain
format behavior. A missing or low-quality participant should not silently force
singles. Player evidence must remain replaceable through the current perception
and domain ports; no host-level badminton geometry is justified by this audit.

Raw rejected detector boxes and rejection reasons are not retained in the caches,
so this audit cannot count pre-ROI false negatives, assess rejected spectators,
or separate failed detector queries from every later admission gate. Add compact
stage/rejection counters and source-bound diagnostic observations before trying
to tune admission thresholds. No threshold or model was changed in this audit.
