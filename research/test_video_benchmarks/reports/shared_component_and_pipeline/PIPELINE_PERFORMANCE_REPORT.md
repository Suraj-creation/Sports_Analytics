# Pipeline performance evidence and pending full-video measurements

**Final scope clarification:** the user requested Video2 only. Completed additional local-video checks are preserved as incidental historical context. The extra amateur run was interrupted and is not a completed benchmark. No further video inference is running. The additional Video2 repeat was not performed: preparation timed out during its300second FFprobe count before a new plan or NN run was created. The original full fresh Video2 run, independent completion proof, unchanged evaluation and failure analysis are complete. Nothing was deleted.

Status: component experiments, Test1/Test2 posthoc technical audits, and normal India/doubles/Test7/Denmark execution receipts are complete. The extra amateur run was subsequently interrupted under the Video2-only scope; it has no full-run resource result. Test1/Test2 processed every frame, then their original workers exited1 during catalogue finalization. Independent completion proofs preserve those failure statuses and establish coverage without rerunning neural inference. The completed probes support an **explicit CPU OCR experiment on this Pascal host**. Neither their results nor the descriptive full-run numbers establish a controlled whole-pipeline speed improvement, regression, real-time capability or production promotion. No partial-run extrapolation is used below.

This report accompanies [PIPELINE_REPAIR_PLAN.md](PIPELINE_REPAIR_PLAN.md). Historical Test2 and GPU reports remain unchanged. The active repair branch is `repair/pipeline-generalization-20261105`, based on `caa91761948d09f2cfe4937b0db743fff8643a12` with recorded working-tree changes. The initial pre-run suite passed3,053tests; its [log](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/full_suite_v3.log) is preserved. The final frozen-source combined suite passed **3,151 tests, 19 warnings, in 438.46seconds**; [final log](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/full_suite_v5.log). Passing tests does not establish sporting accuracy or performance.

## Actual hardware and execution environment

The configured application profile name `gpu-rtx4000` describes a target configuration. The actual machine has **two GTX 1080 Ti cards**, rather than an RTX 4000 Ada. Hardware and package evidence comes from [runtime_inventory.json](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/runtime_inventory.json), supplemented by a read-only `nvidia-smi` query during this report's preparation.

| Item | Observed value |
|---|---|
| CPU | Two Intel Xeon E5-2699 v3 sockets; 18 cores/socket, one exposed thread/core; 36 logical CPUs |
| CPU affinity | CPUs 0–35; two NUMA nodes |
| RAM | 128 GB class host; Linux `MemTotal=131912644 kB`, approximately 125.80 GiB usable |
| Physical GPU0 | NVIDIA GeForce GTX 1080 Ti, 11,264 MiB; UUID `GPU-96e23501-7ac6-918a-adf7-047ff31a6ae3` |
| Physical GPU1 | NVIDIA GeForce GTX 1080 Ti, 11,264 MiB; UUID `GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab` |
| GPU compute capability | 6.1 on both cards |
| NVIDIA driver | 580.178.04 |
| Python / Torch | 3.12.12 / `2.14.1+cu126` |
| Torch CUDA build / cuDNN | 12.6 / 91002 |
| ONNX Runtime GPU package | 1.29.0 |
| PyAV / OpenCV module / NumPy | 19.0.1 / 5.0.0 / 2.5.3 |
| RapidOCR / trackers / supervision | 3.10.0 / 2.6.1 / 0.30.9 |
| ORT advertised providers | TensorRT, CUDA, CPU |
| TensorRT Python package | Unavailable in the inventory; no TensorRT execution established |
| `psutil` | Unavailable; worker telemetry uses existing `/proc`, `resource` and `nvidia-smi` instrumentation |

CUDA build version, driver version and physical GPU identity are different facts. A process assigned one UUID can see that physical card as logical `cuda:0`; completed-run receipts must bind the UUID, worker PID and visible Torch properties. Registered providers alone do not prove executed-node placement. A configured precision string or FP32 NumPy export does not prove internal arithmetic precision.

The earlier [GPU placement report](GPU_PERFORMANCE_REPORT.md) contains bounded RF-DETR/RTMPose executed-node profiles and TrackNet tensor hooks. Its conclusions apply to its recorded inputs, providers and sessions. They are not new full-run placement measurements. No profiler was inserted into the source-frozen repair workers.

## OCR backend and threading comparison

The registry string `rapidocr_v4@4` is a **legacy package alias**, not proof of actual PP-OCRv4 execution. Authoritative Test1 `ci.runtimes.ocr` records RapidOCR3.10.0 and these actual graphs, matching the controlled baseline/probe hashes:

| Stage | Actual filename | Recorded package configuration tag | Actual SHA256 |
|---|---|---|---|
| Detector | `PP-OCRv6_det_small.onnx` | `PP-OCRv6` | `090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f` |
| Classifier | `ch_ppocr_mobile_v2.0_cls_mobile.onnx` | `PP-OCRv4` | `e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c` |
| Recognizer | `PP-OCRv6_rec_small.onnx` | `PP-OCRv6` | `6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884` |

