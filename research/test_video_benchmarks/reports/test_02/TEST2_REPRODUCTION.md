# Test2 reproduction and provenance — 5 November 2026

This experiment uses the current production upload path with fresh neural perception. Semantic own-cache replay is a subsequent diagnostic and is never counted as fresh inference. Original Test1 artifacts, models and Part2 annotations remain unchanged.

## Repository and runtime

Repository: `/home/administrator/Desktop/sport-analytics/Sports_Analytics`. The parent workspace directory is not itself a Git repository. Initial branch was `Benchmarking`, HEAD `caa91761948d09f2cfe4937b0db743fff8643a12`, with a clean working tree. Keep this branch: the earlier general instruction naming `main` predates the explicit benchmark branch authorization. Do not reset historical experiments.

Run commands from the repository and use the configured environment:

```bash
cd /home/administrator/Desktop/sport-analytics/Sports_Analytics
source ../gpu-env.sh
git branch --show-current
git rev-parse HEAD
git status --short
```

The initial inventory is `artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/discovery_inventory.json`. It contains initial and capture-time Git state, installed distributions, actual hardware, source listing/download receipt bindings and 7,264 read-only historical file hashes covering 2,867,743,793 bytes. All hashes that could be compared with the previous release index matched. Capture-time dirtiness includes this task's changes and is distinct from the clean starting checkout.

Actual hardware is two NVIDIA GeForce GTX 1080 Ti cards, 11,264 MiB each, compute capability 6.1, driver 580.178.04. GPU UUIDs are `GPU-96e23501-7ac6-918a-adf7-047ff31a6ae3` and `GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab`. A profile filename containing RTX4000 does not identify this hardware.

Runtime inspection found Python 3.12.12, Torch 2.14.1+cu126, CUDA build 12.6, cuDNN 91002, ONNX Runtime 1.29.0, PyAV 19.0.1, OpenCV 5.0.0.93, NumPy 2.5.3, SciPy 1.18.1, Pydantic 2.14.0 and PyYAML 6.0.3. ORT advertises TensorRT, CUDA and CPU providers; these are availability observations, not per-node execution measurements. The prior recorded ORT node-placement probe is described in `GPU_PERFORMANCE_REPORT.md` and applies to its own models, shapes and configuration. Test2's run receipt supplies its actual provider settings and process allocation.

## Exact source and download

The exact previously shared URL is:

```text
https://drive.google.com/drive/folders/1_2QWSYd_X_BojdRwbu-AMKdx74cIQvGp?usp=sharing
```

This exact folder link appears in the original user benchmark instruction at `/home/administrator/.codex/history.jsonl:10`, session `01a1a79f-fb26-7a81-8d1b-c392df74960c`, and `docs/architecture/audits/part2-label-readiness-20261103.md:11`. No separately shared direct Test2 file URL was found. File selection came from the live contents of that exact supplied folder; a reconstructed direct URL was not substituted for the original source.

The experiment retains `shared_url_evidence.json`, `discovery_source.json`, `drive_folder_listing.html`, `drive_files.json` and `download_receipt.json`. The live listing selected `video_raw/Test2_Full_Rev.mp4`, ID `17EeE7JmLC4zQNWzeTjr7cZk_DFYdh3Bs`. Its ID, filename, size and digest agree with `docs/testing/task2/drive-video-download-manifest.json:28–31` and the earlier Test1 public-listing provenance.

Download used existing gdown 6.5.1, folder discovery with `skip_download=True`, then only the selected file ID with `resume=True`, `retries=3`, through official Drive endpoints. The existing inference `.venv` was not replaced or modified to install gdown. The download receipt records the actual downloader environment and method; the inventory correctly reports gdown absent from the inference `.venv`.

Verified original bytes:

| Property | Value |
| --- | --- |
| Filename | `Test2_Full_Rev.mp4` |
| Absolute location | `/home/administrator/Desktop/sport-analytics/Sports_Analytics/Part2/video_raw/Test2_Full_Rev.mp4` |
| Bytes | 2,453,914,397 |
| SHA256 | `4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a` |
| Video | H.264 Main, 1920×1080, progressive, `yuv420p` |
| Nominal / average FPS | 30/1 / 30/1 |
| Source time base | 1/15360 |
| Container frame count | 29,296 |
| Video duration | 976.533333 seconds |
| Audio | AAC LC stereo, 48,000 Hz, time base 1/48000, duration 976.533 seconds |

`video_metadata.json` preserves FFprobe stream/container output. `source_frame_pts.csv` and `source_timestamp_audit.json` independently retain all 29,296 decoded frames: zero-origin frame `f` has exact source PTS `f × 512` at time base 1/15360, all 29,295 PTS increments are 512, there are no nonmonotonic timestamps or reported decode errors, and the last frame ends at 976.5333333333333 seconds. This establishes source CFR 30 by decoded timestamps; the independent proxy verification is recorded below.

The completed media-preparation output was then decoded independently while neural inference continued. `proxy_pts_precompletion/timestamp_audit.json` and `proxy_frame_pts.csv` verify all 29,296 source/proxy rational presentation timestamps are identical, with identity frame mapping from 0 seconds through the final frame PTS 976.5 seconds. Neither decoder reported an error. Proxy SHA256 is `2841ee54fb0b6d28c2a57e89293ba4530173980635c21aa8d08f60f52931b6cd`. This is a complete media/timestamp check, not a neural-run completion claim. Final validation must additionally bind that proxy digest and source identity to the completed inference/executor receipts.

Verify independently without modifying the source:

```bash
sha256sum Part2/video_raw/Test2_Full_Rev.mp4
ffprobe -v error -show_streams -show_format -of json Part2/video_raw/Test2_Full_Rev.mp4
```

No Test2 video or partial copy existed in the workspace, `/tmp` or Downloads at discovery. The historical nine-video download note referred to a Windows copy; it was not evidence that these files remained on this server. `Part2/video_raw` initially contained only `.gitkeep`.

## Source chronology and selected configuration

The selected Test1 tracklet experiment used source `33d3a5b1bcfd945555b76360cc361881e5a3eb8a`. Later commits through task-start HEAD are:

| Commit | Result |
| --- | --- |
| `011e39a` | Source-bound replay, causal controls and failure-package verification |
| `181cb91` | Fresh shuttle admission results and unresolved causal failures |
| `1308250` | Causal observations, contact reliability, optional ambiguity handling, scene authority and pipeline reliability contracts |
| `8599325` | Media/perception/runtime evidence harnesses; frozen source for six later fresh neural runs |
| `f85b1df` | Physical uncertainty transport, stable CSV and application/Q&A/calibration/failed-job reliability |
| `caa9176` | Preserved production-readiness studies and release gates |

The old `rally-evidence-tracklets-v1` profile is a reference, not automatic authority for Test2. The later association+scene experimental configuration was exercised on complete Test1 and Test7 inputs. Production-readiness concluded that it remains experimental: Test1 detection was complete, but contacts, shot labels, boundary accuracy and independent labels remain insufficient for production promotion. This task freezes current source and the selected configuration anew rather than bypassing an old source-root digest guard.

Model originals are inventoried against the unchanged previous release:

| Artifact | SHA256 |
| --- | --- |
| RF-DETR-small ONNX | `fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e` |
| RTMPose-M archive | `f7fbb6c5c11a1bb70f3d445e4ddec5d144ea89ad5649c081ef976f9b24a0b741` |
| RTMPose-M graph | `5c0a4bf67953e6d2ac43ce15e77dc9d5d354ae18430a47d2c5963a7bc5683e3c` |
| TrackNetV3 checkpoint | `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a` |

The complete upload plan records source/configuration/model input hashes, captured source files, exact YAML and Git dirty state. The executor verifies those bindings before and after its worker. Use its actual invocation and output paths from the completed executor receipt when repeating the run in a new directory.

## Cross-video comparability limits

`artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/comparability_audit.json` retains exact input paths/hashes and the source diff. Read-only comparison against the frozen Test1 association+scene metadata verifies that all 65 recorded badminton-domain source hashes and 27 of 28 engine source hashes match the frozen Test2 plan exactly. The sole engine difference from `8599325` through task-start `caa9176` is `engine/src/bai_engine/config.py`: later LLM token-budget field validation, reported/strict mode and per-call output-cap settings. There is no domain/perception/rally numerical source change in that commit interval. The matcher is retained unchanged.

The Test1 scene YAML and Test2 prepared YAML differ only in passive diagnostic ranges: Test1 retained 7 selected ranges covering 2,187 frames; Test2 retains 120 windows covering 3,600 frames, spread from the input's first through last frame without labels. This changes telemetry coverage and overhead. All numerical model/temporal settings in those YAMLs match. Actual runtime/model/provider receipts still need comparison at completion; matching YAML does not itself establish identical device placement or elapsed-work scope.

Session metadata are not byte-identical. The frozen Test1 executed constructor omits `players` and `roster`, so the frozen schema supplies two unnamed scoring placeholders (`P1`, `P2`) and `roster=None`. The prepared Test2 session explicitly records `players=[]`, `roster=None`. There is no standalone Test1 session JSON in the frozen association+scene directory; initialization is established from its executed runner and unchanged schema, without connecting to its historical SQLite database. Both sessions initialize format as unknown and use sustained-court auto-inference; Test1 was not configured as singles. Its frozen event trace records inferred singles at frame 120. Test2's eventual format decisions must be reported from its own completed evidence.

The placeholder-name difference reaches `ScoreReconciler` through `player_names`. Its only name-based binding method discards null names, so both initializations supply an empty effective known-name map; no rally-numerical effect from that list difference was identified by source inspection. Persisted/public scoring-name metadata can still differ. Report this as a matched numerical profile and compatible source implementation, with different recording/session metadata, telemetry selection, model-staging paths, hardware allocation and shared-resource concurrency; do not describe it as an identical full runtime/configuration or a controlled performance comparison.

## Fresh inference and evaluation separation

The actual fresh preparation and execution commands are:

```bash
.venv/bin/python research/production_external_stress.py prepare-upload \
  --video Part2/video_raw/Test2_Full_Rev.mp4 \
  --profile-source artifacts/benchmarking/experiments/prod_20261105_fresh_association_scene_v1/profiles/experiment.yaml \
  --case test2 \
  --output /home/administrator/Desktop/sport-analytics/test2-runs-20261105/protocol_v1
.venv/bin/python research/production_external_stress.py run \
  --plan /home/administrator/Desktop/sport-analytics/test2-runs-20261105/protocol_v1/plan.json \
  --case test2 --gpu-index 0 \
  --output /home/administrator/Desktop/sport-analytics/test2-runs-20261105/fresh_v1
.venv/bin/python research/production_external_stress.py run \
  --plan /home/administrator/Desktop/sport-analytics/test2-runs-20261105/protocol_v1/plan.json \
  --case test2 --gpu-index 1 \
  --output /home/administrator/Desktop/sport-analytics/test2-runs-20261105/fresh_repeat_v1
```

The preparation directory exists and preserves the exact plan, captured source and `UPLOADTEST2` input session. Completion is established separately by the finished executor receipt, rather than by these command lines. Repeat in new output directories. The upload preparer verifies source decoded count and unchanged CFR proxy rate, constructs a fresh source-bound session with no predefined players, and enables only bounded passive diagnostic windows. Full decoder/association caches remain available for all frames. Neither command accepts a ground-truth path. Annotation contents must not be loaded into perception, tracking, event generation or segmentation.

`fresh_v1` is the predefined scored arm. `fresh_repeat_v1` is a second complete fresh neural run of the same frozen plan, launched on physical GPU1 before Test2 labels were loaded, to test numerical/endpoint reproducibility. It is not a second configuration or an opportunity to choose the better score. The workers overlap and share CPU, RAM and I/O despite using separate physical GPUs. Report both runtime scopes; this concurrency prevents a controlled speed comparison with historical Test1. Compare raw cache values, output endpoints and semantic outputs after both receipts complete.

