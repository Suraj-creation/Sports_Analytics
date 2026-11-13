# Completed-run visual evidence renderer

`render_validation_evidence.py` creates a **new** diagnostic folder from curated frames of a genuinely completed upload. It performs no inference, semantic replay, metric recomputation, annotation repair, polling or cleanup. No Test3 inputs were used in its development or tests.

Run from the main repository using its configured server environment. Use actual completed paths, an exact original video (or a byte-identical restored copy), and the existing full timestamp audit:

```bash
source ../gpu-env.sh
.venv/bin/python evaluation/ground_truth_validation/orchestration/render_validation_evidence.py \
  --run /absolute/completed-evaluation/run \
  --pipeline-root /absolute/checkout-that-produced-that-run \
  --source-video /absolute/exact-original.mp4 \
  --source-pts /absolute/completed-evaluation/timestamps/source_frame_pts.csv \
  --pts-audit /absolute/completed-evaluation/timestamps/timestamp_audit.json \
  --dataset-label 'Dataset name supplied by the orchestrator' \
  --frames 300,355 \
  --output /absolute/new-visual-evidence-v1
```

`--pts-audit` defaults to `timestamp_audit.json` beside `--source-pts`. Frame IDs are zero-origin **canonical proxy frames**, bounded by the completed run; one invocation permits1–128 unique curated frames. FPS and source/proxy dimensions come from run metadata. The source PTS CSV must cover every frame and equal the unchanged zero-origin CFR timeline rationally, as certified by the completed source/proxy audit. Native VFR, rate conversion, nonzero origins and display-rotated source media require a separate explicit mapping/transform and are refused rather than silently aligned.

For before/after panels add:

```text
--baseline-run /absolute/original-completed-baseline/run
--baseline-pipeline-root /absolute/checkout-recorded-in-baseline-plan
--baseline-pts-audit /absolute/original-completed-baseline/timestamps/timestamp_audit.json
```

The baseline needs its own genuine worker, parent, plan, catalogue and timestamp audit, the same original-source SHA and canonical frame/coordinate basis. Each arm's own proxy bytes are verified and decoded. Different proxy encodings are not falsely declared pixel-identical. `--baseline-pts-audit` defaults to `timestamps/timestamp_audit.json` under the baseline run's parent.

There are **no pipeline imports or ROOT assignments**: the renderer reads original metadata directly. Optional explicit checkout arguments must equal roots recorded in the original plans; a candidate checkout is not rebased to main. Historical source URIs remain untouched if the supplied source is a restored copy with the exact original SHA. This does not relax any source identity check.

## Cases, supplied reference rows and captions

Use `--frames-json /absolute/frames.json` instead of `--frames`. A plain list of integer frames is accepted; an object additionally requires the exact source SHA:

```json
{
  "source_sha256": "REPLACE_WITH_EXACT_ORIGINAL_SOURCE_SHA256",
  "frames": [
    {
      "frame": 300,
      "case_id": "curated-case-identifier",
      "caption": "Describe the observed disagreement; distinguish expected supplied annotation from physical truth.",
      "reference_rows": [
        {
          "file": "/absolute/preserved/reference_row_comparisons.json",
          "pointer": "/Example_rally.csv/comparison/0",
          "role": "legacy_generated_reference_agreement"
        }
      ]
    }
  ]
}
```

`pointer` is a JSON pointer into an existing metrics/reference document. Supplied values are copied verbatim into evidence and the indexes, with input hashes and declared roles. Up to8 reference rows per frame may be included. When that document declares a source SHA, it must match. A document without a source field remains explicitly unbound at the reference-authority level; it is never newly certified GT. Class/box/identity/contact labels are not inferred from filenames, predictions, captions or the renderer. The tool defines no new matching or metric rules.

## Preserved artifacts

