# Contact reliability and same-camera continuity investigation — 2026-11-05

Current source: `64d098b72e592998222f81bf858163b45496d799`, branch `Benchmarking`. This investigation used CPU source decoding, cached fresh-v1 observations, and controlled numerical examples. No production code, checkpoint, source video, annotation, baseline, or historical artifact changed during these experiments. Full neural inference was independently running in the orchestrator; this replay runtime is therefore not an isolated performance comparison.

## Findings and experiment decisions

H10 reproduces on current source. `events/contact.py::score_frame` uses `post/max(pre,1e-6)` for impulse and a direction cosine with a near-zero product floor. A tiny incoming velocity can consequently supply saturated impulse and redirect. A zero incoming vector has no reliable direction; treating its numerical angle as physical redirect support is inappropriate. Missing physical contact labels still prevent contact precision/recall claims.

H02 reproduces in fresh-v1 source-bound evidence. Contact12748 has speed0.022836→1.160224 px/frame, legacy support0.729734, proximity0.0656 and no racket overlap. Contact12771 has speed0.050048→103.816847, support0.785034 and no racket observation. The latter outgoing least-squares fit has residual RMS75.484px; its large velocity is primarily a static-to-new-location association jump, not reliable evidence of physical acceleration. Original reviewed images place the earlier observations on the painted serviceT while players continue overhead activity. This supports a distractor diagnosis without creating new pixel/contact ground truth.

The current temporal chain differs from the older report: accepted contact12748 rebases stationary history, stationary proposal occurs12757 with endpoint12748, closure12763, and contact12771 finalizes12455–12748 and starts another segment. The already-fixed contact-history bug remains fixed. No merge allowance was increased.

## Prespecified contact policy and falsifying controls

The alternative fits each side using only observed, noninterpolated samples within the existing scene bounds. Its slope sensitivity combines a declared spatial scale with fit residuals. The declared scale is2.5/sqrt(12)px, from the TrackNet heatmap cell at1280px analysis width; it is an explicit sensitivity assumption, not calibrated localization-error covariance. Direction support is multiplied by each side's resolved-speed fraction. Relative division by incoming speed is replaced by a bounded positive absolute speed-gain feature after a three-sigma sensitivity margin. No incoming-speed rejection floor is introduced.

This policy is a research proposal, not a calibrated contact model. The unchanged legacy scorer remains available. The process-local replay sets `engine.CONTACT_MODEL=contact_motion_reliability_v1_experiment` so its event provenance does not pretend to be the legacy model.

| Controlled trajectory | Legacy support | Alternative support |
| --- | ---: | ---: |
| small_static_jitter | 0.9781187290638694 | 0.3100255188723875 |
| zero_incoming_weak_launch | 0.9726532132038171 | 0.368667654050042 |
| zero_incoming_clear_launch | 0.9726532132038171 | 0.56531738413356 |
| slow_smooth_apex | 0.4360088281043264 | 0.3100255188723875 |
| fast_smooth_flight | 0.3100255188723875 | 0.3100255188723875 |
| fast_racket_redirect | 0.9168273035060777 | 0.8988644706164346 |
| slow_terminal_stop | 0.8976542855175086 | 0.3100255188723875 |

The two zero-incoming launches remain above the existing0.35 gate. Jitter, smooth low-speed apex and terminal stop lose their saturated direction evidence. These controlled examples validate numerical behavior only; no example is a newly reviewed sporting contact label. All447 reconstructed incoming/outgoing velocities agree with the recorded rounded component scores to<0.001px/frame. At prior live timestamps115/447 retain support>=0.35. That large coverage change is a negative control against declaring improved accuracy from the numerical tests alone.

## Full cached semantic trial: rejected for rally accuracy

Replay uses the actual structural cache decoder, current engine/ports, recorded format decisions and exact explicit rally flags: `rally-evidence-v2`, reconstruction=false, motion_guard=false, exit_recovery=true. It runs full contextual candidate scoring and NMS; it does not merely rescore prior accepted hits. It emitted147 live estimated contacts, compared with447 in fresh-v1. Source fingerprints remained unchanged and all39 predicted intervals were exported with the seven-column contract. This is not fresh perception inference.

