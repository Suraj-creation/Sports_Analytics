# Shuttle perception and TrackNet audit

Audit C; production revision `301baf08be5e989dd0ed93cb885733c3cf6f356a`, frozen benchmark revision `b773e20`. Original video, CSV, baseline outputs, checkpoints and production source were read only. Test 1 is a development benchmark. Model observations and agent visual inspection are diagnostic evidence, not new ground truth.

## Evidence and reproduction

- Baseline `inference.json`, `benchmark_metadata.json`, raw per-frame msgpack caches, prediction/comparison tables and raw events.
- `research/audit_c_observations.py` produces `artifacts/benchmarking/investigation/audit_c/observation_audit.json` from all 17,268 cache frames. It computes a global stabilized/segmented trajectory diagnostic, explicitly **not** an exact recreation of the engine's bounded windows, format resets or contact state.
- `research/audit_c_window_contract.py` executes the actual `TrackNetV3.detect()` tensor/index path with **synthetic heatmaps**, proving output/frame coverage; it does not measure model quality. Results: `window_contract.json`.
- The orchestrator's **exact** production semantic replay reproduced all 49 baseline endpoint pairs. Exact state examples below use `artifacts/benchmarking/investigation/baseline_semantic_replay/fsm_trace.jsonl` rather than the global diagnostic.
- Original-frame diagnostic views: `boundary_frames.png`, `boundary_frames_observations.png`, `stationary_point_crop.png` under the Audit C artifact directory. Frames were selected by source PTS and resized only for display. Red marks show cached TrackNet predictions, not labels.

Reproduce CPU audit work on the configured GPU host:

```bash
source ../gpu-env.sh
python research/audit_c_observations.py
python research/audit_c_window_contract.py
pytest -q sports/badminton/tests/test_tracknet_background_retention.py sports/badminton/tests/test_shuttle_scene_boundaries.py sports/badminton/tests/test_perception_verified_shuttle.py
```

No new GPU inference or alternative-model download was performed by this auditor. Component-test result is recorded in `component_tests.log`.

## Actual implementation chain

| Stage | Source and implementation | Finding |
| --- | --- | --- |
| Model load | `perception/pipeline.py:315`, `_load_shuttle`; `perception/tracknet.py`, `TrackNetV3.__init__` | Registry passes a verified private checkpoint snapshot. Runtime records CUDA:0, FP16, no backend fallback, checkpoint `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a`. Checkpoint parameters select seq_len=8, background concat; architecture checks the loaded state. |
| Image preparation | `tracknet.py:452`, `_prep` | 720p BGR proxy → 512×288 `INTER_AREA` → RGB; concatenate background before eight RGB frames; NCHW 27 channels; divide once by255. This layout agrees with the eight-frame concat checkpoint. Official reference preprocessing uses PIL resizing, so interpolation differs; this is an unmeasured distribution shift, not a demonstrated defect. |
| Inference | `tracknet.py:460`, `_forward`; `:472`, `detect` | Every temporal output position is returned. Step8 is window stride, **not** sampling one frame out of eight. Output assignment retains the input frame's index; inference completion latency is not added to timestamps. |
| Window boundaries | `detect` | Windows cannot cross camera-shot IDs. Short tails repeat the last frame. Repeated padded indices are counted once per window. Real overlaps average heatmaps. |
| Background | `tracknet.py:140`, `BackgroundModel`; `pipeline.py:480`, `seed_background` | Up to120 sampled RGB frames per active shot; observe one per15 frames, refresh after20 new samples. At30FPS refresh nominally occurs every10s and capacity spans60s. Startup uses sampled video frames. `_prep` observes the whole chunk before constructing inputs, so background may incorporate future frames within that chunk (valid for VOD, needs separate causal-live contract). |
| Detection decode | `tracknet.py:193`, `heatmap_to_point` | Apply flight mask, threshold averaged heatmap at0.5, choose the connected component containing the global maximum, return its heatmap-weighted centroid and peak value. No multi-hypothesis motion association chooses between competing components. Peak scores are uncalibrated, not visibility probabilities. |
| Court mask | `perception/isolation.py`, `flight_mask`; `pipeline.py:497`, `process` | Image-space floor hull swept upward by0.35×height and dilated; this is not a 3D airborne court attribution. Model inference can run on a mixed-view chunk but non-main frames are masked/suppressed before temporal ingestion. |
| Trajectory | `shuttle_post.py:54`, `remove_spikes`; `:99`, `fill_gaps`; `:161`, `process` | Adjacent spike limits300/130 proxy px; gap fill≤25frames, moving anchors and≤120px/frame mean-speed gate. Cubic spline marks interp=True and confidence0.35; segmented by camera/replay/coordinate context. |
| Segmentation input | `engine.py:1350`, `_window`; `:1394`, `_advance`, particularly lines1464–1473 | `observed = track.vis & ~track.interp`. Speed uses only adjacent independently observed coordinates; interpolation is deliberately excluded. Thus smooth drawn trajectories do not imply observed evidence or prevent the FSM's invisible-frame counter. |

