# Existing-model GPU runtime and provider-placement probe

Date:2026-11-05. Branch:`Benchmarking`; executor HEAD:`181cb917dd923524c48772b55ecc71a49ae68518` with the ongoing scoped production-readiness work uncommitted. This is a small model-level diagnostic, not a new full-video benchmark or a production-promotion result.

The allocated GPU1 successfully executed the existing RF-DETR-small, RTMPose-M and TrackNetV3 artifacts. ORT's executed-node profiles distinguish actual CUDA placement from registered provider names. Torch hooks distinguish actual network tensor precision from the final NumPy export type. No weights, environment, deployments or application profiles were changed; no model was downloaded, installed, converted or exported.

## Machine and isolation evidence

Initial `nvidia-smi` inspection found two NVIDIA GeForce GTX1080Ti cards, each11,264MiB, driver580.178.04, compute capability6.1. GPU0 used74MiB and GPU1 used7MiB; neither had a compute process. The workspace also had a CPU scene diagnostic at the initial inspection. CPU scheduling was not isolated or continuously attributed to peer processes, so these timings cannot establish dedicated-machine CPU performance.

The successful probe set `CUDA_VISIBLE_DEVICES=1` inside its own process. Its logical`cuda:0` properties report UUID`a618f090-66bf-ad80-b0a5-0c91bee61fab`, matching physical GPU1 UUID`GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab`. Only one Torch device was visible. The tool checked GPU1 for foreign compute PIDs and the host for the full-pipeline experiment runner before every model forward. Resource samples report no foreign GPU1 PIDs. No full-pipeline job overlapped these probes, and both cards returned to their initial idle memory levels afterward. Unrelated processes were preserved.

Measured environment:

| Item | Actual value |
| --- | --- |
| Python |3.12.12 |
| Torch |2.14.1+cu126 |
| Torch CUDA build |12.6 |
| cuDNN reported by Torch |91002 |
| ORT |1.29.0 |
| ORT advertised providers |TensorRT, CUDA, CPU |
| Requested ORT provider sequence |CUDA with production HEURISTIC cuDNN algorithm search, then CPU |
| ORT probe threads |Two intra-op, one inter-op; explicit bounded probe configuration |
| Torch CPU threads |Two in this probe process |
| Torch cuDNN benchmark |false |
| Float32 matmul precision setting |highest |

TensorRT was advertised by ORT but was neither requested nor validated. Provider availability alone does not show a working TensorRT engine, supported target architecture, TensorRT precision or actual graph placement. The CUDA provider reports`use_tf32=1` among its options; that option is not evidence that these cards executed TF32 or any particular hardware arithmetic unit.

## Reproduction, artifacts and input scope

```sh
source ../gpu-env.sh
.venv/bin/python research/production_runtime_probe.py \
  --output artifacts/benchmarking/experiments/NEW_runtime_gpu1 \
  --gpu-index 1 --warm-count 5 --source-frame 12760
```

The tool refuses an existing output directory, enforces GPU1 allocation, uses only existing files and fails on a model digest mismatch or loss of isolation. Exact executed source bytes, source/config/model/input hashes, raw ORT profiles, node summaries, resource samples and model heatmaps are retained in:

`artifacts/benchmarking/experiments/prod_20261105_runtime_gpu1_v2/`.

Its executed script SHA-256 is`63812406baa68f4a2a141c0ae65fa9179c1640d5ceaf09e3e5068763e1d94c63`; its source guard passed. The external log is`prod_20261105_runtime_gpu1_v2.log`. First attempt`v1` stopped before any model execution because optional`psutil` was absent. No dependency was installed: the successful implementation uses standard-library`/proc` and`resource`, plus already-installed NVML. The failed log is preserved as`prod_20261105_runtime_gpu1_v1.log`.

Source video SHA-256 is the immutable Test1 hash`877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6`. The probe decodes exact PTS for original frames12760–12767 and verifies the30FPS mapping. It does not read ground-truth labels.

RF-DETR receives one whole original frame through the existing RGB512×512 normalization; this is not the production court ROI. RTMPose receives one fixed original-image crop through the existing RGB affine/normalization method. That crop is a diagnostic input, not a labelled player box. ONNX session inference excludes frame decoding, input preprocessing and output postprocessing.