The classifier's package tag and older filename are recorded separately; neither is renamed to fit the alias. Actual Test1 providers are CPU-only for all three stages, fallback=false, with ORT intra/inter thread fields0 and requested thread count unset. Package-selected graphs are indirectly pinned by the package/configuration and explicitly identified in runtime/cache records; the registry alias alone does not independently pin the three graphs. Equal actual hashes support these controlled comparisons. Per-stage approved graph pins would make registry-only provenance clearer; no graph or registry change was made during the runs.

The same 25 saved inputs were evaluated with CUDA/default threads, CPU/four threads and CPU/default threads. They comprise eight uniform frames per verified Test1, Test2 and Test7 proxy (`floor(N*k/9)`, `k=1..8`), each using the same top-left 45% × 25% crop, plus one empty negative. Canonical frame PTS, proxy/source references, PNG hashes, actual model hashes, raw float32 tensors, decoded boxes and text are preserved. No rally or score annotations were loaded.

The table describes one call per fixed input, including one first call and the empty negative. These are component-call distributions, not production OCR cadence, locked-ROI performance or a whole-video throughput estimate. Linear-interpolated P95 over 25 observations has a small-sample limitation.

| OCR configuration | Call count | p50 ms | p95 ms | Model/session loading seconds |
|---|---:|---:|---:|---:|
| CUDA, package-default threads | 25 | 8,431.106 | 10,289.992 | 0.881 |
| CPU, explicit four intra/inter threads | 25 | 1,388.176 | 1,500.070 | 0.406 |
| CPU, package-default threads | 25 | 658.362 | 1,041.115 | 0.541 |

CPU/default threads is fastest in these probes. Four threads is an explicit resource-bound alternative with greater observed call latency. The loader's default threading behavior remains unchanged. The experimental full-video configuration explicitly requests `onnx-cpu` and leaves its thread parameter unset; it does not silently fall back from a configured CUDA backend.

Decoded-output agreement is strong on these inputs, while raw numerical equivalence is limited:

| CUDA versus either CPU arm | Result |
|---|---:|
| Identical decoded text sequences | 25/25 |
| Identical decoded boxes | 25/25 |
| Identical score rows and abstentions | 25/25 |
| Entire parsed reading dictionaries identical | 24/25 |
| Raw array comparison passing original `rtol=1e-4, atol=1e-4` gate | 11/25 |
| Maximum absolute raw tensor difference | 0.0003359914 (CPU/four); 0.0003378093 (CPU/default) |
| Detector mask pixels crossing the unchanged 0.3 threshold | 9 |
| Classification/recognition argmax disagreements | 0 |
| Maximum difference in rounded text confidence | 0.00004 |

The one parsed-dictionary difference is the minimum reading confidence, 0.86225 versus 0.86224, with identical rows and values. All 14 failed raw-array tolerance cases remain recorded; the tolerance was not relaxed. Borderline detector pixels and class/recognition peak checks are retained in both comparison JSON files. This sample does not prove general backend equivalence, text accuracy or score-sequence accuracy.

The corrected parser produces coherent observations on 4/8 Test1, 5/8 Test2 and 6/8 Test7 uniform crops and abstains on the others, including the empty negative. Those are model-observation coverage counts, not accuracy. The generic parser repair prevents a broadcaster logo from borrowing numeric fields across an intervening athlete name. On original Test2 frame22924, the model omitted the top current digit9; the parser now abstains rather than interpreting the completed-game21 as current or returning `SXFI`/`LIVE` as competitors. Complete compatible fields retain the actual observed name rows and exclude the logo from ROI bounds. No missing digit is reconstructed.

A separate original-Test2 placement probe recorded CUDA execution for the OCR detector/classifier and most recognizer nodes, plus a small CPU shape partition. Its recognizer profiles accumulate approximately14.145 seconds in CUDA `Conv` kernel events out of14.188 seconds of recognizer kernel-event durations across two calls. These sums are not wall-time fractions, critical-path latency or GPU utilization. The recorded cost is not explained by whole-model CPU fallback. One-thread CUDA and `HEURISTIC` convolution-search probes did not remove the several-second fixed-input cost. The exact low-level cause of slow convolution on this Pascal/ORT/cuDNN combination remains unproved; dynamic-shape recompilation and CPU oversubscription were not established as causes. The package's unchanged detector preprocessing expands the576×180 crop to2368×736; no preprocessing or model replacement was selected.

CPU/GPU experiments ran serially by backend on a shared host in fixed CUDA → CPU/four → CPU/default order. Order, host cache state and thermal/clock history were not counterbalanced. Other CPU research work was present; a 4.31-second focused OCR test overlapped late CPU/four-thread samples, and raw-output comparison overlapped early CPU/default samples. These limitations are preserved explicitly. The observed component latency difference justifies a full-video experiment, not a controlled end-to-end speed claim.

Evidence and reproduction:

- [OCR repair report](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/OCR_REPAIR_REPORT_v2.md), [summary](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/ocr_summary_v2.json), [exact commands](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/OCR_REPRODUCTION.sh).
- [CUDA/CPU default comparison](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/ocr_cuda_cpuauto_comparison_v1.json), [CUDA/CPU four-thread comparison](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/ocr_cuda_cpu4_comparison_v1.json).
- [Hash verification](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/ocr_verification_v2.json): 75 input/raw-array pairs and the actual staged model hashes checked.
- [Final forwarding receipt](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/ocr_forwarding_receipt_v1.json): 71 OCR tests passed, including absent/configured thread forwarding and real rendered-board inference.
- [Original Test2 OCR node-placement evidence](/home/administrator/Desktop/sport-analytics/Sports_Analytics/artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/ort_ocr_node_probe_v1/report.json): fixed actual source input, profiles and stated scope; unchanged historical artifacts.

## Tracker and pose diagnostics on common inputs

A separate bounded experiment ran fresh RF-DETR on480 actual canonical proxy frames: two uniformly positioned120-frame windows per Test1, Test2, prepared doubles and amateur recording, with one detector update per two frames. It preserved every actual input PNG, BGR hash, ORT input tensor, raw output tensor, decoded person box/score, timestamp and model hash. All four trackers consume the exact same saved detector rows. These are raw person detections, rather than tracker estimates relabeled as detections.

The experiment uses full images and retains spectators, officials and people on other courts. It does not measure target-court detection recall, named identity, team membership or doubles completeness. Amateur original VFR15-to-proxy30 source mapping remains unaudited; the recorded frame/PTS contract is explicitly the actual canonical proxy. Each tracker repeats exactly three times, yielding1,440 measured updates per implementation and identical replay output within that implementation.

| Tracker | p50 update ms | p95 update ms | Anonymous local track episodes |
|---|---:|---:|---:|
| ByteTrack | 0.867 | 1.224 | 100 |
| OC-SORT | 1.210 | 1.804 | 102 |
| BoT-SORT, CMC disabled | 1.672 | 2.395 | 104 |
| C-BIoU | 1.727 | 2.419 | 103 |

Common declared settings use elapsed timestamps, a one-second lost-track buffer, minimum consecutive updates1, high-confidence threshold0.5, and activation threshold0.4 where supported. Other family defaults remain distinct and recorded. No ReID model is used; BoT-SORT camera-motion compensation is explicitly disabled and C-BIoU already disables it. Parameters were not selected against labels. The comparison excludes detector inference and input/output serialization from tracker-update timing. Episode counts and current-detection geometric overlap are technical diagnostics; fewer episodes do not prove fewer physical identity switches. HOTA and IDF1 are unavailable without independently reviewed person/identity truth. No tracker is promoted.

RTMPose-M and the `rtmpose_x_halpe26` alias were then run on the same32 observed boxes across eight source frames. Each measured adapter call contains **four sequential person crops**, with one neural forward per crop; it is not a four-person GPU batch:

| Pose adapter | Actual network input per crop | Actual per-person output | First call with four sequential crops ms | Remaining seven such calls, p50 ms |
|---|---|---|---:|---:|
| RTMPose-M body7 | 3×256×192 | 17×3 | 114.763 | 24.564 |
| X alias, documented body7 placeholder | 3×384×288 | 17×3 | 193.627 | 62.880 |

Both models returned finite outputs on all32 common boxes. The output joint axis is symbolic in static ONNX metadata; the17-joint count is established by actual inference. The X manifest already states that the alias uses a body7 placeholder pending a heel/toe export. Its exporter detail references a COCO configuration and contains a stale192×256 claimed input shape; actual ONNX metadata and the executed adapter use384×288. No manifest was edited. This is not a26-joint heel/toe accuracy result. Pose PCK, wrist/ankle/contact/jump accuracy and player attribution remain unvalidated.

The installed `rtmlib.RTMPose.__call__` loops over `bboxes`, running preprocessing, `self.inference(img)` and postprocessing once per person. `BaseTool.inference` constructs a `1×3×H×W` float32 tensor for each iteration. The active `PoseEstimator` forwards the list of boxes to this loop; it does not implement GPU batching. The profile's `pose.batch=2` field is not forwarded or used by this active adapter and must not be reported as executed batch2. This is a performance limitation to investigate separately after the current freeze, with common-input output comparisons before changing execution.

The [installed-source audit](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/pose_sequential_execution_audit_v1.json) records package version0.0.16, the inspected method source and module hashes. Current installed `rtmpose.py` SHA256 is `98b37228b3ff2a705d856e139486992d2c1f2124d805cf5db5a97bf295ed4e97`; `tools/base.py` SHA256 is `0d287088838eee78cc8cb5ef722a53148f7c100bf73eed16457ce3f9f40b272a`. This was a read-only source inspection with no new model, session or GPU forward, rather than added runtime batching instrumentation. Original probe results remain unchanged; their timing scope is clarified here.