| Metric | Fresh-v1 | Alternative cached replay |
| --- | ---: | ---: |
| true_positives | 35 | 34 |
| false_positives | 4 | 5 |
| false_negatives | 1 | 2 |
| precision | 0.8974358974358975 | 0.8717948717948718 |
| recall | 0.9722222222222222 | 0.9444444444444444 |
| f1 | 0.9333333333333333 | 0.9066666666666666 |
| start_frame.mae | 45.77142857142857 | 46.088235294117645 |
| start_frame.rmse | 72.40047355804084 | 73.0871759894829 |
| start_frame.median_absolute_error | 29.0 | 27.5 |
| start_frame.mean_signed_error | 39.2 | 42.6764705882353 |
| start_frame.p90_absolute_error | 98.2 | 98.4 |
| start_frame.max_absolute_error | 297.0 | 295.0 |
| end_frame.mae | 16.314285714285713 | 11.117647058823529 |
| end_frame.rmse | 39.530458419516755 | 15.027425907711697 |
| end_frame.median_absolute_error | 6.0 | 9.0 |
| end_frame.mean_signed_error | -8.428571428571429 | -10.235294117647058 |
| end_frame.p90_absolute_error | 27.000000000000007 | 26.299999999999994 |
| end_frame.max_absolute_error | 218.0 | 43.0 |
| duration_sec.mae | 1.894285714285719 | 1.8833333333333424 |
| duration_sec.rmse | 2.7849083083136366 | 2.6469429894772 |
| duration_sec.median_absolute_error | 1.4333333333333371 | 1.466666666666697 |
| duration_sec.mean_signed_error | -1.5876190476190613 | -1.7637254901960875 |
| duration_sec.p90_absolute_error | 3.9866666666666797 | 3.5966666666666667 |
| duration_sec.max_absolute_error | 9.233333333333405 | 9.833333333333314 |

GT27 becomes a new miss. Its first fragment now ends12673, so the reduced matched-only end MAE excludes the most severe lost row. That is a regression, not successful terminal-boundary repair. GT4/22 starts improve partially (-71→-55 and-29→-3), while GT31 remains295frames late. Previously recovered GT2/19/20 stay matched. Contact-only correction cannot repair the upstream static attractor and should not be adopted as the selected rally candidate. A separately selectable numerical-reliability implementation may support further reviewed contact experiments, with explicit exploratory status.

| GT | V1 interval | Alternative interval | V1 start/end error | Alternative start/end error |
| --- | --- | --- | --- | --- |
| 1 | 339–717 | 339–717 | 96/2 | 96/2 |
| 2 | 891–1255 | 891–1247 | 4/-7 | 4/-15 |
| 3 | 1402–1659 | 1402–1652 | 4/-5 | 4/-12 |
| 4 | 1803–2167 | 1819–2167 | -71/6 | -55/6 |
| 5 | 2309–2496 | 2309–2496 | 99/-4 | 99/-4 |
| 6 | 2661–2799 | 2661–2799 | 103/-7 | 103/-7 |
| 7 | 2983–3377 | 2981–3372 | 7/0 | 5/-5 |
| 8 | 3523–3699 | 3523–3687 | 72/4 | 72/-8 |
| 9 | 3863–4059 | 3862–4057 | 112/-14 | 111/-16 |
| 10 | 4344–4804 | 4344–4804 | 97/-35 | 97/-35 |
| 11 | 4901–5027 | 4907–5016 | 29/-18 | 35/-29 |
| 12 | 5455–5887 | 5455–5866 | 25/16 | 25/-5 |
| 13 | 5979–6315 | 5977–6302 | 21/3 | 19/-10 |
| 14 | 6451–6639 | 6451–6639 | 69/-17 | 69/-17 |
| 15 | 6803–6908 | 6803–6902 | 87/-5 | 87/-11 |
| 16 | 7006–7499 | 7006–7452 | 30/41 | 30/-6 |
| 17 | 7535–7731 | 7537–7731 | 3/-10 | 5/-10 |
| 18 | 7953–8052 | 7954–8052 | 6/-1 | 7/-1 |
| 19 | 8110–8627 | 8110–8627 | 4/-1 | 4/-1 |
| 20 | 8715–9947 | 8715–9947 | 32/-20 | 32/-20 |
| 21 | 10250–10539 | 10250–10531 | 5/-24 | 5/-32 |
| 22 | 10578–10737 | 10604–10693 | -29/29 | -3/-15 |
| 23 | unmatched | unmatched | None/None | None/None |
| 24 | 11274–11397 | 11275–11389 | 3/5 | 4/-3 |
| 25 | 11613–11867 | 11634–11867 | 45/2 | 66/2 |
| 26 | 12046–12196 | 12046–12187 | 70/-1 | 70/-10 |
| 27 | 12455–12748 | unmatched | 4/-218 | None/None |
| 28 | 13115–13439 | 13115–13439 | 61/-3 | 61/-3 |
| 29 | 13686–13982 | 13686–13982 | 7/-12 | 7/-12 |
| 30 | 14222–14331 | 14222–14331 | 3/-4 | 3/-4 |
| 31 | 14701–15171 | 14699–15151 | 297/20 | 295/0 |
| 32 | 15354–15529 | 15354–15522 | 4/-6 | 4/-13 |
| 33 | 15668–15951 | 15668–15951 | 72/5 | 72/5 |
| 34 | 15983–16385 | 16000–16376 | -15/-2 | 2/-11 |
| 35 | 16521–17031 | 16521–17021 | 8/5 | 8/-5 |
| 36 | 17074–17207 | 17074–17183 | 8/-19 | 8/-43 |