TrackNet uses the real eight-frame window, the existing local background preprocessing and the existing production`_forward`. Its input is`[1,27,288,512]` and output`[1,8,288,512]`. The background has only this local eight-frame initialization, so no parity with a long-running production background is implied. Torch forward timings include input transfer and conversion to the exported FP32 CPU array, with CUDA synchronization around each call. No benchmark annotation or contact timestamp influences any inference result.

## Model integrity and recorded rights

| Artifact | SHA-256 | Existing local registry record |
| --- | --- | --- |
| RF-DETR-small ONNX |`fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e` |Apache-2.0; ONNX export mirror |
| RTMPose-M extracted ONNX graph |`5c0a4bf67953e6d2ac43ce15e77dc9d5d354ae18430a47d2c5963a7bc5683e3c` |Apache-2.0, MMPose RTMPose |
| RTMPose-M source archive |`f7fbb6c5c11a1bb70f3d445e4ddec5d144ea89ad5649c081ef976f9b24a0b741` |Verified existing extraction manifest/registry lock |
| TrackNetV3 checkpoint |`df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a` |MIT code/checkpoints; HF mirror of the official release |

All digests match the existing lock or verified extraction manifest. These are preserved local registry declarations, not a new legal clearance of mirror, training-data or video-distribution rights. No new third-party model/code adoption occurred. Optional ReID, OCR, InpaintNet, alternative detectors, TensorRT and other model/device combinations were not profiled here.

## Executed ORT node placement

Each model ran one initial forward followed by five repeated fixed-input forwards under ORT profiling. The parser counts only complete`Node/*_kernel_time` events, avoiding fence/session double counting. It reports provider, optimized-node identity, operation and observed tensor metadata. All5,670 recorded node events have explicit provider metadata.

| Model | CUDA-assigned optimized nodes | CPU-assigned optimized nodes | CUDA node events | CPU node events |
| --- | ---: | ---: | ---: | ---: |
| RF-DETR-small |758 |0 |4,548 |0 |
| RTMPose-M |185 |2 |1,110 |12 |

RTMPose CPU nodes are`Slice_209` (index207) and`Concat_211` (index208). The raw profile identifies their inputs/outputs as tiny`int64` shape tensors, not floating image convolutions. Across the six forwards, their summed profiled durations are72µs and76µs respectively. CUDA-assigned operations include the convolution and matrix-multiplication operators. No node changed provider across these repeated inputs.

CPU provider registration therefore does not imply whole-model CPU fallback; RTMPose has a real small CPU partition. Conversely, the RF-DETR result proves CUDA provider placement for this optimized graph/input, not that every host-side reshape or launch uses a physical GPU compute kernel. Summed ORT node durations are **not** wall-time fractions, GPU utilization or critical-path latency. These profiles do not prove placement for every dynamic shape or later provider/session configuration. No named Memcpy kernel events appeared; host/device transfers still occur and are not disproved by that absence.

Both ONNX models have FP32 graph inputs/outputs and output arrays. Observed profile tensor types are`float` plus shape/control`int64` (and RF-DETR`bool`). That evidence does not prove accumulator precision or hardware execution units.

## Limited runtime measurements

All values below are milliseconds. ORT profiling overhead is included. Setup is model/session-instance initialization after libraries and source inputs are available; it is not a cold machine, process, filesystem or driver measurement. Warm samples repeat the same input five times. Tiny-sample P95 is linear interpolation of the five observations, not a stable tail-latency estimate.

| Model/configuration | Setup | First forward | Warm mean | Warm median | Warm min–max | Warm P95 |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| RF-DETR-small CUDA/FP32 tensors |419.161 |268.299 |18.375 |18.328 |18.270–18.612 |18.561 |
| RTMPose-M CUDA + CPU shape partition |99.757 |94.785 |5.394 |5.383 |5.206–5.648 |5.599 |
| TrackNet CUDA/FP16 |896.352 |50.740 |26.945 |27.877 |25.163–28.337 |28.279 |
| TrackNet CUDA/FP32 |852.366 |23.398 |21.596 |21.564 |21.451–21.715 |21.710 |