The detector/pose extraction took108.604 seconds including evidence capture; that duration includes PNG/tensor serialization and source/model setup and must not be presented as production throughput. These are shared-host component diagnostics. [The detailed report](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/TRACKER_POSE_COMPONENT_COMPARISON.md), [per-video diagnostics and verification](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/tracker_component_report_v1.json), [fresh input manifest](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/tracker_components_v1/inputs_manifest.json), [tracker comparison](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/tracker_components_comparison_v1/comparison.json), and [source contact sheet](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/tracker_source_contact_sheet_v1.jpg) retain the evidence. Seven focused harness tests and changed research-file Ruff checks passed. Installed package source/version/license receipts remain separate from model/data license declarations.

## Experimental configuration and completed measurements

The application profile [gpu-rtx4000.yaml](/home/administrator/Desktop/sport-analytics/Sports_Analytics/config/profiles/gpu-rtx4000.yaml) is unchanged. The repair experiments use the separate [experimental-pipeline-repair-v1.yaml](/home/administrator/Desktop/sport-analytics/Sports_Analytics/config/profiles/experimental-pipeline-repair-v1.yaml), whose source SHA256 is `280cbf717568fa2a7a1c3b476921bac1b48e9958bf65be0469fae7b5b2dae756`. Each protocol retains its resolved YAML, model/config/source hashes, source probe, session input, executed source and dirty-tree receipt. Passive peak/player diagnostics are uniformly bounded; all-frame raw/association caches remain enabled. No annotation or previous session state is supplied to the inference worker.

The experimental profile explicitly requests Torch/CUDA FP16 TrackNetV3, actual FP32 RF-DETR/RTMPose ONNX graphs, CPU RapidOCR with default threading, ByteTrack, observed-evidence rally reasoning and the selected detector/layout content-continuity provider. It does not enable TensorRT or claim that unavailable optional components ran. Completed `execution_backends` and degradation receipts must confirm the actual loaded stages; a YAML declaration is insufficient.

| Recording | Source frames | Source duration | Source video | Run state | Worker/executor seconds | Throughput | Peak memory |
|---|---:|---:|---|---|---|---|---|
| Test1 | 17,268 | 575.600 s | 1920×1080,30/1fps,`1/15360` timebase | Coverage proven after original GPU0 worker/report failure | Parent failure-inclusive2,037.224s; worker/NN-only unavailable | 8.476sourceFPS on that parent scope | Sampled worker GPU2,126MiB; tree RSS3,068,030,976bytes |
| Test2 | 29,296 | 976.533333 s | 1920×1080,30/1fps,`1/15360` timebase | Coverage proven after original GPU1 reporting failure | Parent failure-inclusive3,643.507s; worker/NN-only unavailable | 8.041sourceFPS on that parent scope | Sampled worker GPU2,122MiB; tree RSS3,052,724,224bytes |
| India prepared clip | 4,800 | 160.000 s | 1280×720,30fps | Normal completed worker/parent, GPU0 | Worker467.405s / parent473.367s | Worker10.269 / parent10.140FPS | Sampled worker GPU2,128MiB; tree RSS2,761,273,344bytes |
| Doubles prepared clip | 3,600 | 120.000 s | 1280×720,30fps | Normal completed worker/parent, GPU1 | Worker363.928s / parent370.173s | Worker9.892 / parent9.725FPS | Sampled worker GPU2,132MiB; tree RSS2,747,203,584bytes |
| Test7 | 10,725 | 357.500 s | 1920×1080,30/1fps,`1/15360` timebase | Normal completed worker/parent, GPU0 | Worker1269.123s / parent1277.470s | Worker8.451 / parent8.396FPS | Sampled worker GPU2,122MiB; tree RSS2,836,393,984bytes |
| Denmark prepared clip | 3,300 | 110.000 s | 1280×720,30fps | Normal completed worker/parent, GPU0 | Worker294.168s / parent299.745s | Worker11.218 / parent11.009FPS | Sampled worker GPU2,122MiB; tree RSS2,725,707,776bytes |

Posthoc proofs verify Test1's17,268frames/frontier17,267/288chunks and Test2's29,296frames/frontier29,295/489chunks, both on1280×720 analysis proxies. Normal parent guards verify India's4,800frames/frontier4,799/80chunks and doubles'3,600frames/frontier3,599/60chunks. Normal Test7 verifies10,725frames/frontier10,724/179chunks and Denmark3,300frames/frontier3,299/55chunks; the extra amateur run is interrupted and excluded from completed-run results. Source/proxy timestamps, tail coverage, fresh-cache status and source/model guards require their own proofs; a source probe or progress percentage is insufficient.

Original Test1/Test2 protocols are `protocol_test1_v2/` and `protocol_test2_v2/`; their closed run roots are `fresh_test1_v1/` and `fresh_test2_v1/` under `../pipeline-repair-runs-20261105/`. Normal India/doubles use their recorded `protocol_india_v2/` and `protocol_doubles_v2/` plans. Test7 completed `protocol_test7_v3/`; Denmark completed `protocol_denmark_v2/`; interrupted amateur used `protocol_amateur_v2/`. Test1/Test2 shared CPU, RAM and storage on separate GPUs. Subsequent pairings have different concurrency contexts. These conditions, together with duration, content, resolution, FPS, cadence, source revisions and diagnostics, must accompany any comparison with frozen historical runs. Historical performance numbers are not substituted for the pending cells.