Unmatched alternative predictions, without hiding fragments:

| Prediction | Start | End |
| --- | ---: | ---: |
| 23 | 10780 | 10908 |
| 24 | 10949 | 11078 |
| 28 | 12455 | 12673 |
| 29 | 12772 | 12954 |
| 33 | 14430 | 14646 |

Both comparisons retain all36rows, IoU distributions, all-GT/matched tolerance denominators, fragmentation and overlap topology: `next_20261105_contact_reliability_replay_v1/evaluation/comparison.json` compares fresh-v1; `comparison_original/comparison.json` compares frozen original. GT23/27/31 remain fragmented; no unmatched prediction has zero GT overlap.

## Same-camera scene continuity: promising diagnostic, no cut rule adopted

The diagnostic decodes exact original PTS onto960×540 copies for CPU feature analysis. Prior cached player boxes define spatial masks only; carried boxes are not relabeled fresh observations. Pyramidal Lucas–Kanade flow is checked forward/backward; raw patch residuals and intensity differences remain inspectable. No flow threshold is fitted to the edit and no scene/camera state is changed.

| Window | Consecutive pairs | Paired-person valid rows | Median discontinuity score | P99 | Maximum |
| --- | ---: | ---: | ---: | ---: | ---: |
| fast_continuous_play | 516 | 510 | 0.317651 | 2.364314 | 4.239013 |
| mixed_visibility | 320 | 288 | 0.188977 | 2.509655 | 47.343714 |
| same_camera_edit | 410 | 402 | 0.177243 | 2.720352 | 26.321104 |

Here the discontinuity score is the mean of `patch_error*(1-forward_backward_consistent_fraction)` over at least two prior-player masks with>=10features each. It is a diagnostic ranking, not a probability or a validated camera-cut threshold.

At10769→10770 the histogram detector remains false. Foreground feature consistency falls to56.0% and7.0%; patch residuals are31.89/41.55, and the combined diagnostic is26.32. The maximum over510 paired full-GT27 fast-action control frames is4.24. A known whole-camera close-up at14404 has47.34 and is already detected by histogram. The local controls show why foreground continuity discriminates this same-camera edit from ordinary fast action better than a global histogram alone. One match does not establish a universally safe cut detector.

No pre-edit preparation was joined to the later exchange. The supplied GT23 onset still precedes the edit by37frames; its annotation semantics remain unknown. Better scene detection is an independent goal and is not presumed to improve rally IoU.

## Reproduction and preserved evidence

```bash
source ../gpu-env.sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/next_contact_scene_diagnostics.py \
  --scene --output artifacts/benchmarking/experiments/NEW_contact_scene_diagnostics
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/next_contact_scene_replay.py \
  --output artifacts/benchmarking/experiments/NEW_contact_reliability_replay
```

Existing experiment IDs must not be reused. New records:

- `next_20261105_contact_scene_sensitivity`: first numerical/payload sensitivity pass, preserved before the added parity field.
- `next_20261105_contact_scene_foreground_v1`: all447 contact fits, seven synthetic controls,1,246 source-pair measurements, source/script/trace hashes.
- `next_20261105_contact_reliability_replay_v1`:69.285s cached full-semantic replay, policy source hashes/provenance override, bounded GT27 diagnostic trace, events, full FSM trace, both evaluation comparisons.

A draft owner-local contact implementation and21focused tests were prepared in`/tmp` while the orchestrator froze production source for an independent fresh control. Those21tests passed in0.84s. They cover jitter, weak launch, zero denominator, fast redirect, apex/stop, declared scale changes, four-person retention, scene/interpolation barriers, missing-sample counts, bad velocity fit, legacy numerical parity and contextual-NMS partition invariance. These draft tests are software contracts; they do not establish real contact accuracy. The owner-local implementation remains subject to integration review and must stay opt-in.

The remaining requirement is independently reviewed contact/visibility/scene evidence, including weak serves and false static-track transitions. Candidate telemetry and upstream association/background experiments should precede calibration. No new model, dependency, license adoption, live-causal claim, identity name or physical impact label was introduced.