TrackNet FP32 is faster in this particular fixed-order, five-sample probe. FP16 ran first and FP32 afterward; thermal/clock/library state, order and CPU scheduling are not controlled as independent factors. This result does not justify changing the production precision default or predicting a full-video speedup. A precision experiment would require repeated randomized or counterbalanced trials, appropriate unprofiled timing, actual production batches/cadence and all observation/boundary/analytics comparisons.

Every repeated fixed-input output hash was identical within its own model/configuration. That is limited within-process repeatability, not cross-run determinism. TrackNet parameters, network input and network output were actually on logical`cuda:0`, with FP16 in the FP16 arm and FP32 in the FP32 arm; both exported NumPy arrays were FP32. This prevents the FP32 export from being mistaken for FP32 internal execution.

The two TrackNet arms used the exact same input tensor bytes. Both heatmap arrays are finite; maximum absolute difference is.000473097 and mean absolute difference.00000637736. These are numerical differences on one input, not measured localization/contact/rally accuracy. No precision-change candidate was promoted.

## Resource measurements and limits

NVML/PID monitoring used a nominal50ms interval; actual elapsed sample times are preserved. The table gives **sampled maxima**, including model setup and a few forwards, not continuous peaks or steady-state production requirements. PID RSS accumulates process/library state from earlier sequential arms. CPU seconds include this probe's monitor and runtime threads; CPU fractions cannot be inferred without the scope/host capacity.

| Model/configuration | Samples | PID RSS MiB | PID GPU MiB | Device GPU MiB | CPU seconds | Sampled GPU utilization max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RF-DETR-small |19 |1,192.50 |416 |523.56 |1.520 |28% |
| RTMPose-M |11 |1,240.86 |294 |401.56 |.642 |12% |
| TrackNet FP16 |35 |1,420.97 |578 |685.56 |2.132 |46% |
| TrackNet FP32 |33 |1,498.21 |630 |737.56 |1.938 |37% |

Torch allocator peaks independently report302,653,952allocated/438,304,768reserved bytes for FP16 and375,054,336allocated/492,830,720reserved bytes for FP32. These exclude non-Torch driver/ORT allocations. Device memory, process memory and allocator memory are different measurements; none is substituted for another. Short bursts and coarse device utilization counters prevent a utilization/occupancy bottleneck conclusion. No full-pipeline frames-per-second or resource reduction is calculated from these microbenchmarks.

## Software controls and remaining work

`research/tests/test_production_runtime_probe.py` passes17 tests. Controls cover repeated nodes versus unique nodes, CPU partitions, fence exclusion, transfer-versus-compute events, unknown/missing providers, per-node provider changes, invalid durations, absent kernel evidence, dtype metadata, empty denominators and exact small-sample latency/P95 arithmetic. Red and final green logs are preserved. Both changed Python files pass Ruff lint and format checks. GPU/model execution is a separately recorded real-artifact diagnostic, not mocked evidence from these parser tests.

The probe resolves the previously unmeasured **limited existing-model placement and tensor precision** question. It does not measure complete-pipeline stage attribution, decode/I/O overlap, detector/pose cadence, OCR cost, tracking/racket/scene/contact/FSM/export time, reconstruction, live latency, production concurrency or independent repeat throughput. It does not establish any sporting accuracy or generalization. The previously preserved full-video runtime remains the valid full-pipeline measurement for its recorded source/configuration; this new diagnostic must not be substituted for it.

## Completed full-pipeline Test1 measurements

The later source-frozen production runs below supersede the earlier statement that no new whole-video timing was available. Perception/event production source is commit `1308250`, with executed harness/source freeze `8599325`. Both processed all17,268 frames to frontier17,267. Two workers ran concurrently on separate physical GPUs and shared CPU/IO, so the pair is not an isolated speed or precision comparison.

| Arm | Elapsed s | FPS | Peak sampled PID RSS MiB | Peak sampled PID GPU MiB | Mean PID CPU % |
| --- | ---: | ---: | ---: | ---: | ---: |
| association | 1649.780 | 10.466851 | 2954.27 | 2888 | 423.40 |
| association_scene | 1794.365 | 9.623459 | 2770.38 | 2894 | 590.21 |