`prefix_reproducibility.json` preserves the historical early check conducted before label access: the first 480 completed cache frames matched across decoder coordinates/support, association, people, court geometry/calibration, view and content evidence. It is superseded by the completed `full_reproducibility.json`: all 29,296 frame payloads match, all 489/489 cache files are byte-identical, prediction CSVs are byte-identical, and normalized semantic event comparison has zero differences. The prefix artifact remains as provenance rather than an outstanding completion requirement.

Only after complete predictions are written does the evaluator load `Part2/dataset/Test2_Full/Test2_Full_rally.csv`. The original annotation is immutable. The earlier annotation audit warns that generated `_rally.csv` files have incomplete review provenance. The requested Test1-compatible reference comparison can measure agreement with this supplied table; it cannot by itself resolve whether every row is independent manually adjudicated sporting truth.

Keep one-to-one maximum-cardinality then maximum-total-IoU matching, threshold 0.5, zero-origin half-open intervals and exact FPS conversion. Preserve all extras and misses, both boundary-tolerance denominators, and seven-column exports. Do not promote a failed source guard into an authorized cached replay or fresh run.

## Diagnostic replay and regression controls

`research/production_external_semantic_replay.py` now selects the recorded executor case from a `production_upload` plan rather than requiring the literal `test7`. It checks the immutable input-session digest and binds its SID, source URI and source hash to the completed output. Existing completion, source guard, plan digest, media count/frontier, proxy bytes, cache catalogue and runner/helper proof checks remain enforced. Replay uses the completed run's own perception and can establish deterministic semantic parity; it does not rerun neural perception.

Independent review additionally found that the old loader ignored the parent executor's `worker_report_sha256`. A modified inference report/profile could therefore enter replay despite its recorded completion digest. Two focused controls reproduced this defect before a mandatory hash comparison fixed it. The correction affects metadata validation only; no neural observations, segmentation semantics or evaluation thresholds changed. `metadata_guard_regression/` preserves red controls, an intermediate fixture-adjustment failure, final green/lint logs, exact executed sources and a hash-bound receipt. Final combined validation passed 103 tests in 2.35 seconds.

Focused validation executed in the configured GPU-server environment:

```bash
.venv/bin/python -m pytest research/tests/test_production_external_semantic_replay.py -q
.venv/bin/python -m ruff check research/production_external_semantic_replay.py research/tests/test_production_external_semantic_replay.py
.venv/bin/python -m ruff format --check research/production_external_semantic_replay.py research/tests/test_production_external_semantic_replay.py
```

Initial loader validation: 44 tests passed in 1.42 seconds. After adding output-artifact digest controls, the combined replay, external-reference and parity-audit suites passed 101 tests in 1.83 seconds; Ruff checks passed. Controls include an arbitrary recorded `test2` case, invalid case kind, missing/wrong case, changed original-session bytes and inconsistent SID/source despite updated metadata, together with existing cache/source/helper guard controls. These are software-contract tests, not component-accuracy evidence.

Replay manifests add `output_artifact_sha256`, mapping `events.jsonl`, `current-events.jsonl`, `parity_vs_fresh.json`, `emission_frontiers.json`, `contact_readouts.json` and the optional `bounded_fsm_trace.jsonl` to their exact SHA256 values. The manifest excludes its own hash and mutable SQLite files. `verify_replay_output_artifacts` validates complete expected population, regular nonsymlink files and exact bytes before diagnostics are consumed or an optional arm accepts the baseline. Diagnostic output therefore remains bound to the source-run/cache/input/harness proof. A full-video trace uses `--trace-ranges '[[0,29296]]'` as passive telemetry; no annotation boundaries select that range.

## Completion receipts

