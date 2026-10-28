# Published FineBadminton reference evaluation

This workflow compares an application snapshot with published, human-refined FineBadminton labels. Timestamp scores mean **agreement with published hit anchors at the declared tolerance**. They do not establish independently verified physical racket-contact accuracy. The hitter comparison measures **top/bottom court side only**, with no durable person or four-player identity score. This document contains no model results.

## Frozen source

Dataset: [`iLearn-Lab/Finebadminton-20K`](https://huggingface.co/datasets/iLearn-Lab/Finebadminton-20K), revision `72cae601e08c83ee8ec7e19f8fd7850e9158af7d`.

| File | Immutable download | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `0044.mp4` | [Source video](https://huggingface.co/datasets/iLearn-Lab/Finebadminton-20K/resolve/72cae601e08c83ee8ec7e19f8fd7850e9158af7d/videos/0044.mp4) | 23,719,088 | `1ac5999828f4d789e246d3cfce2ef0fbd7b647cd4e40326a6629157b368899e7` |
| `0044_updated.json` | [Source annotations](https://huggingface.co/datasets/iLearn-Lab/Finebadminton-20K/resolve/72cae601e08c83ee8ec7e19f8fd7850e9158af7d/finebadminton-20K/0044_updated.json) | 53,218 | `51d940300a7386253f3af63d8b2f15ecc13b48be02b5c4144bc48f7bc74785b1` |

The dataset card lists Apache-2.0 and both expert-generated and machine-generated annotations. The [FineBadminton paper](https://arxiv.org/html/2508.07554v1), sections 3.1–3.2, describes manual annotation and human verification/refinement of model-assisted structured labels. Keep its citation and source-video ownership with the files. Downloaded media and full source/derived annotation JSON must stay outside Git.

Local `ffprobe` inspection of the hash-verified video found 1280×720, `r_frame_rate=25/1`, `avg_frame_rate=25/1`, 7,577 frames and 303.08 seconds. Check the actual file again when transferring or rebuilding an application proxy.

The JSON contains 41 hit records for Lakshya Sen and Jia Heng Jason Teh in four annotated rallies:

| Rally index | Half-open source frames | Seconds at 25 fps | Hits |
| --- | --- | --- | ---: |
| 0 | `[2197,2530)` | `[87.88,101.20)` | 13 |
| 1 | `[3921,4120)` | `[156.84,164.80)` | 8 |
| 2 | `[4342,4527)` | `[173.68,181.08)` | 7 |
| 3 | `[4841,5150)` | `[193.64,206.00)` | 13 |

Other video spans are unlabelled for this evaluation. They are not negative/no-contact ground truth.

## Timestamp and taxonomy conventions

The paper's section 5.1 describes hitting frames as anchors that partition video into inter-hit segments. This supports interpreting contiguous `hitting.start_frame`/`end_frame` intervals as hit-anchor segments. The public release does not explicitly certify that every JSON `start_frame` is the exact physical racket–shuttle contact frame, nor provide a contact-frame uncertainty bound. The converter retains each published start frame unchanged and uses half-open rally windows as an explicit evaluation convention.

The default tolerance is 0.20 seconds, or five frames at 25 fps. It is a matching criterion selected before evaluating this recording; it is not a provider-validated timing-error guarantee. Timestamp MAE is relative to published anchors. Do not retime labels, infer midpoint contacts, tune an offset, or select a tolerance based on model errors on a held-out recording. Current extraction excludes predictions outside the declared windows, including candidates just before the first anchor.

Mapping version `finebadminton-reference-map-v1` retains raw type, subtype, player name and top/bottom side in every converted record. Unsupported types become `unknown`. Ambiguous serves require a supported short/long subtype. FineBadminton `kill` with an explicit smash subtype maps to `smash`; an explicit net-kill subtype maps to `rush`; an ambiguous bare `kill` remains unknown. Cross-court net shots become family `net_shot` plus placement `cross_court`. The evaluator applies equivalent normalization to prediction `cross_net`, retaining `original_family`; placement is retained but not separately scored. Source comments are not used to rewrite provider class labels.

## Convert on the local CPU

Download the two frozen files into a temporary or ignored directory. The existing `huggingface_hub.hf_hub_download` client can retrieve a file by pinned revision if a direct storage redirect stalls. Verify SHA-256 after download. Do not substitute an unpinned revision or accept a partial MP4.

Probe the actual evaluated source/proxy and use its metadata. For this file:

```powershell
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,duration -of json C:\path\0044.mp4
```

From the checkout, use the actual application session ID and a new output directory:

```powershell
$env:PYTHONPATH = 'engine/src;sports/badminton/src;.'
.venv/Scripts/python.exe -m research.finebadminton_reference `
  --source-json C:\path\0044_updated.json --media C:\path\0044.mp4 `
  --video-name 0044.mp4 --session ACTUAL_SESSION_ID `
  --expected-source-sha256 51d940300a7386253f3af63d8b2f15ecc13b48be02b5c4144bc48f7bc74785b1 `
  --expected-media-sha256 1ac5999828f4d789e246d3cfce2ef0fbd7b647cd4e40326a6629157b368899e7 `
  --fps-num 25 --fps-den 1 --n-frames 7577 --width 1280 --height 720 `
  --output-dir C:\path\new-normalized-reference --accept-published-review `
  --split development
```

The split/reservation options are valid only if the entire recording was reserved before tuning. Otherwise use `--split diagnostic` or `--split development`. Once the recording guides feature or threshold choices, it becomes development data; reserve another recording for subsequent held-out evaluation. Reading labels to implement an importer does not itself create an unseen-model guarantee.

## Recording reservation after the initial baseline

`0044.mp4` is development data for subsequent work because its aggregate results informed a general singles anonymous-context fix. Preserve the initial frozen files and their original historical reports. Generate fresh development manifests instead of editing the original held-out directory. The example above therefore uses `--split development`.

`0046.mp4` was reserved as a new held-out recording at **2026-10-28T17:13:21.0189127Z**, before inspecting predictions or tuning algorithms on it. Selection used compact file size and a distinct match: Lakshya Sen–Shogo Ogawa, compared with Sen–Teh in `0044`. This is match-disjoint, not athlete-disjoint; pretrained training overlap remains unknown. The reservation is recorded in a separate temporary `reservation.json` created before download/inference.

The new recording uses the same pinned dataset revision and provider-review provenance:

| File | Immutable download | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `0046.mp4` | [Reserved source video](https://huggingface.co/datasets/iLearn-Lab/Finebadminton-20K/resolve/72cae601e08c83ee8ec7e19f8fd7850e9158af7d/videos/0046.mp4) | 20,019,008 | `263c7456643f96f37ad5ccc7d04c01c08d201209d49f141997405325709d0a2d` |
| `0046_updated.json` | [Reserved source annotations](https://huggingface.co/datasets/iLearn-Lab/Finebadminton-20K/resolve/72cae601e08c83ee8ec7e19f8fd7850e9158af7d/finebadminton-20K/0046_updated.json) | 93,556 | `0d314ea7c0d963af6f1270850914fb45694cb6c39260981c73e9f893b6adfa08` |

Hash-verified media metadata from local `ffprobe`: 1280×720, `r_frame_rate=avg_frame_rate=25/1`, 7,616 frames, 304.64 seconds. The raw JSON's Git blob SHA-1, `5de9a7db7135ed02a241a42ecfe1373e13bd10ed`, also matches the pinned official API entry.

There are 72 published hit anchors across seven rallies, with half-open frame windows `[1324,1408)`, `[1612,1844)`, `[2028,2416)`, `[2706,2871)`, `[2957,3042)`, `[3168,3430)` and `[5360,5785)`. The respective anchor counts are 3, 9, 17, 6, 3, 11 and 23. No predictions or benchmark scores were used to select these windows or rewrite these anchors.

To regenerate its seven manifests, use the converter command above with `0046.mp4`, `0046_updated.json`, their hashes, `--n-frames 7616`, the actual application session ID, a fresh output directory, and `--split held_out --held-out-reserved-before-tuning`. Keep the same declared tolerance and frozen mapping when the reserved evaluation runs. If its outputs subsequently guide model or threshold changes, it also becomes development data.

Imports default to `status=draft`, `split=diagnostic`. `--accept-published-review` explicitly accepts the provider's reported human refinement and records `human_verified=true`, `provider_human_verified=true`, `our_human_reviewed=false`, publication, revision and hashes. It does not claim that our team reviewed every event. The converter writes one JSON file per rally and refuses overwrites.

## Evaluate an application snapshot

Run actual inference separately on the GPU server using its existing environment. Evaluation does not run inference. Use completed analysis with a contiguous frontier covering every reference window. Back up historical session results before any reanalysis; prefer a fresh isolated session and a stable snapshot for this benchmark.

On the GPU server, from the checkout:

```sh
source ../gpu-env.sh
export PYTHONPATH="$PWD/engine/src:$PWD/sports/badminton/src:$PWD"
.venv/bin/python -m research.evaluation.benchmark_reference_session \
  --annotations-dir /path/to/normalized-reference \
  --data-dir /path/to/stable-application-data \
  --session ACTUAL_SESSION_ID --tolerance-s 0.2 \
  --output /path/to/new-reference-report.json
```

Draft imports require the evaluator's explicit `--allow-draft`. Output files are never overwritten. The evaluator binds session, media hash, canonical FPS, resolution, frame count and frame/time windows. It checks catalogue, raw event-log bodies, source/proxy bytes and input JSON for changes during scoring. It rejects corrected or human-edited shot/contact evidence through the existing machine-only extractor.

The `contact_detection` key remains for compatibility, but its `metric_label` and report `metric_semantics` explicitly describe **published hit-anchor agreement**. Known-family, confusion and joint counts are aggregated across rallies before computing precision/recall/F1; per-rally F1 values are not averaged. Missed, unresolved, wrong-side and spurious events remain visible in the relevant denominators.

Predicted court side comes only from finite stored `hitter_court_xy`, with positive Y interpreted as far/top and negative Y as near/bottom, and supported `classification_context_source` (`named_player` or `provisional_track_episode`). Missing context, nonfinite coordinates or Y=0 abstain. Names, score-slot order, ground-truth names and per-episode person remapping never derive predictions. Pixel geometry is not independently revalidated by this evaluator.

Published reference labels and project-level reservation do not prove pretrained models never encountered this recording. Model-training overlap remains unknown. Professional singles results do not establish amateur, doubles or durable four-player identity accuracy.

## CPU validation

Tests use synthetic fixtures for mapping, boundaries, machine-only extraction, count aggregation and mutations. No public video or full source JSON is embedded in tests.

```powershell
$env:PYTHONPATH = 'engine/src;sports/badminton/src;.'
.venv/Scripts/python.exe -m pytest research/tests/test_finebadminton_reference.py research/tests/test_reference_session_benchmark.py research/tests/test_shot_benchmark.py research/tests/test_participant_benchmark.py -q
.venv/Scripts/python.exe -m ruff check research/finebadminton_reference.py research/evaluation/benchmark_reference_session.py research/tests/test_finebadminton_reference.py research/tests/test_reference_session_benchmark.py
```