`prod_20261105_fresh_association_v1/inference.json` retains backend/dtype/degradation, resource samples, allocation UUID and per-stage wall time. Stage aggregates overlap:

```json
{
  "media_ready_wall_seconds": 2.242285348009318,
  "court_scene_wall_seconds": 113.38094055978581,
  "decode_perception_cache_wall_seconds": 1454.6699708402157,
  "semantic_ingest_wall_seconds": 73.48173029487953,
  "perception_court": 106.75754411472008,
  "perception_shuttle": 260.7417593547143,
  "perception_players": 629.5642446638085,
  "perception_ocr": 338.78333888109773
}
```

`prod_20261105_fresh_association_scene_v1/inference.json` retains backend/dtype/degradation, resource samples, allocation UUID and per-stage wall time. Stage aggregates overlap:

```json
{
  "media_ready_wall_seconds": 2.3982105581089854,
  "court_scene_wall_seconds": 108.87476654071361,
  "decode_perception_cache_wall_seconds": 1603.0221362044103,
  "semantic_ingest_wall_seconds": 68.8330723689869,
  "perception_court": 102.74683730537072,
  "perception_content_continuity_and_players": 746.2371927849017,
  "perception_shuttle": 241.78719548834488,
  "perception_players": 70.43187887733802,
  "perception_ocr": 325.43197728460655
}
```

TrackNet actually ran CUDA FP16 with checkpoint `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a`; no precision setting was promoted. Detector and pose provider sequences include CUDA and CPU; the limited separate node-placement probe above establishes its own measured partition, not every possible inference shape. OCR executes and records three stage-model hashes and actual configured provider options. Racket is an OpenCV CPU heuristic. Optional OSNet/ReID is explicitly degraded/unavailable. No actual actor identity is fabricated.

CPU/RSS scope is the worker process, sampled GPU memory is the worker PID sum at two-second intervals, and Torch allocator maxima exclude ORT/FFmpeg. Full shared-host system peak RAM and per-stage instantaneous GPU peaks are not inferred. Throughput below30FPS on these GTX1080Ti runs does not establish a low-latency mode or predict RTX4000Ada speed. Additional frozen exposed-data runtimes will be indexed separately after completion.

## Completed exposed-recording runtime scope

The four source-frozen external workers have now completed. The launcher sampled actual per-PID memory on the leased physical GPU; all workers used the same existing model artifacts and fixed experimental association+scene profile. These are complete-input wall times, not isolated model speed or real-time guarantees.

| Input | Frames | Launcher wall s | Launcher FPS | Worker elapsed s | Sampled worker GPU MiB peak |
| --- | ---: | ---: | ---: | ---: | ---: |
| india | 4800 | 559.121 | 8.5849 | 552.338 | 2884 |
| denmark | 3300 | 227.816 | 14.4854 | 221.886 | 2826 |
| doubles | 3600 | 388.573 | 9.2647 | 381.416 | 2888 |
| test7 | 10725 | 1167.769 | 9.1842 | 1157.291 | 2882 |

India/Denmark/doubles harnesses retain per-chunk perceive, ingest/track and retention timers plus actual model-call counts; they did not sample CPU/RSS, which remains unavailable. Decode, setup, progress persistence and postprocessing are not all assigned to those three timers. Full Test7 worker reports self CPU7,145.64seconds and maxRSS3,094,992KiB; its perception substage timers overlap. The process GPU samples exclude foreign PIDs and other-GPU workers; they are two-second samples, not instantaneous peaks or whole-device resource attribution. Exact stage sums/scopes, GPU samples and input/output hashes are in `prod_20261105_external_summary_v1/summary.json` and the four immutable `.executor.json` receipts.

Actual external ORT node placement was not reprofiled for every shape/forward. The earlier fixed-input probe remains the node-level placement evidence; these runs add actual model calls and allocated-GPU PID use, not proof that every operation runs on GPU. No model/configuration/default/precision was changed based on these throughput observations. RTX4000Ada and true-live latency remain unvalidated.