## Verified full-run measurements and receipt scopes

[technical_analysis.json](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/analysis_test1_v1/technical_analysis.json) is read-only analysis after [strict independent completion proof](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/completion_test1_v1/completion_receipt.json), whose recorded SHA256 is `45afa92ab692534a132ef9732e684b1cf5c7b1efc4a6dd82239c7e43887ea712`. It preserves the original partial/failed parent status and worker exit1. The catalogue20/21 mismatch occurred after complete neural processing; posthoc decoding and source/cache verification are not fresh NN inference and do not turn the failed original receipt into success.

| Recorded scope | Seconds | Source frames/second |
|---|---:|---:|
| Repair Test1 parent, including final reporting failure | 2,037.2235298110172 | 8.476242173386769 |
| Frozen historical Test1 report | 1,794.3652807851322 | 9.6234585902687 |

The historical values come from the preserved [original inference report](/home/administrator/Desktop/sport-analytics/Sports_Analytics/artifacts/benchmarking/experiments/prod_20261105_fresh_association_scene_v1/inference.json). The repair observation is slower on these recorded clocks. It is **not a controlled regression estimate**: parent/worker endpoints, final failure work, source revisions, diagnostics, content policy and concurrent CPU/RAM/storage contention differ. The component OCR result cannot be translated into an end-to-end speedup by subtraction. Both descriptive rates are below the30FPS source clock; neither proves live or buffered real-time performance.

Actual saved stage-invocation samples provide the following distributions. Every row retains its invocation count and summed scope-frame population. These are multi-frame application invocations, not individual model forwards; a scope-frame population is not an exact neural-input frame count. View policy/cadence can omit a shuttle invocation while full cache/frame coverage remains complete.

| Run / stage | Calls | Scope-frame population | Total seconds | p50 invocation ms | p95 invocation ms |
|---|---:|---:|---:|---:|---:|
| test1 / `court` | 288 | 17,268 | 110.121 | 321.411 | 799.302 |
| test1 / `content_continuity_and_players` | 288 | 17,268 | 864.607 | 3313.882 | 3899.482 |
| test1 / `shuttle` | 288 | 17,268 | 256.244 | 827.320 | 1249.416 |
| test1 / `players` | 288 | 17,268 | 72.006 | 230.901 | 520.635 |
| test1 / `ocr` | 288 | 17,268 | 392.144 | 1277.346 | 2133.222 |
| test2 / `court` | 489 | 29,296 | 170.081 | 323.079 | 509.977 |
| test2 / `content_continuity_and_players` | 489 | 29,296 | 1509.989 | 3393.748 | 4099.433 |
| test2 / `shuttle` | 489 | 29,296 | 429.486 | 845.570 | 1157.774 |
| test2 / `players` | 489 | 29,296 | 143.980 | 277.370 | 595.891 |
| test2 / `ocr` | 489 | 29,296 | 587.194 | 1102.111 | 1716.329 |
| india / `court` | 80 | 4,800 | 22.487 | 241.960 | 594.153 |
| india / `content_continuity_and_players` | 80 | 4,800 | 197.062 | 3150.801 | 4672.262 |
| india / `shuttle` | 61 | 3,660 | 58.474 | 880.611 | 1432.470 |
| india / `players` | 80 | 4,800 | 13.373 | 123.856 | 484.237 |
| india / `ocr` | 80 | 4,800 | 96.950 | 1400.218 | 2340.424 |
| doubles / `court` | 60 | 3,600 | 33.087 | 394.408 | 1296.247 |
| doubles / `content_continuity_and_players` | 60 | 3,600 | 146.679 | 1794.883 | 6694.694 |
| doubles / `shuttle` | 39 | 2,340 | 34.068 | 815.378 | 1199.856 |
| doubles / `players` | 60 | 3,600 | 15.942 | 71.444 | 779.482 |
| doubles / `ocr` | 60 | 3,600 | 59.519 | 1326.360 | 2348.590 |
| test7 / `court` | 179 | 10,725 | 80.942 | 339.739 | 922.154 |
| test7 / `content_continuity_and_players` | 179 | 10,725 | 514.890 | 3325.637 | 4221.018 |
| test7 / `shuttle` | 177 | 10,605 | 153.919 | 831.824 | 1172.662 |
| test7 / `players` | 179 | 10,725 | 70.070 | 375.510 | 871.927 |
| test7 / `ocr` | 179 | 10,725 | 246.423 | 1396.250 | 1950.457 |
| denmark / `court` | 55 | 3,300 | 48.109 | 298.425 | 2633.039 |
| denmark / `content_continuity_and_players` | 55 | 3,300 | 84.294 | 1256.090 | 3958.149 |
| denmark / `shuttle` | 44 | 2,640 | 37.861 | 821.459 | 1094.643 |
| denmark / `players` | 55 | 3,300 | 8.460 | 90.137 | 390.260 |
| denmark / `ocr` | 55 | 3,300 | 54.128 | 1107.465 | 1900.790 |

