# Court-origin participant continuity: closed-data investigation

**Decision: no production motion-gate patch is justified yet.** c585 remains an unaccepted control for the next video. A one-second court lease loses real visible athletes; simply extending it restores the official handover. The installed ByteTrack covariance cannot safely replace that lease. An untuned scale-aware model helps, but still exposes genuine coverage losses and a covariance-growth handover failure. No production code, profile, annotation, checkpoint, baseline or historical matrix was changed; no neural inference or Test3 access occurred.

## Evidence and scope

The immutable completed Test1 review supplies all **182 gross withheld participant rows**, including the 125 not visible in the narrower57 scored-reference pairs. Historical selected fresh observations are replayed through installed motion filters; their private production Kalman states were not serialized and are **not claimed recovered**. Those conditional histories retain original measurements even where the proposed gate would reject them. A separate chronological hypothesis shadow applies its own decisions. The all182 timeline uses historical selected observations and lacks unreturned competing detector candidates, so it measures conditional potential coverage, not full-pipeline recall.

All ten existing Test1/Test2 source-bound prefix windows also have full retained RFDETR candidate sets. These raw-candidate shadows start from empty state at each bounded window, use the original recorded source geometry/detector schedule, and reset at the recorded c585 foreground barrier/hard-cut boundaries. They do not independently evaluate scene detection, neural inference, pose, engine feedback, roster identity, contacts, scoring or physical accuracy. This is diagnostic evidence, not a new benchmark arm. Existing generated annotations remain agreement references rather than human tracking ground truth.

- [All182 preserved original rows](../../regression_tests/pre_test03_scene_v1/test01_independent_v2/gross_coverage_all_182_rows.json)
- [ByteTrack conditional and ten-window summary](summary.json), [all182 conditional rows](all_182_conditional_rows.json)
- [Untuned scale-aware alternative](scale_aware_v1/summary.json)
- [Full4D contradiction-stop shadow](hypothesis_v2/summary.json)
- [Exploratory width-ablation shadow](hypothesis_partition_v3/summary.json)
- Each summary links/hashes its inputs. Raw per-observation states, residuals and candidate decisions are separate JSON files, never hidden in Markdown.

## Installed backend and integration defect boundary

Installed `trackers2.6.1` ByteTrack uses an8D **XYXY + four corner velocities** constant-velocity filter. Initial covariance is identity; ByteTrack sets measurement noise `.1I` and one-frame process noise `.01I`. The actual association is IoU/Hungarian; package source contains no chi-square table or Mahalanobis admission gate. Motion projection is `H x`, innovation covariance `H P Hᵀ + R`, and squared residual distance `rᵀ S⁻¹r`.

`PlayerTracker.update` passes `frame_idx/fps`. The backend converts elapsed seconds to elapsed source-frame steps, uses a nominal one-frame bootstrap and elapsed-seconds lost-track pruning; its process-noise implementation scales gaps using white-noise acceleration. A diagnostic caller must predict a detached state once per actual detector observation using elapsed source frames, not call count or a fresh nominal timestep for every detector stride. Carried frames must not update the filter, teach appearance or renew observation authority. Duplicate/backward timestamps and resets require explicit handling.

The actual current architecture filters raw detections in `PlayerPerception._roi_admission` **before** `PlayerTracker.update`. Therefore a gate cannot read an already-updated filter after ROI rejection and call that an independent prediction. The implementation must expose a non-mutating prior proposal at the tracking boundary, or own a separately versioned origin-hypothesis state. It must never predict/mutate the shared backend twice. Court-origin time, last positive image observation and current spatial estimate need separate fields.

The installed library also contains `BoTSORTTracklet` with XCYCWH state and scale-aware default sigmas `.05` position, `.00625` velocity and `.05` measurement. That existing model was measured unchanged, including its update-time measurement-noise refresh. No BoT-SORT appearance extractor, camera-motion compensation or full BoT-SORT association engine was executed. Model/source fingerprints are in the receipts. The Roboflow implementation is Apache2; the original BoT-SORT repository and Torchreid code use MIT. No external model weights or datasets were adopted.