## Rejected hypothesis: eight-frame inference drops seven frames

The actual method and synthetic contract check reject this hypothesis. Controlled lengths1,7,8,9,48,60,64 all returned one correct output per real input frame. Synthetic heatmaps encode each frame independently; this verifies indexing only.

An important configuration interaction remains: production actually supplied **287 chunks of60 frames plus one of48**, although profile `chunk_frames` is64. For a60-frame, single-shot chunk, step8 uses starts `[0,8,16,24,32,40,48,52]`; frames52–55 receive two window votes. Window phase alternates because60 is not divisible by8. A nominal 64-frame chunk would align eight disjoint windows. This creates uneven context and averaging, **not lost frames**. All-GT frame phase observation rates vary ~0.809–0.888 in this recording, but scene/activity confounding prevents attributing that variation to phase. No phase-causal claim is established.

Window context alone spans at most eight frames (0.267s); it does not directly establish a fixed6.7s frame offset. Multi-second start errors instead require inspecting evidence runs and prior fragment loss.

## Cached evidence coverage

All cache indices0..17267 exist. Raw detections: **11,767/17,268 (68.14%)**. Reconstructed usable geometry:16,941frames. Global diagnostic independently observed after gates/spikes:11,750; interpolated:974. The global postprocessing approximation removed or invalidated only17 raw observations overall; this does **not** show spike filtering has no boundary-local effect. Missing observations total5,501frames; 107 raw missing runs last at least10frames. Missing cache `c=0` means no accepted detection; it does not preserve the true subthreshold heatmap maximum.

| GT rally | Raw observed fraction | Global postfilter fraction | Interpolated frames | Key internal unobserved runs (inclusive) | Stationary-gate opportunities in global diagnostic |
| --- | ---: | ---: | ---: | --- | ---: |
| 2 | .8324 | .8324 | 18 | 1024–1064 (41) | 24 |
| 5 | .6838 | .6838 | 4 | 2255–2307 (53),2424–2458 (35) | 39 |
| 19 | .8509 | .8509 | 37 | 8267–8305 (39),8612–8622 (11) | 15 |
| 20 | .8957 | .8957 | 55 | 9526–9542 (17),9647–9680 (34) | 40 |
| 23 | .8497 | .8497 | 3 | 10909–10935 (27),10937–10947 (11) | 38 |
| 25 | .6980 | .6980 | 40 | 11588–11611 (24),11620–11632 (13),11746–11795 (50) | 8 |
| 27 | .9360 | .9341 | 31 | 12518–12527 (10) | 49 |
| 28 | .6375 | .6324 | 78 | 13054–13111 (58),13130–13147 (18),13156–13168 (13),13253–13271 (19) | 5 |
| 29 | .7816 | .7816 | 27 | 13844–13881 (38) | 9 |
| 31 | .7741 | .7714 | 55 | 14404–14426 (23),14445–14489 (45),14647–14694 (48),14970–14992 (23),15041–15055 (15) | 6 |

The threshold is **shuttle** motion, not player inactivity. Player stationary-vs-moving hypotheses must not be substituted for these recorded low-motion shuttle coordinates.

## Proven mechanisms and bounded hypotheses

### C1 — GT20 airborne disappearance is converted into final termination

**Symptom:** matched segment ends9525,442frames before annotated9967. **Evidence:** raw points at9523=(459.71,70.63),9524=(457.86,54.90),9525=(456.25,41.12), no raw detection9526–9542, returns9543=(435.05,40.66). Proxy resolution1280×720. This geometry and original-frame review support an overhead trajectory leaving/re-entering the upper image, not observed evidence of a rally end.

**Exact trace:** at9535, invisible_run=10 enters ENDING with tentative_end9525; the trajectory is interpolated with x438.44,y−4.44, but `visible=False`. At9543 the FSM is already CLOSED. Observed speed8.286 at9544 produces only one moving sample; missing9545–9546 resets the streak. At9548,23frames beyond tentative_end9525, the previous rally is finalized because the merge budget is22frames. The negative spline y is consistent with the inferred out-of-image arc; interpolation is still an estimate, not measured airborne ground truth.

**Proven cause:** the configured absence/confirmation/closed-resume logic turns this temporary observation gap into a final split. **Alternative explanations:** source-frame micro-label ambiguity; model failure before true image exit; brief repeated gaps delay return-run confirmation. **Confidence:** high for the state mechanism, medium-high for physical out-of-frame explanation. **Causal experiment:** same cached observations, change only continuation treatment for independently bracketed, trajectory-consistent temporary loss; keep interpolated points ineligible as contact observations. **Action:** explicit observed/missing/estimated/invalid evidence and a bounded continuation candidate before finalization. **Expected effect:** reduce early-end max/P90, fragmentation and dependent late starts. **Risk:** incorrectly bridging real between-rally breaks; test nearby separate rallies and scene transitions.