- `completion.json`:final source identity, selected frames, arms, all bound input hashes and output artifact hashes; written only after successful verification. Existing output directories and symlink escapes are refused.
- `executed_tool.py.source`, `invocation.json`:exact tool bytes, arguments, Python/platform/PyAV/OpenCV/MessagePack versions and explicit direct-metadata guard scope.
- `input_metadata/`:original timestamp CSV, timestamp audit(s), and requested-frame JSON when supplied.
- `current/`, optional `baseline/`:original worker/parent/plan/session/catalogue receipts, full effective configuration and model/checkpoint/version metadata, pinned small config/model manifests where retained, selected closed cache snapshots and original selected semantic payloads. Source-code hashes remain those in the executed plan; no current checkout is substituted for historical execution.
- `frame_*/`:exact native source pixels, explicit source resize to analysis dimensions, actual arm proxy pixels, separate source/proxy overlays, full raw frame observations and exact rational PTS/pixel hashes. Raw bbox/track/pose/racket/shuttle values, freshness, model support and uncertainty remain in JSON.
- `index.md`, `index.html`:dataset-specific captions, canonical frame/time, source/proxy panels, supplied expected/reference values and links to actual observations/events. HTML caption/reference text is escaped.

Green boxes have `detector_matched=true`; orange boxes are carried/unknown freshness. Magenta shows all finite pose joints, with **no hidden confidence filter**. Red ellipses are raw racket estimates, not certified equipment. Raw and associated shuttle positions remain distinct. The renderer shows every returned person; it does not truncate doubles to two or turn track numbers into named identities. Semantic racket abstention is retained in original event evidence; raw racket overlays deliberately remain raw.

Codec22 adds blue boxes labelled **IMAGE CONTEXT ONLY**. These detached regions can include non-athletes or regions without current court-admission authority. They do not create person tracks, roster identities, athlete-admission evidence or GT. Every codec22 frame requires bounded typed `fg` metadata with exact frame, unique opaque keys, finite positive-extent coordinates and explicit boolean/unknown freshness; the guard checks unselected frames too. Codecs20/21 remain supported, with scene-only context explicitly unknown. Raw V3 witness parameters/supporting keys and decision layout indices remain unchanged in snapshots and appear as provenance captions; the renderer does not recompute scene decisions.

Source resize and actual encoded proxy are separate images and have separate pixel hashes. Their compression/resampling differences are not errors or claims of byte equality. A floor homography is not applied to airborne shuttle positions.

`model_metadata_binding.json` distinguishes the producer's two hash conventions: `manifest_sha256` binds exact manifest bytes, whereas `pins_sha256` binds `json.dumps(parsed_pins, sort_keys=True, allow_nan=False)` as UTF-8. Staging reserializes the pin file, so its raw SHA is retained separately and is not compared to the value hash. Original source pin bytes must still match the recorded plan, and staged/source pin values must agree; changed values or source bytes are refused.

If decoding or caption resolution fails after output creation, `failure.json` and partial artifacts remain; no completion is published and no evidence is removed. Choose a new output path after correction. Original inputs and earlier evidence are never overwritten.

## Verification

```bash
source ../gpu-env.sh
.venv/bin/python -m pytest -q evaluation/ground_truth_validation/orchestration/test_render_validation_evidence_guards.py
```

The47 focused synthetic checks cover exact24fps decoding, four-player preservation, paired-arm provenance, supplied-row captions/HTML escaping, source/checkout mismatch, incomplete receipts, changed cache/catalogue bytes, coherently rehashed malformed frame/header/model identity, full PTS mapping, invalid/duplicate/excess frame requests, output/artifact symlinks, failed baseline refusal, immutable existing evidence and failed-render preservation. Pin serialization checks retain separate raw/value hashes while rejecting changed manifests, changed staged pins, source-byte changes, forged value hashes and missing original pin bindings. Codec22 checks retain separate scene-only context, forbid athlete/GT promotion, preserve raw witness/layout metadata, and reject malformed foreground even on unselected frames; legacy20/21 context stays unknown. They use tiny temporary videos and no models or real benchmark inputs. Passing these guards is tool validation, not physical pipeline accuracy or a completed real-video rendering claim.


Codec23 is accepted with the same mandatory typed foreground/source/receipt
guards. Its new acquisition cohorts, court/camera proof and decision metadata
are preserved verbatim in raw frame snapshots. The actual producer decoder and
completed-run audit validate decision semantics; rendering never grants new
identity, point or ground-truth authority. Synthetic roundtrip and malformed
unselected-frame checks cover both22and23. Earlier45-test receipts remain
immutable records of the prior tool.