Exact preformatting executed script bytes were subsequently snapshotted under each completed foreground/replay run's`executed_scripts/`, with SHA256 equality verified against the original immutable manifests. `source_snapshot_manifest.json` is supplemental provenance; the earlier result manifests were not rewritten. The final formatted research helpers pass Ruff lint and format checks; formatting does not change the policy. The first sensitivity-only run predates these snapshots and remains a preliminary record.


## Independent renderer review: second missed edit and contact-context leakage

The temporal specialist's synchronized replay was independently reviewed at original frames10578,10601,10603,10604,10607,12748and12771. At10578/10601/10603 the players are walking/repositioning with lowered rackets; at10604 their positions jump to an ongoing exchange and both the broadcast overlay and venue scoreboard content change discontinuously. Original10603→10604 is therefore strong source-image evidence of another same-camera edit, distinct from10769→10770. This is an agent diagnostic finding, not a newly accepted human cut annotation.

A reproducible second probe was run on10565–10615 using the final helper's`--scene-ranges '{"GT22 onset edit":[10565,10615]}'`. The result in`next_20261105_contact_scene_gt22_foreground_v2/` retains exact script bytes, all288 input-cache hashes, source/trace hashes and50consecutive frame-pair measurements. The preliminary ad-hoc probe in`next_20261105_contact_scene_gt22_foreground/` is also preserved. At10604 whole-frame gray MAE is5.02914 versus the next-largest0.39694; histogram correlation0.998871 remains above0.55 and CutDetector is false. Prior-player LK consistency is0%/45.1%, patch residuals52.47/19.15 and the paired discontinuity diagnostic31.49. No scene threshold or production cut decision changed.

This edit has a direct contact-context mechanism. The live estimated contact10601 has support0.790741, incoming speed0.215744 and outgoing89.005696px/frame. Its outgoing fit includes the post-edit10604 observation. A diagnostic context barrier at the source edit leaves only pre-edit same-context samples; outgoing speed becomes0.168895 and both speeds are below the existing0.5 gate. The accepted estimated contact10769 similarly uses the10770edit in its outgoing fit: incoming0.006469→outgoing47.488470; a same-context barrier leaves no independent outgoing velocity at all. The source-bound numerical counterfactual is retained in`edit_contact_context_counterfactual.json` under the second probe. It introduces no GT intervals, changes no inference frames and is not an oracle-cut candidate for promotion.

The missing same-camera transitions therefore allow observations from different physical content epochs to manufacture trajectory acceleration and high-support pre-edit contacts. This helps explain GT22's early provisional contact and GT23's first fragment starting10769, one frame before its visible edit. The GT22 early candidate starts10578 from another weak/static trajectory contact (support0.395209, incoming0.5324→outgoing0.0928), so detecting10604 alone is not proof that every pre-edit false candidate disappears. Upstream candidate validity, source scene continuity and contact velocity reliability remain separate owners.

The renderer correctly labels accepted contacts as hypotheses, preserves raw pixels, exposes the full component scores and distinguishes absent top-k/rejection evidence as unavailable. Its purple `carried` label should be interpreted as carried-or-tracker-only/unmatched; detector_matched=false does not establish that a detector was not executed. Contact `confirmed` is a ledger lifecycle state, not a verified physical impact. At12748/12771, a static model point on the paintedT and active player poses remain contradictory evidence; neither the player posture nor accepted contact ledger establishes a physical contact timestamp or a landing. A general automatic same-camera-edit detector still needs reviewed cuts/fast-action/occlusion controls before changing scene authority.

The draft numerical/control tests were strengthened to32passing cases (0.72s) with missing/incoming/outgoing/interpolated/excluded evidence, window-edge abstention, no observations beyond the declared local context, coordinate-scale/translation semantics, finite-position admission and close contacts on separate scenes. WindowObs has no image dimensions: out-of-view authority is supplied upstream through context/visibility, and the contact scorer must not invent an image-bound gate from coordinate magnitude alone.


## Owner implementation after the independent control source freeze

After the orchestrator released the source freeze, the reviewed opt-in reliability policy was applied to`events/contact.py` and the32draft controls were converted to ordinary production imports in`test_contact_motion_reliability.py`. Only these two owner-assigned production/test files were changed by this specialist. Legacy scoring/selection remains the default; the new policy is separately injectable and is not selected as the rally candidate because its measured trial regressesGT27.