Primary-source context: [Roboflow ByteTrack source](https://github.com/roboflow/trackers/blob/develop/src/trackers/core/bytetrack/tracker.py), [motion timing/noise implementation](https://github.com/roboflow/trackers/blob/develop/src/trackers/utils/motion_models.py), [scale-aware tracklet](https://github.com/roboflow/trackers/blob/develop/src/trackers/core/botsort/tracklet.py), [BoT-SORT paper](https://arxiv.org/abs/2206.14651). Online branches are mutable; the experiment uses separately hashed installed source, not a claim that today’s branch matches every installed byte.

## Fixed-gate differential

The first gate uses the standard4D95% chi-square quantile9.4877, independently documented in [DeepSORT’s original Kalman source](https://github.com/nwojke/deep_sort/blob/master/deep_sort/kalman_filter.py). DeepSORT uses a different, scale-aware XYAH model. Its table does **not** calibrate ByteTrack’s pixel covariance or turn these outputs into probabilities. No gate threshold was fitted to a video.

|Conditional observations|ByteTrack XYXY|Installed scale-aware XCYCWH|
|---|---:|---:|
|Test1 comparable fresh pairs|14004|14004|
|Pass standard4D gate|1528|12328|
|Reject standard4D gate|12476|1676|
|Fresh comparable pairs within182 withheld rows|72|72|
|Pass within that72|15|67|
|Reject within that72|57|5|

The other110 withheld rows are carried or lack a comparable prior; they are explicitly retained in the raw report, not counted as successful fresh observations. The simple ByteTrack gate rejects most legitimate selected motion and box-shape variation, so it is unsuitable as a repair with its existing covariance.

### Real handover: Test2 5956→5958→6492

Exact source/crop-bound raw boxes change from a far athlete of height121.112px at5956 to a seated official of height52.807px at5958 near the same location. Both on-court athletes are present in the6492 raw candidates.

The naive scale-aware shadow accepts5956 athlete (d²2.545) and initially rejects5958 official (49.751). However, keeping the unobserved hypothesis lets covariance widen: it admits the official at5964 (5.518), later renews it repeatedly, and thereby recreates the handover. Initial rejection is not sufficient. See [critical frame snapshots](scale_aware_v1/critical_official_handover.json) and the complete [5505–6510 trace](scale_aware_v1/test2_05505_06510_shadow.json).

A contradiction-stop shadow removes the origin hypothesis after a mutually unique overlapping **fresh but incompatible** observation; outside candidates cannot reseed it, and missing/ambiguous detections only retain an unrenewed estimate within the existing one-second missing budget. This closes the observed delayed-official-reacquisition path, but also rejects genuine athletes. The model is not a physical identity oracle.

## Coverage costs remain visible

|Original gross withheld group|Rows|Full4D contradiction-stop exact regions retained|Exploratory center+height partition exact regions retained|
|---|---:|---:|---:|
|753–800|48|48|48|
|3413–3449|37|5|37|
|6365–6381|17|0|0|
|7801–7805|5|0|5|
|7812–7856|45|0|45|
|8087–8105|19|19|19|
|14103–14113|11|0|11|
|Total|182|72|165|

These are conditional shadow-region counts, not new physical recall or production predictions. All original182 rows and seven groups remain present. The prior240 added rows/net58 population change does not cancel these losses.

### Width articulation and limits of the exploratory partition

Every one of the five scale-aware fresh-pair failures within the72-row conditional subset is dominated by changing bbox **width**, while center and height remain consistent: frames3418,3420,6380,14104,14112. For example3418 totald²25.538 contains24.599 width contribution;14112 total22.019 contains19.149 width. This is a concrete non-rigid-box model mismatch, not evidence that the person disappeared.

After inspecting that failure, a separately preserved exploratory arm tests standard center2D95%5.9915 and height1D95%3.8415, keeping width as a diagnostic rather than an identity veto. It retains165/182 historical regions, accepts the actual5956 athlete, rejects5958 official on both center and height, and never accepts that known seated-official candidate through6492; both6492 athletes remain current. This is explicitly **post-observation model exploration**, not held-out validation. Partitioned gates do not jointly imply calibrated95% coverage.

It still rejects the real white athlete outside the right sideline: at6338, center innovationd²10.489 violates5.9915 despite heightd².203. The court anchor is6334, and all17 later6365–6381 regions are then lost. Fast acceleration, articulated boxes, cropping, perspective and camera motion remain model limitations. Loosening a threshold until these videos pass would conceal those assumptions; no further such threshold search was performed.

Raw ten-window results are independently enumerated under each arm’s summary. In particular the raw-proposal and selected-history shadows have different state/population histories; their hypothesis numbers are local IDs, never physical identity labels. A current positive box, an unobserved estimate and a court-supported participant must remain distinct.

## Minimum reusable implementation proposal, pending stronger evidence

1. Introduce an explicit replaceable **court-origin anonymous hypothesis** policy at the player tracking/admission boundary. Seed only a uniquely supported actual court observation; keep `last_actual_court_frame`, `last_positive_image_frame`, motion prior and image-origin evidence separate. Missing/carry frames cannot renew any of them. Cut, calibration basis, source rewind, provider reset, overflow and format changes must clear incompatible state.
2. Use current mutually unique raw observations for continuity. Ambiguity cannot choose a person, create a named identity, renew positive time or update an anchored appearance bank. A fresh contradictory candidate must not become eligible later solely because an uncertain covariance grew. Actual new court evidence can create a new unknown episode.
3. Compare a frozen court-origin appearance anchor with current fresh crops as an independent cue before deciding how to preserve fast valid off-court motion. The existing production torso HSV descriptor is available without inference; the separate appearance investigation is responsible for its measured limits. Existing OSNet adapter/registry support is opt-in, and no checkpoint is present under the inspected cache search; no model was loaded or downloaded. Feature similarity must not teach its own initial mistaken identity, bind roster names or confer scoring authority. Same-uniform doubles, officials with similar clothing, occlusion, truncated crops and broadcast illumination need controls.
4. Preserve every rejected raw detection and diagnostic reason. Gate only the semantic participant hypothesis; do not silently rewrite raw observations or label withheld athletes as non-athletes. Current foreground image context must survive independently and continue supporting scene resets.

This proposal requires an independently evaluated appearance/motion contract; **neither full4D nor the exploratory partition is recommended as a production patch on present evidence.** A pre-ROI positive-continuity hook must not borrow downstream identities/score or ground truth. Any implementation requires a new provider/algorithm identity beyond candidate `court-player-episodes-v1@4`, a truthful new membership-policy fingerprint, pipeline/cache invalidation of dependent perception, and preserved old codec/read compatibility. Keep RFDETR/checkpoint identities unchanged if their bytes and neural preprocessing remain unchanged. Do not overwrite accepted historical cache identities.

## Regression requirements and diagnostic controls

The frozen current provider has an expected RED synthetic regression: a continuously observed, uniquely overlapping athlete immediately outside the baseline disappears after1s. [RED source](test_current_lease_RED.py), [one expected failure](current_lease_RED.log). This establishes the current behavior without claiming a synthetic fix establishes video accuracy.

Twenty diagnostic motion-control cases pass, covering singles/two and doubles/four hypotheses; FPS25/30/60; detector strides2/6; fresh outside continuity without renewing court time; width articulation; mutually ambiguous duplicate candidates without renewal; exact elapsed-time expiry; origin revocation that cannot recover through covariance growth; actual-court reseeding; and scene reset. [Control source](test_shadow_contracts.py), [20-pass log](shadow_controls.log). These test only the diagnostic policy, not production integration.

Before any production acceptance, run RED/GREEN against the actual player/tracking port; preserve raw inputs; test never-inside officials, same-position different-scale handover, true jump/runoff, acceleration, seated/crouching athletes, same-uniform doubles, crossings, partial occlusion, negative/unknown/missing detections, variable cadence, rewind/duplicate time, dropped frames, all lifecycle resets, capacity uncertainty and alias no-reranking. Keep exact Test1 all182 losses visible and all ten source windows, then full fresh Test1 and Test2 versus immutable controls. Scene7857/8106 and Test2 true edits6151/6307/11346 must remain correct; contact/class and anonymous-attribution changes need review separately. All unsupported physical metrics remain unavailable.
