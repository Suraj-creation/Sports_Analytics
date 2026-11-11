# Test 2 fresh-prefix component overlays

These panels compare **actual fresh baseline model estimates** with source pixels and separately labelled legacy generated points. They are diagnostic evidence, not new human ground truth or a declaration that the baseline run has completed. The renderer does not open the live SQLite database, invoke any model, decode another video, alter predictions or edit original annotations.

## Reproduce and extend

From the repository root, with the existing GPU environment:

```bash
source ../gpu-env.sh
.venv/bin/python evaluation/ground_truth_validation/test_02/diagnostics/component_visual_review/render_component_panels.py
```

The default requested frames are 300,1594,16246,22924. Each invocation examines the currently available **closed `seg_*.msgpack` files**, checks complete contiguous segment frame ranges and stable file bytes/stat information, and copies the entire selected segment into `cache_snapshots/` under its SHA256. This is a snapshot of existing completed segments, not a live worker cache edit. It does not wait or poll; unavailable later frames remain in [manifest.json](manifest.json). Reinvoke after those segments finish. `--frames` accepts additional comma-separated source frame indices when corresponding raw panels already exist in `../annotation_visual_review/frame_metadata.json`.

For every rendered frame, the directory preserves:

- `exact_source_resized.png`: byte-exact copy of the original root extractor's 1280×720 resized source panel.
- `current_cache_frame.json`: complete corresponding prediction frame from the immutable segment snapshot.
- `current_vs_legacy.png`: current bbox/track/pose/racket/shuttle overlay plus clearly identified legacy point predictions.
- `evidence.json`: source-frame metadata/pixel hashes, original and copied cache paths/hash/range, model identities, output hashes and full prediction record.

Existing evidence files are verified byte-identical on repeat use; the renderer raises instead of silently replacing different evidence. The top-level manifest is the explicit mutable progress index. The source video SHA remains `4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`; source coordinates and exact sampled PTS are bound by the independently reviewed annotation certificate in `../annotation_visual_review/`.

## Display semantics

Green boxes and track IDs are current detector/tracker estimates. `det_match` distinguishes matched versus propagated boxes. Magenta shows every finite pose joint and the documented 17-joint skeleton; there is no confidence cutoff chosen from these annotations. Joint0/head and wrists9/10 are labelled for inspection. Pose/racket source frames are printed separately from the current source index, so stale components cannot silently look current. Red ellipses are the current **geometry racket estimate**, with a line to the selected wrist index, not confirmed racket/contact locations. Ellipse axes are drawn as half the saved fit diameters.

Orange cross is the current raw decoder shuttle position, cyan ring the association's selected position. They may coincide. White circles are the two legacy anonymous detection slots; white diamond is the generated filled shuttle, drawn only if its unchanged coordinates lie within the image. Off-canvas values remain printed in the legend and preserved in raw metadata. No legacy value is relabelled as independent physical truth.

## Independent visual findings from the available prefix

### Frame 300 / 10.000000 s

[Actual overlay](frame_00300/current_vs_legacy.png), cache range300–359, current main view and VALID calibration. Both player boxes follow the two visible athletes and the pose skeletons qualitatively follow their body/limb regions. This supports execution/source association at this sampled instant; it does not quantify box/joint accuracy or certify persistent named IDs.

The geometry racket estimates raise a concrete quality concern: track0's high-confidence red ellipse is near the near athlete's head, at **(581.52,418.34), confidence0.909**, while its selected wrist10 is **(651.46,451.12)**. Track1's ellipse is beside/over the far athlete's head at **(678.95,230.32), confidence0.825**, with selected wrist10 at **(629.62,282.57)**. The visible held racket regions do not justify treating either head-adjacent ellipse as a confirmed physical racket. These are model estimates with heuristic support, not calibrated correctness probabilities. A source/algorithm review must determine whether the wrist-search window, shape candidate or shaft association produces the false association; this overlay alone does not prove the exact code cause.

The raw and associated shuttle agree at **(534.93,157.61)**, near the legacy estimate **(536,160)** in the advertising region. This demonstrates model-to-model agreement on a pixel location, not independent shuttle accuracy or physical contact. Downstream contact/outcome claims must inspect the actual object and trajectory evidence.

### Frame 1594 / 53.133333 s

[Actual overlay](frame_01594/current_vs_legacy.png), cache range1560–1619. Current tracks4 and5, matched detector boxes, same-frame pose and racket estimates are present. The main body boxes and pose skeletons approximately follow the two athletes, with track identities differing from the earlier sample; cross-sample ID correctness requires the tracker evidence/epoch history, not an assumption that changing IDs is automatically an error.

Current raw and associated shuttle are **(555.04,390.02)**, whereas the supplied filled trajectory is **(544,737), Visibility=1**, outside the720-pixel image height. This is an exact source-bound disagreement; it cannot be converted to a physical localization error by assuming the legacy value is correct. The visible image contains a bright streak near the current region, but a still image does not certify its shuttle center or a temporal contact. Preserve the off-canvas annotation category explicitly.

Racket estimates remain visually reviewable, including geometry near the far advertising area and the near athlete's torso/wrist region; no whole-component correctness claim is inferred from their execution. Exact centers, confidences and wrist indices are in each frame's JSON.

## Pending evidence and limits

Frames16246 and22924 were not yet available in the fresh prefix at this review's creation. They must be rendered and inspected after their closed segments exist. Largest-disagreement frames may be added after the complete annotation comparison, using source panels extracted once with exact timestamps. Full-run metrics, scored outcomes, accepted contacts, threshold decisions and cross-video regressions remain the central orchestrator's responsibility. No pipeline fix was made by this renderer task.