Both fresh workers and their parent executors completed successfully. Each processed all 29,296 frames, reached canonical frontier 29,295, recorded `cached_perception_used=false`, and retained 489 own perception-cache files. Both parents verified the unchanged frozen source/inputs, original model copies and completion-time source-bound cache catalogue after their workers closed. The catalogue digest is identical in both runs: `e6d50773286e13684c1c57b7542895e9b224f5c350ed4dcf440642727615a580`. The source and proxy digests equal the separately decoded PTS audit identities. No original worker was interrupted or restarted.

`full_reproducibility.json` supersedes the prefix-only check: all 29,296 frame payloads match, all 489 perception-cache files are byte-identical, both proxies match and both prediction CSVs are byte-identical (SHA256 `a49494fa848a54d0a47256743a7b634a1f8dda3b5a84120a1d8b8d765192f358`). Source-bound semantic event comparison reports no differences after resolving run-generated event and participant IDs through their recorded origins. It does not claim raw event JSONL byte identity, cross-hardware determinism or correctness against labels. The predefined primary remains the scored run.

| Measurement | Primary `fresh_v1` | Repeat `fresh_repeat_v1` |
| --- | ---: | ---: |
| Physical GPU | 0 | 1 |
| Worker elapsed seconds | 6544.650144 | 6332.028585 |
| Parent elapsed seconds | 6554.687973 | 6344.420933 |
| Worker frames/second | 4.476328 | 4.626637 |
| Parent frames/second | 4.469473 | 4.617600 |
| Model staging seconds | 1.756688 | 2.086041 |
| Component/model initialization seconds | 8.839453 | 8.818851 |
| Worker max RSS KiB | 3,032,436 | 2,968,496 |
| Worker CPU seconds | 23,315.610990 | 22,970.305132 |

Worker elapsed begins after model staging, includes media/analysis/completion-cache work, and differs from the broader parent interval. Component initialization is a timed subset and must not be added to overlapping perception stage totals. These same-host concurrent measurements are observations, not a controlled speed comparison with Test1 or a performance guarantee.

Primary report SHA256 is `64f5fde890af06030e220bcd488a0a8e20c22545517542efa61440e2644b322c`; repeat report SHA256 is `b93d326951c17c736f6c9068756e59e87f34163e3f5f9308af4d5098776fc29a`. Their parent receipts are `/home/administrator/Desktop/sport-analytics/test2-runs-20261105/fresh_v1.executor.json` and `fresh_repeat_v1.executor.json`. Exact CLI, GPU UUID, source guard, model postverification, cache verification and launch samples are retained alongside the workers.

Both actual shuttle runtimes report Torch CUDA, logical `cuda:0`, FP16, no backend fallback and the unchanged TrackNet checkpoint digest. RF-DETR and RTMPose report CUDA+CPU provider sequences without fallback; these receipts do not separately profile every node. Association uses NumPy CPU, scene continuity OpenCV CPU, and racket evidence the OpenCV ellipse/shaft heuristic. RapidOCR 3.10.0 records detector `090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f`, classifier `e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c` and recognizer `6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884` graph hashes, actual configured providers and options. Optional OSNet/ReID remains explicitly unavailable. Original models were not replaced.

The isolated product check used the existing `prod_20261105_frontend_release_v5/build` explicitly, since the smoke tool's older default is v2. Read-only preflight verified all 45 build-file hashes, all 6 recorded source hashes and the exact embedded content of 76 local frontend sources across source maps; none differs from the current source. Existing Firefox and geckodriver executed the checks. Completed Test2 results were copied to a separate data tree before serving on ephemeral loopback ports with `start_engine=false`; the original SQLite database was never opened. This checks actual transport/rendering/export consistency and is not another inference run.

`test2_product_executor.py` extends the existing actual HTTP/Firefox harness with analytics, reviewed/estimated individual data, highlights, heatmaps, insights, state and provider-status reads, plus seven browser panels. It checks deterministic summary/API equality and same-session highlight evidence references when present. The Ask panel was inspected without submitting a question; HTTP logs contain zero provider-request POSTs. The following invocation ran only after both neural workers had completed:

```bash
.venv/bin/python artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/test2_product_executor.py \
  --completed-run /home/administrator/Desktop/sport-analytics/test2-runs-20261105/fresh_v1 \
  --build artifacts/benchmarking/experiments/prod_20261105_frontend_release_v5/build \
  --output artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/product_validation_v1
```

`product_validation_v1/results.json` records successful completion: all 11 added API endpoints returned 200, seven actual browser panels rendered the correct Test2 video/source, the four browser-downloaded exports matched independently fetched HTTP bytes, and the public durable event IDs/counts exactly matched the copied producer output (73 rally ends and 812 contacts/strokes). No stale Test1 label appeared. All 2,456 consumed original file bindings, current-source guards and frontend guards remained unchanged. The owned server was reaped after its graceful-stop timeout required SIGKILL; geckodriver exited normally. Independent checks found both PIDs gone and both ephemeral ports closed.

These successful transport checks expose important product coverage limits. All 73 candidate rallies are unofficial, so the official application rally CSV has zero rows, highlights are empty, the four queried P1/P2 presence/movement heatmaps each contain zero samples, and official shot-accounting totals are zero. The UI separately shows 73 rally candidates and 231 of 812 shot events classified. No candidate was removed from the raw benchmark predictions. The original harness's `all_official_boundaries_exact=true` is vacuous for an empty export, and the positive highlight-reference loop exercised zero rows; neither establishes positive boundary/highlight accuracy. `product_validation_v1/product_review.json` records these limits explicitly. The JSON match summary is deterministic session/analytics/highlight data, not generated prose; provider-status availability describes local configuration only, with no connectivity or answer-generation check.

`product_empty_outputs_causal_audit.json` follows this absence back through the actual producer Parquet and event JSONL. All 58,338 person rows are retained and visible, 56,485 have finite floor coordinates, 46,629 contain current-frame pose, and 57,968 reference a participant observation. Every player row nevertheless has `player_id=None`; all 812 contacts and 812 strokes likewise retain anonymous actors. The engine deliberately initializes physical identity as unresolved independently of `Session.players`, preserving visual episodes while withholding legacy P1/P2 attribution. Therefore the empty heatmaps are not evidence that person observations were dropped or that Test2's empty player-name list selected an incorrect dictionary key.

Every rally independently remains `phase=unknown`, `official=false`, with the exact reason “match activity requires human or scoreboard confirmation” and unavailable score transitions. The only stabilized broadcast OCR event, at frame 22924, contains unmapped `SXFI:21` / `LIVE:12` rows; it does not establish a sequence of accepted source score increments. The strict activity policy does not promote formation/tempo alone. The analytics rebuild consequently has no official-owned strokes or intervals to admit, and its subsequent named-player row gate also has no eligible rows. API and frontend correctly request their declared legacy P1/P2 keys and receive missing-grid zeros. This is a substantial accepted-evidence/product-coverage limitation, with no proved producer-to-API key-mapping defect. Filling it by inventing identities, official points or highlights would violate the evidence contract.

Component diagnostics call `frame.s` raw shuttle evidence relative to association and temporal processing. It is the decoder output after the court-mask gate; it does not mean the unmasked heatmap maximum. Unmasked/masked peak diagnostics and candidate/rejection information have their separately recorded schemas and bounded full-diagnostic coverage. Keep these evidence levels distinct when interpreting absence or rejection counts.

## Post-inference annotation audit and unchanged evaluation

These commands ran after the primary predictions and completion receipts existed; `label_access_barrier_receipt.json` retains that ordering. Both tables remain immutable. The fine reference is the requested `_rally.csv`; the coarse table is a separately reported sensitivity reference and does not replace the primary score.