Stage scopes may overlap and must not be summed to infer neural-only runtime. OCR samples contain the scheduled reads within each chunk; they are not the standalone one-crop benchmark denominator. Source-bound runtime declarations report TrackNet CUDA/FP16, CUDA+CPU provider registration for detector/pose, and the actual CPU OCR graph identities listed above. Those declarations do not substitute for full-run per-node profiling.

The985 parent resource rows contain no recorded sampling error. Sampled worker-PID GPU peak is2,126MiB on the allocated GPU0 UUID; sampled current-descendant tree RSS peaks at3,068,030,976bytes. The largest/last observed current-tree CPU counter is20,603.53seconds and minimum sampled system available RAM is98,946,695,168bytes. These CPU snapshots omit exited children and can decrease when descendants exit, so they are not final worker CPU usage or an exact utilization denominator. RSS can count shared pages twice; two-second samples can miss short peaks.

Original Test1/Test2 `inference.json` files were not written. Their neural-only throughput, isolated model loading, media-ready, model-staging, component initialization, final worker CPU seconds and worker maximum RSS remain **null/unavailable**. They are not reconstructed from stage residuals. Successful India/doubles/Test7/Denmark reports provide the separate startup/resource scopes below. The extra amateur run is interrupted and excluded from completed results.

### Test2 historical comparison and normal completed receipts

The [closed Test2 technical audit](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/analysis_test2_v1/technical_analysis.json) and its independent completion receipt preserve the original failed reporting status. Its parent process-loop observation is3,643.506590575911seconds, or8.04060573837725sourceFPS. The preserved [historical Test2 worker](/home/administrator/Desktop/sport-analytics/test2-runs-20261105/fresh_v1/inference.json) reports6,544.650143535808seconds and4.476327894919768FPS; the [historical parent](/home/administrator/Desktop/sport-analytics/test2-runs-20261105/fresh_v1.executor.json) reports6,554.687972566113seconds and4.4694728601292715FPS. Worker and parent clocks are kept separate.

Thus repair Test1 is descriptively slower than its historical observation while repair Test2 is descriptively faster. The historical Test2 primary/repeat workers shared the host with another Test2 run; repair Test1/Test2 shared it with different-duration recordings and CPU research work. Source revision, GPU index, OCR backend, diagnostics, policy, clock endpoints and concurrency differ. These are **not controlled end-to-end regression/improvement estimates**. The same25source-crop/model controls do demonstrate lower measured CPU OCR call latency with decoded-output agreement; that component result cannot be assigned the whole-video time difference.

Normal [India inference](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/fresh_india_v1/inference.json)/[parent](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/fresh_india_v1.executor.json) and [doubles inference](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/fresh_doubles_v1/inference.json)/[parent](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/fresh_doubles_v1.executor.json) both close successfully with worker exit0, fresh-cache flags, complete frontier, unchanged frozen source/model guards, matching worker-report hashes and parent-verified completion catalogues. Their stage sample hashes and distributions were independently checked for this report. India/doubles ran concurrently on separate GPUs while sharing CPU/RAM/storage. Their720p prepared sources and diagnostic density/view mix differ from full1080p-source Test1/Test2, so their rates do not measure a recording-independent speed gain.

Normal [Test7 inference](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/fresh_test7_v1/inference.json)/[parent](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/fresh_test7_v1.executor.json) now also verify worker exit0, complete frontier10,724, all179catalogued chunks, unchanged source/model guards and exact stage/report hashes. It ran on GPU0 alongside the ongoing amateur recording on GPU1. Denmark started on GPU0 after Test7 closed, concurrently with amateur on GPU1. Its [inference](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/fresh_denmark_v1/inference.json)/[parent](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/fresh_denmark_v1.executor.json) receipts now verify exit0, all3,300frames/frontier3,299, all55catalogued chunks, unchanged source/model guards and exact report/stage hashes. It is a110second720p30prepared recording, so its rate has a different content/resolution scope from full1080p-source Test1/Test2.

| Run | Worker seconds / FPS | Parent process-loop seconds / FPS |
|---|---:|---:|
| india | 467.405316567 / 10.269459567 | 473.367071498 / 10.140122305 |
| doubles | 363.928187861 / 9.892061456 | 370.172749590 / 9.725189129 |
| test7 | 1269.122724349 / 8.450719378 | 1277.469533006 / 8.395503550 |
| denmark | 294.168273602 / 11.218069031 | 299.744733260 / 11.009367751 |

The parent elapsed field is the launch/wait/sampling loop; parent source/model/catalogue verification can follow that clock. It is not a total including every post-close guard. Successful worker elapsed includes analysis/export and final worker checks; model staging and runner construction precede it. Time scopes remain descriptive rather than interchangeable.

| Run | Media-ready s | Model staging s | Component initialization including model constructors s | Decode/perception/cache parent scope s | Completion-catalogue validation s |
|---|---:|---:|---:|---:|---:|
| test1 | unavailable | unavailable | unavailable | unavailable | unavailable |
| test2 | unavailable | unavailable | unavailable | unavailable | unavailable |
| india | 1.373374 | 2.075371 | 8.944497 | 428.046783 | 1.365833 |
| doubles | 1.374420 | 2.099583 | 8.876373 | 327.503690 | 1.528902 |
| test7 | 1.951184 | 1.991410 | 9.494732 | 1144.578295 | 2.929130 |
| denmark | 1.337909 | 1.999680 | 9.037008 | 263.579183 | 1.178753 |

