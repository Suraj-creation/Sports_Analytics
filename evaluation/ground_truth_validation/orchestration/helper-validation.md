# Test1 component diagnostic helper: contracts and validation

Helper: `evaluate_test01_components.py`. This is offline post-completion diagnosis, not an inference or semantic replay entry point. All annotations, source files and existing run outputs remain read-only. Output requires a new directory outside the immutable original run.

## Normal use

From `Sports_Analytics`, source `../gpu-env.sh` and run:

```bash
.venv/bin/python evaluation/ground_truth_validation/orchestration/evaluate_test01_components.py \
  --run evaluation/ground_truth_validation/test_01/runs/baseline_v1 \
  --output evaluation/ground_truth_validation/test_01/diagnostics/components_v1
```

Use the actual completed run directory supplied by the orchestrator; the example path is not evidence that this directory exists. Original historical failed Test1 publication requires the explicitly supplied `--completion-recovery <recovery-directory>`; default normal success guards are not weakened. Test3 or any different media hash is rejected before annotations/output creation.

The helper requires exact source Test1 SHA256 `877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6`, canonical1280×720,30FPS,17,268frames, completed parent/worker/source/cache guards and exact prediction-to-live-rally-ledger agreement. It reuses the existing strict completion/catalogue helpers, loads every actual cached frame once in source order, and hashes every consumed input again before publication. It never opens original databases directly or reconstructs an `inference.json`.

## Complete reference accounting

Every existing Test1 annotation file gets its SHA256 and an applicability record. All applicable interval families are compared independently with the unchanged IoU0.5 one-to-one evaluator: coarse Full, generated rally, T, T4, mixed Full2 and generated win_predictions. Generated-reference results are legacy agreement, not independent physical accuracy.

Full2 contains20 valid numeric intervals plus malformed data row21 (`...` and absent remaining fields). The malformed original row is retained with an explicit error. All valid positives are compared, but Full2 precision/F1/false-positive counts are null: no negative coverage interval is invented from a partial/mixed file. All unmatched current proposals are retained with frame/time spans under `unscored_current_predictions`, rather than discarded or counted as false detections.

Coarse and generated winner labels are not treated as source-bound physical PlayerA/B identity truth. Known/unknown model winner/stroke output coverage is retained. Player AP/mAP/IoU, IDF1/HOTA/ID-switch/fragmentation accuracy, pose PCK/OKS, physical shuttle visibility/localization accuracy, contact/racket PR/F1/timing, per-shot confusion, score-sequence correctness and semantic highlight quality remain explicit null with exact missing prerequisites.

## Coordinates: default candidates, optional declared diagnostic review

Without `--coordinate-binding`, coordinate distances remain null. The helper exports every frame’s old/current player points, current bounding boxes, old visibility/confidence, current raw shuttle coordinates, view and calibration state to `frame_point_candidates.jsonl` for synchronized overlays. Current raw shuttle cache coordinates are analysis-image pixels; associated `selected_xy` can be registered-reference pixels and are not silently mixed into this comparison.

A later **separate diagnostic run** may supply a source-bound review JSON. It is not a ground-truth certification. Base fields:

```json
{
  "status": "source_and_coordinate_semantics_verified",
  "source_sha256": "877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6",
  "frame_size": [1280, 720],
  "fps_num": 30,
  "fps_den": 1,
  "reviewed_frames": [0, 8634, 9000],
  "reviewer_type": "agent_diagnostic",
  "evidence": ["actual/source-bound/overlay/path.png"],
  "reference_sha256": {},
  "legacy_player_point": "bbox_bottom_center",
  "legacy_shuttle_point": "analysis_image_xy",
  "court_corner_semantics": "outer_singles_floor_corners"
}
```

Replace evidence paths and `reference_sha256` with real files and exact values; do not run with placeholder evidence. Component declarations are optional and independent. A court-only review need not claim verified shuttle or player semantics. Each declared component requires its matching supplied annotation hash: `player_detections.csv`, `Test1_Full_ball_filled.csv`, or `Test1_Full_court.json`. Missing/wrong source/media/reference hashes or invalid reviewed frame IDs are rejected.

Player distance uses anonymous minimum-Euclidean-distance one-to-one assignment per frame, separately for all current rows and only fresh detector-matched rows. No tracking identity or distance threshold is fitted; unmatched reference/current point denominators are preserved. Shuttle distance conditions on both reference visibility and current raw presence; the four legacy-visible/current-present coverage populations remain explicit. Invisible or missing points are not zero-filled. All of this is generated-output disagreement, not AP, identity accuracy or physical shuttle error.

## Court frame8634

The helper recovers current calibration candidates using the live calibration event matching the cache calibration reference, composed with the actual per-frame camera matrix. It exports projected singles and doubles outer-floor corners separately. Current geometry must be VALID/main-view, with matching calibration identity. It does not compare the raw initial calibration untransformed against a later image.

Qualitative review from the provenance agent suggests the supplied Test1 court corners follow the **singles** sidelines, not outer doubles sidelines. Therefore doubles semantics must not be forced. Optional `court_corner_semantics` accepts `outer_singles_floor_corners` or `outer_doubles_floor_corners`, which select different court widths. Without this declared diagnostic review, corner error remains null and both candidates are available for overlay adjudication. When declared, a four-corner pixel disagreement is reported at the annotated frame only; this is not all-frame calibration accuracy or an independently adjudicated calibration label.

No court labels are injected into baseline calibration, and no future-frame correction is used for inference.

## Validation executed

The helper was compiled in the existing GPU-server environment. Independent contract checks executed:

- Loaded actual Full2:20 valid positive rows and malformed source row21 preserved.
- Verified partial-reference FP/precision/F1 are null and unmatched current proposals remain available, with intervals, as unscored records.
- Minimum-distance crossing fixture matches anonymous slot order correctly; empty candidate fixture returns no assignments.
- Timestamp parser accepts raw seconds and MM:SS without an inferred FPS/offset repair.
- An existing complete Test3 run is rejected for its different source hash before any diagnostic output directory is created.
- A source-bound singles-court-only certificate is accepted without falsely requiring player/shuttle declarations.
- A wrong-source certificate is rejected.

These checks establish guarded helper behavior, not a completed fresh Test1 evaluation. Actual fresh-run completion and runtime integration are the orchestrator’s next use of this helper. No model inference, production modification, annotation edit or replay was performed during validation.