```bash
.venv/bin/python research/test2_annotation_audit.py \
  --csv Part2/dataset/Test2_Full/Test2_Full_rally.csv --fps 30 --frame-count 29296 \
  --output artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/test2_rally_annotation_audit.json
.venv/bin/python research/test2_evaluation.py \
  --ground-truth Part2/dataset/Test2_Full/Test2_Full_rally.csv \
  --predictions /home/administrator/Desktop/sport-analytics/test2-runs-20261105/fresh_v1/predicted_rallies.csv \
  --inference-json /home/administrator/Desktop/sport-analytics/test2-runs-20261105/fresh_v1/inference.json \
  --frame-count 29296 --fps 30 \
  --output artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/evaluation
.venv/bin/python research/test2_annotation_audit.py \
  --csv Part2/dataset/Test2_Full/Test2_Full.csv --fps 30 --frame-count 29296 \
  --convert-coarse artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/test2_coarse_converted.csv \
  --output artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/test2_coarse_conversion.json
.venv/bin/python research/test2_evaluation.py \
  --ground-truth artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/test2_coarse_converted.csv \
  --predictions /home/administrator/Desktop/sport-analytics/test2-runs-20261105/fresh_v1/predicted_rallies.csv \
  --inference-json /home/administrator/Desktop/sport-analytics/test2-runs-20261105/fresh_v1/inference.json \
  --frame-count 29296 --fps 30 \
  --output artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/evaluation_coarse_reference
```

Frozen Test1 supplemental reporting used `research.test2_evaluation.supplement` on the unchanged Test1 annotation and each frozen prediction CSV at 30 FPS / 17,268 frames. It asserted that the entire resulting primary metric dictionary equals that run's existing `metrics.json` before writing new supplemental artifacts. Frozen `next_20261105_fresh_air_tracklet_v1` produces `test1_historical_reference`; frozen `prod_20261105_fresh_association_scene_v1` produces `test1_matched_profile_reference`. `aggregate({'Test1': reference, 'Test2': primary})` records both comparisons in `cross_video_comparison.json`. Neither original Test1 directory is changed or re-inferred. Use new destination paths for reproduction: these tools intentionally refuse existing output directories.

## Own-cache replay, causal trace and final regression gate

The exact first diagnostic invocation was:

```bash
.venv/bin/python research/production_external_semantic_replay.py \
  --run /home/administrator/Desktop/sport-analytics/test2-runs-20261105/fresh_v1 \
  --session UPLOADTEST2 \
  --output /home/administrator/Desktop/sport-analytics/test2-runs-20261105/owncache_v1 \
  --trace-ranges '[[0,29296]]'
```

It failed strict parity because replay substituted diagnostic provenance for the original inferred-format event at frame 96. All other event counts/payloads matched. `owncache_v1`, its log and failure summary are preserved. The diagnostic helper was corrected to validate the recorded format event and reuse its exact original provenance; the comparator and production core were unchanged. Red controls (4 failures) and final 93 focused passing tests are retained in `replay_provenance_red.log` and `replay_provenance_green.log`.

The same invocation with `--output /home/administrator/Desktop/sport-analytics/test2-runs-20261105/owncache_v2` then passed strict baseline parity, with zero semantic event differences, 73 rally ends, 812 contacts, 812 strokes and all 29,296 ordered FSM steps. Its manifest binds `bounded_fsm_trace.jsonl` SHA256 `70a28ce6f9a35000d085406e2c4a620854c83a0b77a36e3ee953c111a1d52b21`. This replay reuses recorded format decisions and retained perception; it reruns neither format detection nor any neural model. It is a causal diagnostic after the two fresh neural runs, not a third inference run.

```bash
.venv/bin/python research/test2_causal_analysis.py \
  --run /home/administrator/Desktop/sport-analytics/test2-runs-20261105/fresh_v1 \
  --replay /home/administrator/Desktop/sport-analytics/test2-runs-20261105/owncache_v2 \
  --evaluation artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/evaluation \
  --output artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/causal_analysis
```

Final combined research/benchmark validation passed 637 tests in 8.62 seconds (`full_research_benchmark_tests_v2.log`). The prior two failures were stale synthetic test fixtures missing the newly mandatory `production_upload` kind; their failed log was preserved, fixtures were updated to the real plan contract, and no guard was weakened.

