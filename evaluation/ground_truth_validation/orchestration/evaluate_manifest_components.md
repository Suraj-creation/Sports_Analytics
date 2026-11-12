# Manifest-driven component evaluation

`evaluate_manifest_components.py` evaluates **new outputs only**, after the original full fresh worker, parent receipt, source/config/model guards and complete perception catalogue pass. It performs no neural inference or replay. It does not modify Test1/Test2 evaluators, matching, thresholds, annotations or historical reports.

The helper must live and execute in the same checkout as the run's recorded production sources. A MAIN helper refuses a candidate-worktree run before consuming annotation contents. After an active source freeze ends, install the new helper and unchanged supporting helpers in the intended checkout, then execute its native CLI. Do not copy it into a checkout during frozen inference.

```sh
source ../gpu-env.sh
.venv/bin/python evaluation/ground_truth_validation/orchestration/evaluate_manifest_components.py \
  --run /absolute/artifacts/run \
  --manifest /absolute/reviewed_manifest.json \
  --output /absolute/new-component-report
```

The output must not exist, overlap the original run/annotation folder/manifest, or point through an existing symlink. Failed attempts and previous reports remain intact. A source video still needs to be available at its original recorded path because the existing genuine-completion guard rehashes it. No replacement receipt or guard bypass is supported.

## Explicit reviewed manifest

A complete Test1-only control example is preserved at [test01_control_manifest.json](../regression_tests/manifest_component_evaluator_v1/test01_control_manifest.json). This is an example of already reviewed data, not a template that guesses the semantics of a new dataset. No new Test3 manifest or Test3 files were accessed to develop this tool.

Required top-level contract:

```json
{
  "schema": "component-evaluation-manifest:v1",
  "source": {
    "sha256": "exact lowercase 64-character source digest",
    "media": {"width": 1280, "height": 720, "fps_num": 30, "fps_den": 1, "n_frames": 120}
  },
  "time_basis": {"timeline": "canonical_cfr", "frame_origin": 0, "offset_seconds": 0, "interval_end": "exclusive"},
  "annotations": {"directory": "/absolute/original/annotation-folder", "files": []}
}
```

`media` contains exactly those five canonical integer fields. Each must match the finished run. Additional descriptive worker metadata, including codec, audio and original source resolution, is preserved separately; it does not replace canonical dimensions/timing. The `files` array must declare every immediate original supporting file, including files that cannot support a metric. Unexpected files, missing files, nested folders and hash changes reject the evaluation.

Every file entry includes:

- `name`: original immediate filename; `sha256`: exact file digest.
- `role`: one of the five roles below, decided by content review.
- `purpose` and `ambiguity`: explicit reviewed descriptions.
- `schema`: exact CSV column order or JSON top-level key set, plus role-specific mappings.
- `field_eligibility`: one declaration per CSV column or JSON key. CSV declarations require `kind`, `status`, and `reason`. Kinds are `timing`, `coordinate`, `outcome`, `stroke`, `score`, `identity`, or `other`. Status/reason explain what the field can establish and its ambiguities. Outcome/stroke/score/identity value counts are retained separately from predictions and accuracy.

A filename never selects a role. The original interval comparator's legacy filename-derived **role metadata** is overridden by the manifest; the numerical comparator is unchanged.

| Role | Additional schema/entry contract | Evaluation meaning |
|---|---|---|
| `interval_reference` | CSV `interval_format`: `frames_seconds`, `frames`, or `clock`; explicit `reference_role`; explicit boolean `partial_positive_only`. | Original maximum-cardinality/IoU matching and all original boundary/duration/tolerance metrics. Partial positives keep FP/precision/F1 null and unmatched predictions explicitly unscored. |
| `dense_generated_players` | CSV `frame_column`; `slots` containing distinct anonymous `id`, `x`, `y` column mappings; confidence column optional. | Anonymous bottom-center disagreement using unchanged Hungarian assignment, separately over all rows and fresh detector matches. No named identity/box AP inferred. |
| `dense_generated_shuttle` | CSV `frame_column`, `x`, `y`, `visibility`, `visible_values`, `invisible_values`. | Raw shuttle disagreement and presence coverage. Unknown visibility remains unknown. Byte-identical tables with identical declared schemas are evaluated once, retaining aliases. |
| `manual_court` | JSON `top_level_keys`; canonical `frame_no`, `frame_size`, `corners` with TL/TR/BR/BL; reviewed `corner_semantics` when scoring. | Single-frame singles/doubles floor-corner disagreement only under a valid binding/current calibration. No all-frame or airborne3D accuracy. |
| `supporting` | Exact CSV/JSON schema and field eligibility, explicit purpose/ambiguity. | Original contents retained; no unsupported metric fabricated. |

The original supported interval column conventions are `Start_Frame,End_Frame,Start_Time_sec,End_Time_sec,Duration_sec`, `start_frame,end_frame`, or clock `start_time,end_time`. The declared convention must match the comparator branch; the tool does not rename columns or change units. Inconsistent/blank interval rows are retained under the original comparator policy. Valid intervals outside source extent reject the evaluation.