Focused validation ran the32new tests plus existing attribution, pose sampling, scene boundaries, event evidence, streaming integrity, singles, doubles and racket tests: **129passed in8.72s, no skips**. Ruff lint and format pass for the two owned files. Exact log, source hashes and scoped contact diff are retained in`next_20261105_contact_owner_validation/`. This is software-contract validation, not a physical contact-accuracy benchmark. Provider registration and event model provenance belong to the orchestrator's integration files and receive separate integration tests.


## GT27 recovery in the mask-plus-tracklet candidate still uses a suspect contact

Read-only review of`next_20261105_mask_tracklet_semantic` and its own hybrid perception source`next_20261105_mask_ceiling_component` finds the recovered GT27 interval`[12455,12954)`. This interval-level result does not mean that terminal observation or contact validity has been repaired.

The exact current trace still proposes a stationary end at12757 with endpoint12748 and enters CLOSED at12763. It reopens at12766 through an accepted legacy estimated contact. That contact remains at the painted-T coordinate`(645.9249,393.4671)`, with support0.787244, redirect1, impulse1, incoming speed0.1247 and outgoing122.1241px/frame. Racket geometry is available but overlap0; swing0. Its outgoing contextual fit includes the newly admitted airborne observation12769. Thus admitting a real top-edge model observation also creates a large static-to-airborne association jump in contact scoring. The earlier handoff contact12771 has effectively shifted to an earlier still-suspicious transition peak; no physical impact at the T was verified.

Original source12766shows the far player preparing an overhead action. The candidate location is on the center court-line T, spatially apart from that raised racket. The top-edge shuttle streak becomes clearly visible in12769and12771source crops. These images support the coordinate-association diagnosis without supplying a human physical-contact timestamp or a replacement annotation.

At12769the selected processed observation jumps406.79px from the T to`(519.19,6.69)`. It then moves13.80px at12770, but the12771step is only0.333px, so the ordinary three-adjacent-moving-sample run resets. A new moving run begins12772and confirms12774. Both observations matter for causal interpretation: without the12766contact, automatic motion confirmation may arrive outside the existing22-frame recovery budget. The trace's exit_proof is null throughout this block, so the visible new GT27 recovery is not explained by the tracklet exit helper at these frames.

A prespecified negative control removes only the selected12766contact **after unchanged candidate scoring and NMS**, with no reranking, coordinate edits, new thresholds or GT interval input. Its wrapper is`research/next_contact_scene_suppression_replay.py`; all unrelated evidence and explicit rally flags remain fixed. The diagnostic was started just before the orchestrator's independent full-pipeline run, then stopped immediately when runtime isolation was requested. It is paused at frame7259and has no completed metrics yet; no result is inferred from a partial run. It accumulated32.11CPU-seconds before the pause, with zero GPU use. The orchestrator has the exact overlap timing for truthful runtime reporting.

Pending negative-control result, the supported statement is: the new mask repairs a demonstrated visible-shuttle filtering failure and improves the conditional GT27 interval, while contact/association/terminal reliability remains open. A higher rally score or a confirmed contact ledger entry must not be reported as evidence of physical racket impact, a valid terminal stationary observation, or independence from the unstable legacy motion ratio. This manually targeted causal control will never be a production inference profile.


### Deferred interaction experiment: same reliable contact policy on the repaired mask stream

The previous reliability replay used the original finite-mask shuttle stream and`rally-evidence-v2`. It cannot determine whether the same contact policy benefits from newly recovered image evidence, nor can its difference from the new tracklet candidate be interpreted as a clean two-factor experiment.

The next controlled cell, to run after the independent fresh pipeline finishes, keeps `next_20261105_mask_ceiling_component` observations and `rally-evidence-tracklets-v1` fixed, with `use_reconstruction=false`, `motion_guard=false`, `use_exit_recovery=true`, `use_curve_exit=false`. Only `ContactInference` changes to the already implemented `contact-motion-reliability-v1` provider, with exactly `spatial_sigma_px=2.5/sqrt(12)` (0.7216878364870323). No parameter is retuned. The harness must inject the actual production provider so each ContactCandidate carries the correct model provenance. The old research wrapper's process-global CONTACT_MODEL override alone is no longer sufficient after per-candidate provenance was introduced.

Hypothesis: newly restored visible shuttle observations may supply reliable motion cues that were absent in the old-mask trial. The competing hypothesis is that the recovered GT27 interval still relies on a false static-to-airborne association impulse and will fragment if that impulse is downweighted. Both outcomes are useful; neither is assumed successful. A seven-point read-only calculation at12766 shows outgoing fit residual RMS78.7605px and slope sensitivity49.8136px/frame. The fixed reliability formula yields redirect0, impulse0 and support0.03586 instead of legacy0.78724. This predicts removal of that local candidate but does not predict all subsequent NMS/contact/rally outcomes.

