# Current Test1 geometry diagnosis and isolated camera-ground-point repair

## Evidence boundary

The source-bound baseline and diagnostic review contain no rewritten labels or model inference. Bottom-center distances compare generated historical points with current generated points; they are not independently reviewed player/shuttle accuracy. Court8634 is a manual-origin assertion with qualitatively reviewed singles-corner semantics, not certified all-frame calibration GT.

## Actual Test1 calibration and coordinate result

At canonical sourceframe8634/287.8seconds, manual points align visible singles sidelines/baselines. Current automatic doubles outer corners follow the actual outer doubles lines. Comparing unlike corner definitions would create a false calibration failure.

| Diagnostic | Value |
|---|---|
| Correct singles-corner mean disagreement | 1.797572px |
| Correct singles-corner maximum disagreement | 3.529582px |
| Incorrect doubles-versus-singles mean | 41.873640px |
| Current valid main-camera frames examined | 16941 |
| Current valid person rows examined | 33702 |
| Nonidentity camera matrices in actual Test1 | 0 |
| Maximum departure from identity | 3.5612086741038954e-14 |
| Observed ground-point transform defect in actual Test1 | 0 person rows |

![Current versus manual court definitions](frame_08634_current_vs_legacy_court.png)

No current Test1 court-calibration or image-to-court transform failure was established from this frame or the complete camera-matrix scan. No label injection, forced singles homography or corner offset fitting was performed.

## Generated point/reference disagreement

| Comparison | Matched point pairs | Mean px | Median px | P95 px | Maximum px |
|---|---|---|---|---|---|
| player_bottom_center_distance_px | 33466 | 3.069777 | 1.507715 | 10.645645 | 70.435594 |
| fresh_detector_bottom_center_distance_px | 13966 | 1.456916 | 1.025709 | 3.940757 | 68.937185 |
| shuttle_raw_distance_px_both_present | 11853 | 7.459980 | 1.478514 | 3.333657 | 561.768698 |

Full-frame shuttle presence populations: `{'legacy_shuttle_visible=False,current_raw_present=False': 3071, 'legacy_shuttle_visible=True,current_raw_present=False': 2161, 'legacy_shuttle_visible=False,current_raw_present=True': 183, 'legacy_shuttle_visible=True,current_raw_present=True': 11853}`. Player-reference points=33768; current-player rows=33716. All-current anonymous matched pairs33466, unmatched legacy points302 and unmatched current points250. Fresh-detector comparisons preserve detector cadence: they condition on fresh matches; their unpaired-reference count includes normal detector-off frames and is not a false-negative detector count. No distance threshold was fitted to labels.

The shuttle distribution has a close median and smallP95 but a large outlier tail. At frame13153/currentraw(472.38,615.64), the cyan point overlays the near athlete’s shoe region, while the legacy filled estimate(508,55) is near the upper image. The exact-PTS image supports a **probable current raw shoe distractor**; it does not independently certify the legacy coordinate or a physical shuttle label. Motion-window and candidate-evidence review is still required before claiming a quantified shuttle detection error or choosing a fix.

![Exact-PTS raw shuttle disagreement](frame_13153_shuttle_disagreement_overlay.png)

## Reproducible current code defect outside the static Test1 case

Current `_stabilise` previously transformed four image-box corners, constructed an axis-aligned reference envelope, and then the engine calculated its bottom-center as the observed ground point. A point does not commute with this reboxing operation under camera rotation/projective registration. This violates the existing detector-bottom-center coordinate contract without requiring any sporting labels.

Independent20-degree rotation/translation example: original box[0,0,20,40] has bottom-center[10,40]. Its correct transformed point is[95.71612047483234, 61.00790626469303]; the old envelope-derived point is[102.55652334134571, 64.42810769794971], an error of7.647803px. An independent projective example also fails through real engine ingestion.

## Minimal isolated repair

Only isolated `sports/badminton/src/bai_badminton/engine.py` and new `sports/badminton/tests/test_stabilized_player_ground_point.py` were edited. `_stabilise` now accepts an optional existing Homography, transforms the original detector bottom-center separately, and fills the already-existing `PersonObs.court_xy`. The engine passes its already-selected active calibration. Visual box/skeleton/racket transforms remain unchanged. Invalid geometry still clears court positions. No new schema field, cache codec, model, numerical threshold or annotation-conditioned logic was introduced. The original checkout and baseline remain untouched.

No calibrated helper argument preserves previous no-calibration behavior. The change does not claim an actual Test1 rally-score improvement: every measured Test1 camera transform is effectively identity. Root will verify complete fresh before/after Test1 behavior rather than inferring invariance from these diagnostics alone.

## Validation

- **Red:**2 real-engine ingestion failures under rotation and projective camera registration;3 identity/no-calibration/invalid-geometry controls passed.
- **Green:**40 passed in20.27seconds across new ground-point tests plus existing engine camera, coordinate-context, invalid-camera-sample and geometry-context tests.
- Raw input boxes remain unchanged after ingestion; the input `PersonObs.court_xy` remainsNone.
- Tests use explicit homogeneous point algebra and a separate simple court homography; expected values are independent of reboxing.
- Actual imported module path and hashes are recorded below; Git diff againstHEAD also contains inherited changes, so `ground_point_only.patch` is the correct narrowly scoped patch against the preserved improved original.

```json
{
  "actual_imported_engine_path": "/home/administrator/Desktop/sport-analytics/test01-pipeline-fixes-20261110/sports/badminton/src/bai_badminton/engine.py",
  "isolated_engine_sha256": "297592bf0b2596313a763bafddd1db55b395dcbf5b6805039688d86223e3b936",
  "original_engine_sha256": "37defaabca8a8029831a956a644edf7f24fb8d68ece847a07a924721883f8ed7",
  "regression_file_sha256": "b79b122eedac91f4e0cc073ea237d45f2f7c371ce3dd955e6f137b5b680015c5",
  "no_schema_or_cache_changes": true,
  "observed_Test1_G_nonidentity_frames": 0
}
```

Command (from isolated checkout):

```bash
source ../gpu-env.sh
PYTHONPATH="$PWD/engine/src:$PWD/sports/badminton/src:$PWD/agents/src:$PWD/apps/api/src" .venv/bin/python -m pytest sports/badminton/tests/test_stabilized_player_ground_point.py sports/badminton/tests/test_engine_coordinate_context.py sports/badminton/tests/test_camera_invalid_sample.py sports/badminton/tests/test_engine_camera.py sports/badminton/tests/test_engine_geometry_context.py -q
```

## Artifacts

- `diagnostic_coordinate_binding.json`: component-specific qualitative review declaration and source/reference/image hashes.
- `bound_reference_diagnostic_v1/`: strict completed-run diagnostics, all per-file comparisons and every frame’s point candidates.
- `current_feet_transform_probe.json`: complete actual Test1 geometry scan and observed zero-impact result.
- `corner_semantics_and_generic_counterexample.json`: singles/doubles corner diagnostics and exact mathematical counterexample.
- `ground_point_red.log`, `ground_point_green.log`: reproducible before/after regression receipts.
- `ground_point_only.patch`: isolated minimal production change relative to the improved original.
- `isolated_code_provenance.json`: actual module import path and source hashes.
- `largest_shuttle_frame_evidence.json`: exact proxy PTS binding for the frame13153 qualitative outlier.