After that final test gate, `historical_integrity_readback.json` read back all 7,264 initially inventoried historical Test1/source/model/report files (2,867,743,793 bytes): every SHA256 and size matched, with zero missing/changed files in 7.668 seconds. No original SQLite connection was opened. Full fresh inference, complete two-run perception/prediction reproducibility, source/proxy timestamp identity, isolated product transport and historical preservation are verified within their recorded scopes; none certifies sporting accuracy or broad generalization.

## Actual failure-viewer and source-review checks

The completed `failure_package/` contains all 40 significant/unmatched cases and 6,551 source-frame JPEGs with exact source PTS, retained perception and a digest-bound FSM trace. The actual Firefox check was:

```bash
.venv/bin/python artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/viewer_browser_executor.py \
  --package artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/failure_package \
  --output artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/viewer_browser_validation_v2
```

The first browser-test attempt is preserved as `viewer_browser_validation_v1`: its readiness check incorrectly assumed WebDriver could access the page's top-level lexical `const D`, although Firefox had rendered source frame 23. The test harness was changed to use real DOM selectors/events and displayed JSON, leaving the package unchanged. V2 passed all 40 cases with 170 rendered frame/PTS/source-image checks, 40 screenshots, overlay-toggle and playback controls in 23.118 seconds. Post-read verification confirms all 170 displayed time bases are exactly 1/15360 and source PTS × time base equals frame/30. Both owned processes were reaped, their ephemeral ports closed, and the viewer HTML retained its original hash. This is tested synchronization and rendering, not 6,551-frame visual adjudication.

`source_visual_review.json` records an agent diagnostic review of GT1, 5, 6, 7, 8, 14, 23, 24, 30, 34, 35 and 37 using exact-frame contact sheets, case/causal JSON and additional unoverlaid consecutive source images. It preserves input hashes, sampled frame IDs, qualitative confidence and independent-review limits. Many onset discrepancies include visible service preparation; GT8/14 terminal references extend into post-point resets, and GT35's reference start is visible previous-point retrieval. Stronger scene observations are continuous play across a false barrier at frame 7703 and an abrupt same-camera edit at 11346 missed by the recorded epoch. Yellow shuttle markers and boxes are model overlays, not adjudicated physical evidence. Neither the original references nor predictions were changed, and no numerical threshold/core correction was justified solely from this diagnostic batch.

## Independent OCR node-placement diagnostic

After both original neural workers closed, a separate component-only probe inspected the existing OCR runtime on proxy frame 22924, using the unchanged reader's cold top-left 576×180 search crop. It ran on free physical GPU1, UUID `GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab`. `ort_ocr_node_probe_v1/report.json` and `verification.json` bind the original source, proxy, decoded PNG/crop, models, raw ORT profiles and exact executed script. Source and proxy PTS both equal 11737088 at 1/15360, or exactly 11462/15 seconds. All three OCR graph hashes equal the completed full-run runtime's hashes.

Recorded command:

```bash
.venv/bin/python artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/ort_ocr_node_probe_v1/executed_probe.py \
  > artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/ort_ocr_node_probe_v1/execution.log 2>&1
```

The probe enabled only process-local ORT profiling/output prefixes. It changed no provider, model, thread, preprocessing or threshold configuration. Executed optimized-node placement was 190 CUDA detector nodes, 179 CUDA classifier nodes, and 181 CUDA plus two CPU recognizer nodes (Concat/Slice). Model loading took 0.887536 seconds; the first profiled call took 10122.236 ms and the one subsequent fixed-crop call 8029.148 ms. These two calls do not establish steady-state latency, original-run per-node placement, performance causation or sporting/OCR accuracy. The crop did not restore the original full-run reader's ROI/history.

Raw OCR observations include `AXELSEN` and `ANTONSEN`, while the unchanged layout parser selects `SXFI:21` / `LIVE:12` branding rows in this diagnostic. This supports an unresolved scoreboard-layout interpretation limitation; no parser/provider tuning or invented score/identity binding was applied. The probe script creates artifacts exclusively and refuses overwriting existing outputs. Reproduction needs a new empty artifact location and copied executor with its output destination adjusted; preserve the recorded v1 files.