Staging is file/registry preparation, not model inference or isolated model loading. Component initialization depends on the selected profile and includes constructors/available model loading; lazy first-forward library/algorithm setup can occur later in stage calls. Media-ready timing can overlap later asynchronous transcode work. Parent scopes overlap subordinate scopes; totals must not be summed. **Isolated decode, preprocessing, detector inference, tracking, pose inference, racket, contact, stroke, rally FSM, analytics, serialization, export and neural-only throughput remain null, not zero**, in the machine-readable summary.

| Run | PID/GPU samples | Errors | Sampled worker GPU peak MiB | Sampled tree RSS peak bytes | Final worker max RSS bytes | Final worker CPU seconds |
|---|---:|---:|---:|---:|---:|---:|
| test1 | 985 | 0 | 2126 | 3068030976 | unavailable | unavailable |
| test2 | 1761 | 0 | 2122 | 3052724224 | unavailable | unavailable |
| india | 229 | 0 | 2128 | 2761273344 | 2785234944 | 4454.848907 |
| doubles | 179 | 0 | 2132 | 2747203584 | 2756665344 | 2916.797843 |
| test7 | 618 | 0 | 2122 | 2836393984 | 2829647872 | 12432.324331 |
| denmark | 145 | 0 | 2122 | 2725707776 | 2758156288 | 2791.790194 |

The allocated GPU UUID and exact worker PID select GPU-memory rows. Current-tree RSS/CPU include only descendants still present; RSS can count shared pages twice and CPU counters can decrease after children exit. Final `resource` values refer to the worker process, not its full historical child tree. Two-second samples miss short peaks. Test2's maximum/last observed current-tree CPU counter is35,651.46seconds and its minimum available-system-RAM observation is98,115,715,072bytes; these are not final worker CPU or attributable per-run system RAM use. Normal India/doubles final worker CPU values above are measured, while no CPU-utilization percentage is inferred from incompatible scopes.

| Run | Logical bytes | Allocated bytes | Staged-model bytes | Perception-cache bytes |
|---|---:|---:|---:|---:|
| test1 | 714,102,123 | 717,713,408 | 361,041,769 | 72,971,704 |
| test2 | 1,016,628,907 | 1,022,640,128 | 361,041,769 | 119,192,401 |
| india | 502,023,237 | 503,029,760 | 361,041,769 | 21,985,337 |
| doubles | 487,817,147 | 488,570,880 | 361,041,769 | 20,828,502 |
| test7 | 591,504,305 | 593,850,368 | 361,041,769 | 49,574,950 |
| denmark | 466,235,404 | 466,903,040 | 361,041,769 | 15,556,493 |

Disk totals are the recorded regular-file/stat scopes, not deduplicated physical-storage requirements across runs. Actual runtime declarations for all six recordings preserve Torch/CUDA FP16 shuttle, ONNX CUDA+CPU provider registration for detector/pose, and RapidOCR3.10.0 CPU-only stages with the graph hashes above. Optional degradation is retained; a selected alias does not prove an unavailable stage ran. Same-artifact bounded probes establish FP32 ONNX image tensors, but no new full-run node-placement or accumulator-precision measurement exists. Those unavailable fields remain null rather than being inferred from provider registration.

[performance_cross_run_v3.json](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/performance_cross_run_v3.json) preserves all six scope-qualified run records, stage denominators/min/max/p50/p95, disk/resources, model/runtime declarations, explicit unmeasured-stage nulls and source/proxy/profile/plan/receipt/sample hashes. Its [read-only extractor](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/performance_cross_run_v3.py) recomputed saved stage distributions and checked normal worker/parent/catalogue bindings. It opens no original SQLite and performs no NN inference. Later closed results will be appended as new artifact versions; these receipts are preserved.

## Separate PySceneDetect candidate signal probe