Controls: compare against the existing new-mask/legacy-contact tracklet replay on every GT row and unmatched prediction; retain GT2/19/20 and weak-launch/apex/line/floor tests; inspect old and new contact timestamps/components independently of rally F1; preserve the single-contact-removal negative control as a separate diagnostic. To complete a true mask×contact factorial, add an old-mask+tracklet+reliability cell and compare it with the existing old-mask+tracklet+legacy control. The historical old-mask reliability replay is supporting context rather than that missing factorial cell.

The prospective CLI must expose baseline/hybrid-cache path, new output ID, `--contact-implementation contact-motion-reliability-v1`, `--spatial-sigma-px 0.7216878364870323`, `--rally-implementation rally-evidence-tracklets-v1` and the four explicit flags above. Its source/config/provider hashes and dirty diff must be snapshotted before execution. No source change or further semantic/GPU run is being made during the current fresh inference. Numeric reliability remains an exploratory opt-in component until this interaction and independently reviewed physical contact evidence support a stronger conclusion.


## Completed GT27 causal negative control and fresh-cache contact interaction

Both deferred CPU replays completed after the independent full production inference released runtime isolation. No production source changed. The negative control resumed its paused process; its recorded elapsed walltime includes that deliberate pause and is not a speed comparison. The short pre-pause overlap accumulated32.11CPU-seconds and is disclosed in`pause_resume_record.json`. The new interaction ran only after release. Neither replay is another neural inference.

### Removing one suspect contact proves the hybrid GT27 recovery dependency

The intervention removes only the selected12766contact after the same scoring/NMS. All17,268processed shuttle-step values match the control exactly. Selected contact calls are493→492, with exactly12766removed and no added timestamp. Live contacts are454→453; every common live contact has exactly identical coordinates, support and component scores. This satisfies the intended single-variable causal control.

GT27 changes from`[12455,12954)`to`[12455,12748)`plus an unmatched`[12772,12954)`fragment. The end error returns from−12to−218frames. At12771the low-speed duplicate resets the two-sample movement run and the old interval is irreversibly finalized; the next run starts12772and confirms12774. All other35GTcomparison rows are unchanged. Detection becomes36TP/1FP/0FN,F1=0.986301. The interval remains IoU-matched; that does not conceal the restored severe truncation.

This proves that, conditional on these hybrid observations, the improved GT27 interval critically depends on the suspect legacy contact at12766. The negative control is a manually selected research intervention, never an inference profile or an accuracy candidate. It does not independently label the contact false, but it rules out a claim that mask repair alone made GT27 terminal reasoning robust.

Artifacts:`next_20261105_mask_contact12766_suppressed/`contains exact source/script hashes, the sole removed candidate, full trace/events, `causal_parity_validation.json`, unchanged-evaluator metrics and all36rows. The root comparison uses the exact hybrid mask/tracklet control. Additional`comparison_v1/`and`comparison_original/`subdirectories compare against both historical references without rewriting them.

### Same production reliability policy on the new fresh run's own observations

The interaction uses`next_20261105_fresh_air_tracklet_v1`own caches, not the earlier hybrid cache stream. The actual production`_MotionReliableContact`is injected into ContactInference with explicit sigma0.7216878364870323, while tracklet flags remain reconstruction=false,motion_guard=false,exit_recovery=true,curve_exit=false. The reference profile in replay_metadata remains explicitly identified as inherited; `contact_provider_override.json`records the actual selected provider/configuration, verifies injection and confirms every contact event reports`contact_motion_reliability_v1`.

All17,268processed shuttle-step values exactly match the fresh candidate's interval-exact semantic control. Source hashes remain unchanged. The scorer emits154live estimated contacts versus457in the fresh legacy-contact control. These are coverage/selection counts, not contact precision/recall; the lost estimates cannot be called corrected false impacts without reviewed physical labels.