Dense tables must contain every canonical frame exactly once in order. Optional `timestamp_column` with `timestamp_format` (`seconds` or `clock`) must align to frame/fps within the original1e-6second tolerance. There is no filling, offset search or index repair. Invalid numeric coordinates and out-of-image values remain flagged in raw evidence; coordinates are never clipped. Confidence values do not create a tuned evaluation cutoff.

## Optional coordinate certificate

Declare the reviewed certificate in the manifest:

```json
"coordinate_binding": {"path": "/absolute/source-bound-certificate.json", "sha256": "exact certificate digest"}
```

An optional `--coordinate-binding` argument must agree with that declaration. The certificate must bind source SHA, canonical size/fps, actual reviewed frame IDs, reviewer type, evidence image hashes, and reference hashes. Existing certificate conventions are supported: `legacy_player_point=bbox_bottom_center`, `legacy_shuttle_point=analysis_image_xy`, and `court_corner_semantics=outer_singles_floor_corners` or `outer_doubles_floor_corners`.

Each scored primary reference must be named in `reference_sha256`; order an identical generated duplicate after its reviewed primary. Missing binding produces unavailable distances/court accuracy, rather than zero. A source-bound agent coordinate review only supports diagnostic agreement; it is not independent physical ground truth.

## Outputs and scope

`component_reference_metrics.json` includes every interval metric, tolerance and missed/extra/unscored ID; generated-point and court diagnostics; actual event/class/outcome/score coverage; complete cache/tracking coverage; measured resources; actual verified model hashes, backend declarations, profile, source plan/root and consumed-input hashes. Ten unsupported physical accuracy families remain explicitly null with prerequisites.

`reference_raw_details.json` retains every original annotation row/key, field eligibility, semantic field counts and interval comparisons. `point_reference_XX.jsonl` holds synchronized original/predicted point rows, invalid/out-of-image flags and anonymous assignments. `component_raw_details.json` retains detailed event, scene, OCR, track and resource evidence. `REPORT.md` is a compact summary; arrays and per-frame observations remain in separate JSON/JSONL evidence.

No AP/mAP, IDF1/HOTA, PCK/OKS, contact/racket F1, stroke confusion, winner/score or highlight accuracy is manufactured from generated references. Successful execution is separate from measured accuracy. Actual source/native-root scope is recorded; a MAIN control is never described as testing candidate production code.


The evaluator also saves the exact `evaluation_manifest.json`, `recorded_plan.json`, optional `coordinate_binding.json`, and every consumed Python helper under `executed_helpers/`. The recorded pipeline commit belongs to the original inference plan; the native evaluator root and helper hashes identify the separate evaluation implementation.

Validation:44 focused guards pass on this workspace; the optional retained-data controls compare all six saved Test1 and three saved Test2 interval metric dictionaries exactly, including partial-reference exclusions. A genuine completed MAIN-native Test1 evaluation also reproduces player/fresh-player/shuttle aggregate disagreements exactly and manual court mean within1e-12. It performs no new NN and does not test candidate production code. [Final validation receipt](../regression_tests/manifest_component_evaluator_v1/verification_receipt_final.json). Three retained-data/report cases skip explicitly when their local preserved fixtures are unavailable; the remaining contracts use small controlled fixtures. No Test3 data was read.

## Scene-proof structural compatibility

The evaluator now obtains the colocated `analyse_native_completed_run.load_native_interfaces(ROOT, ROOT)` boundary and requires its returned analysis module to be the exact already-imported native module. The decoder and structural auditor must share the evaluator's recorded native root. Every packet passes the actual native diagnostic decoder; relative camera claims are additionally checked against the actual adjacent packet. A raw-false epoch increment needs a positive V4 raw/V3 decision proof, confirmed source format and calibrated court/camera binding. Missing, downgraded, unknown, no-barrier, forged or unapplied proofs reject evaluation. Original strong raw/unknown fallback remains supported.

This only changes structural audit compatibility. Raw hypotheses remain distinct from actual resets, and every numeric comparison, matching threshold, interval/partial-reference policy, point assignment, distribution, court calculation and annotation contract is unchanged. Structural tool/proof hashes are retained in `provenance.structural_compatibility`, `input_sha256` and copied helper snapshots. No guard ROOT is reassigned. A candidate must receive the colocated adapter and auditor only after its existing source freeze ends; this update was **not installed in frozen2418**.

The new validation is separate from the original44-guard receipts: [manifest_component_evaluator_v2](../regression_tests/manifest_component_evaluator_v2/REPORT.md).61 focused cases pass (the original44 plus17 new structural/root/AST cases). A genuine completed MAIN-native Test1 control reproduces every original result value exactly, except explicitly expanded tool provenance/input hashes. No candidate-native generic evaluation or Test3 content analysis is claimed by this control. Actual2418 weak-frame355 native decoder/adapter controls are separately recorded in [the postprocessing compatibility validation](../component_evaluations/pre_test03_audit_compat_v1/IMPLEMENTATION.md).