### C2 — GT27 static court-line attraction plus stationary termination

**Symptom:** end12748 versus annotated12966 (218frames early), despite93.6% raw coverage. **Evidence:** cached predictions12748–12768 remain around(645,393) with peaks~0.51–0.58 and many sub3px/frame deltas. Original frame12760 places that prediction on the painted center-service T intersection while players continue an overhead exchange. This supports a static-line attractor, not verified shuttle rest. Pixel-level shuttle GT is unavailable, so this is an agent visual diagnostic rather than a newly labeled localization false positive.

**Exact trace:** acceptedcontact12748 updates last_contact; stationary ending is clamped at12748; closes12763. Contact12771 is23frames after end, so exceeds22-frame merge. That new contact opens a new segment and the same frame's stationary history immediately proposes another end. **Source:** `heatmap_to_point`, `BadmintonMatchEngine._advance`, `RallyFSM.step/on_contact`.

**Proven cause:** stationary model coordinates plus contact/merge timing drive the split. **Hypothesis:** peak selection follows a static white court feature instead of the shuttle. **Alternatives:** a real stationary spare shuttle, genuine shuttle rest and annotation grouping, or true low image-plane motion. **Confidence:** high state mechanism; medium-high static-attractor visual interpretation. **Experiment:** inspect top-k heatmap components and motion-consistent competing peaks around12735–12790; compare unchanged thresholds with temporal association and independent continuation evidence. **Action:** retain ambiguity rather than equating any confident static peak to confirmed end evidence. **Expected effect:** reduce premature stationary endings and false contacts on static features. **Risk:** rejecting true low-speed shuttle/landing evidence and delaying legitimate ends.

### C3 — Early fragments are lost and later fragments win matching

**Symptom:** GT2 start+179frames, GT19+202frames. **Evidence:** first detected portions precede raw gaps1024–1064 and8267–8305; predicted first segments end exactly1023 and8266. Their later fragments, not the early fragments, receive the one-to-one match. **Cause confidence:** high that observed gaps fragment these rallies; exact resumption/rejection reasons are in the orchestrator replay. **Alternative:** inaccurate manual start; weak first launch observations. **Experiment/action:** continuation reconstruction conditioned on compatible pre/post trajectory, court continuity and contact evidence, with no label input to generation. **Expected effect:** improve start MAE/max and lower unmatched-fragment FP count simultaneously. **Risk:** masking truly late starts by unsafe merges; retain raw component intervals and evaluate true separate rallies.

### C4 — Weak evidence is irrecoverably collapsed at the threshold boundary

**Symptom:** cannot distinguish low peak, competing peak, flight-mask rejection, skipped view and physically invisible shuttle from the exported `(None,0)` representation alone. **Evidence:** `heatmap_to_point` returnsNone; `pipeline.process` writes `shuttle_conf=0` for no detection; caches contain coordinates/peak only. Raw heatmaps and subthreshold candidates are absent. **Proven observability limitation**, not proof that0.5 is wrong. **Experiment/action:** optional bounded diagnostic candidate/peak/rejection metadata, retaining raw/estimated provenance independently. **Effect:** enables calibrated analysis and confidence-aware continuation. **Risk:** memory/storage and API compatibility; bounded diagnostics should be opt-in rather than caching full video heatmaps.

### C5 — Preprocessing/background and peak-choice differences remain untested

`INTER_AREA` instead of reference PIL resizing, rolling per-shot background rather than full-rally median, and single peak-component weighted centroid rather than reference contour-size decoding are real implementation differences. They may help or hurt. None is established as a Test1 root cause by existing caches. Freeze all other factors in paired experiments before changing them. New model trials must preserve original-frame timestamps, masks and event interfaces.

## Ranked experiments; no production edits made

1. Replay a temporary-loss continuation policy using exact cached observations, preserving separation between estimates and independent contact evidence. Controls must include legitimate short gaps between distinct rallies; report max/P90 errors and FP/FN, not only IoU.
2. Add diagnostic top-k peaks/rejection reasons and inspect static-line locking atGT27. Isolate temporal candidate association from threshold changes.
3. Paired TrackNet step8/4/1 trials using the same checkpoint/background/masks; then independently test globally aligned or64-frame chunks. For60-frame single-shot input, network windows are8/14/53, not exact theoretical1×/2×/8×. No GPU result for these alternatives is claimed here.
4. Paired background and resize experiments only after continuation/interface defects are addressed. Preserve baseline and compare both perception evidence and end-to-end boundaries.
5. Alternative models need independent localization labels and a held-out video before adoption; do not promote published pixel F1 into rally-boundary F1.

## Scope limits

No new shuttle pixel annotations, alternative pretrained inference, empirical FP16/FP32 comparison, latency/VRAM profiling, or causal eight-frame-step ablation was performed by Audit C. Existing inference is real; the window-contract check is synthetic. The audited video is a broadcast singles source; doubles and amateur-camera validity cannot be inferred from this recording. No baseline file or production source was changed.