| Metric | Fresh own-cache legacy-contact control | Same-cache reliability provider |
| --- | ---: | ---: |
| true_positives | 36 | 36 |
| false_positives | 0 | 1 |
| false_negatives | 0 | 0 |
| precision | 1.0 | 0.972972972972973 |
| recall | 1.0 | 1.0 |
| f1 | 1.0 | 0.9863013698630136 |
| start_frame.mae | 29.13888888888889 | 29.0 |
| start_frame.rmse | 41.36725758374611 | 41.68333000133266 |
| start_frame.median_absolute_error | 21.0 | 20.0 |
| start_frame.mean_signed_error | 22.75 | 25.77777777777778 |
| start_frame.p90_absolute_error | 69.5 | 68.0 |
| start_frame.max_absolute_error | 106.0 | 106.0 |
| end_frame.mae | 10.333333333333334 | 16.666666666666668 |
| end_frame.rmse | 14.300349646075091 | 39.77785536926014 |
| end_frame.median_absolute_error | 6.0 | 9.0 |
| end_frame.mean_signed_error | -2.2777777777777777 | -15.833333333333334 |
| end_frame.p90_absolute_error | 22.0 | 30.5 |
| end_frame.max_absolute_error | 41.0 | 222.0 |
| duration_sec.mae | 1.1324074074074078 | 1.5000000000000062 |
| duration_sec.rmse | 1.5477083816300448 | 2.071574220993883 |
| duration_sec.median_absolute_error | 0.6333333333333302 | 1.0999999999999943 |
| duration_sec.mean_signed_error | -0.8342592592592682 | -1.3870370370370428 |
| duration_sec.p90_absolute_error | 2.7000000000000064 | 3.0333333333333314 |
| duration_sec.max_absolute_error | 4.0 | 7.533333333333303 |

The policy is rejected as the selected rally candidate. It preserves all36matches but reintroduces GT27 fragmentation: matched`[12455,12744)`has end−222frames, with extra`[12772,12954)`. Its slight aggregate start-MAE reduction does not offset this severe end regression. GT4/22 start errors move−71→−55and−29→−3, while GT31's repaired14430start remains. These are numerical boundary comparisons, not new adjudications of the annotation convention or physical contact timing.

| GT | Fresh legacy start/end | Reliability start/end | Fresh signed start/end errors | Reliability signed start/end errors |
| --- | --- | --- | --- | --- |
| 1 | 264/717 | 264/717 | 21/2 | 21/2 |
| 2 | 890/1255 | 890/1247 | 3/-7 | 3/-15 |
| 3 | 1402/1659 | 1402/1652 | 4/-5 | 4/-12 |
| 4 | 1803/2167 | 1819/2167 | -71/6 | -55/6 |
| 5 | 2308/2496 | 2308/2496 | 98/-4 | 98/-4 |
| 6 | 2578/2799 | 2589/2799 | 20/-7 | 31/-7 |
| 7 | 2977/3377 | 2977/3372 | 1/0 | 1/-5 |
| 8 | 3519/3699 | 3519/3687 | 68/4 | 68/-8 |
| 9 | 3857/4059 | 3857/4057 | 106/-14 | 106/-16 |
| 10 | 4272/4804 | 4272/4804 | 25/-35 | 25/-35 |
| 11 | 4901/5027 | 4907/5016 | 29/-18 | 35/-29 |
| 12 | 5455/5887 | 5455/5866 | 25/16 | 25/-5 |
| 13 | 5979/6315 | 5977/6302 | 21/3 | 19/-10 |
| 14 | 6450/6639 | 6450/6639 | 68/-17 | 68/-17 |
| 15 | 6802/6908 | 6802/6902 | 86/-5 | 86/-11 |
| 16 | 7006/7499 | 7006/7452 | 30/41 | 30/-6 |
| 17 | 7535/7731 | 7537/7731 | 3/-10 | 5/-10 |
| 18 | 7953/8052 | 7954/8052 | 6/-1 | 7/-1 |
| 19 | 8110/8627 | 8110/8627 | 4/-1 | 4/-1 |
| 20 | 8715/9947 | 8715/9947 | 32/-20 | 32/-20 |
| 21 | 10250/10539 | 10250/10531 | 5/-24 | 5/-32 |
| 22 | 10578/10737 | 10604/10693 | -29/29 | -3/-15 |
| 23 | 10769/11085 | 10780/11078 | 36/7 | 47/0 |
| 24 | 11274/11397 | 11275/11389 | 3/5 | 4/-3 |
| 25 | 11613/11867 | 11633/11867 | 45/2 | 65/2 |
| 26 | 11982/12196 | 11982/12187 | 6/-1 | 6/-10 |
| 27 | 12455/12954 | 12455/12744 | 4/-12 | 4/-222 |
| 28 | 13115/13439 | 13115/13439 | 61/-3 | 61/-3 |
| 29 | 13686/13982 | 13686/13982 | 7/-12 | 7/-12 |
| 30 | 14222/14331 | 14222/14331 | 3/-4 | 3/-4 |
| 31 | 14430/15171 | 14430/15151 | 26/20 | 26/0 |
| 32 | 15354/15529 | 15354/15522 | 4/-6 | 4/-13 |
| 33 | 15664/15951 | 15664/15951 | 68/5 | 68/5 |
| 34 | 15983/16385 | 16000/16376 | -15/-2 | 2/-11 |
| 35 | 16521/17031 | 16521/17021 | 8/5 | 8/-5 |
| 36 | 17074/17207 | 17074/17183 | 8/-19 | 8/-43 |

