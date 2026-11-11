# Test 2 scene continuity: existing repair and remaining acquisition blind spot

This is a read-only current-source/historical-evidence review. No production
change, new detector inference, new full-video result or independently reviewed
scene ground truth is claimed.

## The historical false reset is already addressed

The old Test 2 run used `foreground-content-continuity-v1` with
`barrier_hypothesis_v1`: a raw hypothesis could reset tracking directly. Current
source supports the inherited experimental
`foreground-content-continuity-v2/barrier_detector_layout_v2` selected by the
current evaluation profile. It retains the original raw observer, then acquires
a detector observation on the exact current frame before tracker mutation.
Complete unique correspondence to all prior two-to-four regions vetoes a reset;
changed layout supports a barrier; missing/ambiguous detector evidence remains
explicitly unknown with a documented raw-barrier fallback.

The raw observer's `foreground-scene-hypothesis:v2` telemetry version is not the
same thing as the provider implementation/policy version. Comparing only that
raw version string would incorrectly imply the historical and current tracking
actions were identical.

`recompute_current_scene_controls.py` recomputed all **51 recorded detector-probe
cases** with current source. It retained **49 barriers** and vetoed the two
source-supported Test 2 false candidates at **7703 and 23639**. All 13 Test 1
candidates remained barriers. Source/model/frame/image and fixture hashes are
preserved in `current_scene_recorded_probe_evidence.json`. This is a deterministic
recomputation from recorded detector observations, not 51 fresh neural calls and
not exhaustive scene precision/recall.

Existing generic source/correspondence/cache tests passed: **54 passed** in
`current_scene_regression.log`. The group covers two and four actors, disjoint
layouts, single-actor loss, occlusion, ambiguous overlapping boxes, missing
geometry/detector sources, source/image/model binding, tampering, actual recorded
cases, cadence alternatives and cache compatibility. No new failing test was
manufactured for the already-resolved false reset.

## The missed edit at 11346 remains outside the trigger

Retained shared reports and compact historical evidence describe a visible
same-camera edit near **11346 / 378.2 seconds**, with a score change and player
repositioning. The later inherited-improvement fresh run had one prior tracked
person at11345, none at11346/11347, two at11348, unchanged content epoch13 and no
raw/change-decision record. This exact trigger failure is distinct from the
already-repaired false-positive reset mechanism.

Current source explains the acquisition boundary:

1. `SceneContinuityDetector.observe()` requires two-to-four immediately preceding
   regions; otherwise it returns unknown with
   `two_to_four_prior_regions_required` and clears adaptive history.
2. The layout policy deliberately constructs that base observer. The alternate
   `SceneContinuityDetectorV2` can measure a single region for diagnostic modes,
   but a single-region change is not enough to authorize a multi-actor barrier.
3. `PerceptionPipeline` calls `probe_detection()` and `layout_decision()` only
   when the raw observer produces `evidence.hypothesis`.
4. Therefore the corroborating detector cannot rescue an edit that never enters
   the raw candidate set. Frame11346 is absent from the 51-candidate fixture.

This is a demonstrated scope limitation of the available acquisition design,
not a newly proven safe minimal code patch. Merely dropping the minimum-region
requirement, substituting 49-frame-old boxes, setting an edit by frame ID or
lowering image thresholds could cause resets on one actor's lunge, occlusion or
courtside handling. An unknown detector layout also does not independently
confirm an edit. The documented fallback is an explicit experimental policy;
it should not be silently relabeled a certainty or removed without controls.

## What the current baseline must resolve

Await the current completed cache and compare exact windows **7698–7708**,
**11335–11358**, and **23634–23644**. For each frame preserve source PTS, current
tracks/freshness, main-view/calibration validity, raw status/reasons, whether a
detector probe ran, the actual layout decision, content epoch, and rally/contact
state transitions. Use source pixels to separate same-camera edit, ordinary
articulation, missing person detection and physical activity context.

If the new baseline still misses11346, independently acquire an alternative cue
without writing it into the accepted pipeline: current source pixels, fresh
detector boxes and scoreboard layout observations can support candidate research.
Prespecify a candidate acquisition policy and test it against continuous rapid
motion, single-person occlusion, true edits, camera changes, missing geometry and
four-player scenes. Keep observation-episode barriers separate from official
points and physical rally endings. A source score pixel difference alone is not
a parsed score transition or cut proof.

An independent annotation reviewer also observed opposite near/far jersey roles
before and after11346; persistent physical identity cannot be recovered by
assigning Player A permanently to the far court. Broadcast scoreboards have
historic-game columns and a rightmost current-game column. These are diagnostic
interpretations, not a new reviewed A/B mapping or accepted score sequence.

## Existing experiments should not be repeated blindly

The shared reports document rejected correspondence-only and cadence-only
policies: suppressing appearance-only alarms also lost real Test 1 edits10770 /
15579 or Test 2 edits4257 /5174 /14107. Existing source-cadence regression windows
retain those controls. Broad background/scene heuristics or a simple lower
threshold do not become justified because one known edit is missed.

Relevant retained reports are
`research/test_video_benchmarks/reports/shared_component_and_pipeline/PIPELINE_REMAINING_ISSUES.md`,
`PIPELINE_COMPONENT_VALIDATION.md`, and
`PIPELINE_REPAIR_IMPLEMENTATION_REPORT.md`. Their old absolute paths into retired
run roots describe historical provenance; use surviving compact evidence rather
than assuming those full raw runs still exist. Current fresh baseline evidence
will be recorded separately and must not overwrite that history.

No production repair is proposed solely from this review. The supported action
is to carry forward the already-implemented detector-layout fix and investigate
the current missed-acquisition example against independent controls.