Actual [PySceneDetect v0.7.2 source](https://github.com/Breakthrough/PySceneDetect/tree/7cd1005e8349d8e913d0930fc1750363eb4ddc51), pinned commit `7cd1005e8349d8e913d0930fc1750363eb4ddc51`, was imported outside the repository without installation or GPU/model work. BSD-3-Clause source/license hashes are retained. Stock ContentDetector27/minimum scene15 and AdaptiveDetector3/minimum content15/window2/minimum scene15 processed968 exact frames from eight prespecified Test1/Test2 windows; every target has60 preceding/following frames. Both emitted zero alarms anywhere in those windows. Target HSV scores2.325–10.647 stayed below both stock content floors. No threshold was fitted or candidate adopted.

| Direct detector API scope | Calls | p50 ms | p95 ms |
|---|---:|---:|---:|
| Stock ContentDetector | 968 | 16.794 | 19.223 |
| Stock AdaptiveDetector | 968 | 16.180 | 17.762 |
| Local raw observer v1 | 968 | 15.651 | 17.570 |
| Local raw observer v2 | 968 | 15.292 | 17.034 |

All receive identical1280×720BGR source arrays; local observers internally resize to480wide and additionally use recorded prior player/view/shot context. The library's SceneManager automatic downscaling is not used. OpenCV has one thread, call order is fixed and the host is shared. Adaptive uses two future frames and stock filtering can delay emission. These are signal/runtime diagnostics, not an identical-information accuracy test or a production-throughput comparison.

The local v2 replay detects the two selected Test1 targets and suppresses7703/23639, but lacks target hypotheses at4257/5174/14107/11346 under this bounded reset and original baseline-player state. Additional alarms, including23697, remain in the evidence. This does not establish the current full repaired pipeline's barrier decisions. Prior target characterizations are exposed agent/source diagnostics, not exhaustive independent scene truth; precision/recall and a cut oracle are not inferred. [Full report](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/pyscenedetect_probe_v1/report.json), [summary](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/pyscenedetect_probe_v1/SUMMARY.md) and [hash verification](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/pyscenedetect_probe_v1/verification.json) preserve all windows, stock defaults, delayed emissions and source/cache/PNG provenance.

## Measurement contract for the completed-run follow-up

The new worker observes each existing perception `_rate` invocation without rescheduling its work. `stage_latency_samples.json` retains the exact wall-time observations and frame population per invocation. `inference.json` binds it with `stage_latency_samples_sha256` and contains `perception_stage_latency` with count, total, p50/p95, minimum and maximum. The source-frozen [instrumentation helper](/home/administrator/Desktop/sport-analytics/Sports_Analytics/research/pipeline_repair_performance.py) explicitly describes its scope.

Additional [device-wide telemetry metadata](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/device_utilization_v1.metadata.json) and [samples](/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105/device_utilization_v1.jsonl) cover GPU/memory utilization, memory use, power, temperature and clocks from `2026-11-05T16:41:10.983363Z` (22:11:10.983363 Asia/Kolkata). This auxiliary monitor started after the first workers launched, so it misses their cold starts. It complements the parent worker/PID CPU/RSS/GPU-memory samples; it does not replace their broader time coverage. Device-wide measurements cannot automatically be attributed to one worker or one stage, and its separate closed receipt is retained after the user scope stop.

These are **application stage-invocation wall times**, rather than individual neural forwards, per-source-frame service times or CUDA-event kernel latencies. A stage may cover a multi-frame chunk, multiple neural calls or no neural call because of cadence/view policy. OCR chunk timing can include multiple eligible reads or none. For the selected foreground-content provider, detector/tracking/pose work is included in `content_continuity_and_players`; the later `players` scope also assembles frame/association evidence. Label names alone do not isolate model execution cost.

Parent scopes overlap: `decode_perception_cache_s` contains subordinate perception work; initialization includes model loading; media preparation can overlap background transcoding. Stage values must not be added to reconstruct total runtime. The recorder wraps completed existing scopes; it does not change cadence, thresholds or numerical results. Per-invocation p50/p95 must retain their call/frame denominators and cannot be compared directly with the standalone per-OCR-call or per-tracker-update tables.

The final audit will use completed worker **and** parent executor receipts, verify the worker-report hash and unchanged source/model inputs, and then retain:

- For normal successful workers, time measured from before media preparation through analysis/export, final catalogue/source/proxy checks and input verification, alongside the parent process-loop clock (post-close parent guards can follow it). Model staging and runner construction precede the timer; final JSON serialization follows its last update. The worker updates `elapsed_s` again after its initial result-dictionary construction. `frames/elapsed` must identify which denominator was used. Failed Test1/Test2 have no final worker time.
- Actual processed frame count, final frontier, source/proxy metadata and timestamps, configured and loaded providers, actual graph/tensor types, model/session initialization scope, stage latency samples and their hash.
- Successful-worker final `resource` CPU seconds and maximum RSS are refreshed with the last elapsed-time update, before final JSON writing; these final fields are unavailable for the failed Test1 worker. Nominal two-second `/proc` samples cover the worker and its current descendants. Tree RSS can double-count shared pages; exited children and short peaks can be absent. Sampled tree CPU deltas require matching elapsed-time and host-capacity denominators before being called utilization.
- GPU samples selected by the completed worker's exact PID **and** allocated UUID. Device total memory, another process's allocation and Torch allocator statistics are different quantities. Two-second samples are sampled maxima, not guaranteed continuous peaks or per-stage attribution.
- Logical versus allocated cache/model/artifact sizes, errors/failed samples, source-frame coverage, completion stability and the concurrency context. Preserved bounded diagnostic windows do not imply dense reviewed perception truth.

No new worker, profile, model, performance-helper or production-source edit is permitted during a guarded run. Read-only analysis and this documentation do not add GPU jobs. The Test1/Test2 failure-inclusive measurements are verified posthoc, and India/doubles/Test7/Denmark have normal closed receipts; interrupted or unavailable fields remain excluded and are not extrapolated. Sporting accuracy, controlled performance differences and generalization remain separate evaluation questions.