The sole unmatched reliability prediction is12772–12954. All previously recovered rallies remain matched; no row is removed or altered. Full tolerance denominators, IoU/distributions, fragmentation, durations and original/v1 comparisons are retained in`next_20261105_fresh_mask_reliable_contact_replay/`and its`comparison_v1/`and`comparison_original/`subdirectories. The executing wrapper/script/critical source bytes were captured before the run and preserved under`executor_source/`. The final research wrapper received a formatting-only line wrap afterward; the exact executed version remains hash-pinned. Semantic walltime was81.033s with CPU replays permitted to overlap; this is not a fresh-pipeline throughput claim.

Reproduction of this interaction into a NEWdirectory:

```bash
source ../gpu-env.sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/next_contact_scene_provider_replay.py \
  --baseline artifacts/benchmarking/experiments/next_20261105_fresh_air_tracklet_v1 \
  --output artifacts/benchmarking/experiments/NEW_fresh_mask_reliable_contact \
  --contact-implementation contact-motion-reliability-v1 \
  --spatial-sigma-px 0.7216878364870323 \
  --rally-implementation rally-evidence-tracklets-v1 \
  --rally-params '{"use_reconstruction":false,"motion_guard":false,"use_exit_recovery":true,"use_curve_exit":false}'
```

### Truthful status after these controls

The airborne mask defect has direct raw-model/source-pixel evidence and a measured repair. The selected candidate's GT27 interval is recovered, but the terminal/static-association root cause remains open and its recovery is fragile to a single suspect legacy contact. Contact numerical sensitivity is reproduced, exposed and addressed by a separately selectable software policy; that policy has not earned accuracy promotion and is rejected for the final rally selection. A perfect36/36development interval assignment does not verify contacts or make the static T a physical shuttle observation. H02/H10therefore require explicit remaining-risk status, reviewed component labels and an independently controlled association/terminal-evidence experiment. No automatic contact threshold retuning, global gap expansion or default promotion follows from this trial.


## Direct fresh-own-cache single-contact control confirms the selected candidate's dependency

To remove the earlier hybrid-input limitation, the same single-contact negative control was repeated on the selected fresh run's **own** perception caches (`next_20261105_fresh_air_tracklet_v1`). The comparison control is its interval-exact semantic replay, `next_20261105_fresh_air_tracklet_semantic`, independently verified against all36 fresh intervals and457live contact/stroke timestamps. This is a new conditional semantic experiment, not another neural inference. The original hybrid result remains preserved separately.

Only selected contact12766 was removed after unchanged scoring/NMS. The selected-contact call sequence changes496→495, exactly by that one frame; no replacement peak is introduced. Live contacts change457→456, and every common live contact has identical coordinates, raw support, component scores and model provenance. All17,268processed shuttle-step records are identical. All35other GT boundary rows remain unchanged. Source fingerprints remain unchanged. These checks are asserted in`next_20261105_fresh_contact12766_suppressed/causal_parity_validation.json`.

GT27 again splits from the selected fresh interval`[12455,12954)`into matched`[12455,12748)`and unmatched`[12772,12954)`. The matched end error regresses from−12to−218frames; duration error is−7.4s and IoU0.568932. Detection remains36TP/1FP/0FN,F1=0.986301. Thus the direct fresh-cache control confirms the unique-contact dependency on the actual selected run; it is no longer only a finding on the hybrid precursor. Matching GT27 does not conceal its severe partial coverage.

The unchanged evaluator and complete36-row comparison are saved in the experiment root against the fresh selected candidate;`comparison_v1/`and`comparison_original/`compare both historical references. The command was the existing suppression wrapper with`--baseline artifacts/benchmarking/experiments/next_20261105_fresh_air_tracklet_v1 --output artifacts/benchmarking/experiments/next_20261105_fresh_contact12766_suppressed --suppressed-frame 12766`. Exact scripts, removed-candidate values, flags, source hashes, full events and FSM trace are retained. This replay completed in82.622s after runtime isolation was released; no GPU work or production code changes occurred.

The final reliability claim remains bounded: visible airborne filtering is repaired, while GT27's selected interval still relies critically on an unverified legacy static-to-airborne contact. Contact reliability and static/terminal association remain open even though the selected full run matches all36development intervals. The intervention is a diagnostic causal proof and will not be encoded as a frame-specific production rule.
