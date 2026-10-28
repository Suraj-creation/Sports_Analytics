# Bounded fresh-inference diagnostic

On 28 October 2026, two local diagnostic runs read `Test7_Full.mp4` (SHA-256 `1ad1eac44150a0a23e2bad1f3d4204bd41f2d257ff6b35156234d38cfa2b9d9c`; 1920×1080, 30 fps) without modifying the video or a session. GPU 1 was selected with `CUDA_VISIBLE_DEVICES=1`; GPU 0 had an unrelated process and was not used. Input was resized to 1280×720. TrackNetV3 ran in torch CUDA FP16, batch 2, step 8; RF-DETR small and RTMPose M body7 used ONNX CUDA with CPU fallback listed; detector and pose stride were both 2.

| Source frames | Time window | Shuttle detections | Contact candidates | Total runtime including load | Sampled peak process GPU memory |
| --- | --- | ---: | --- | ---: | ---: |
| 0–95 | 0–3.2 s | 2/96 | none | 5.60 s | 1,376 MiB |
| 180–299 | 6–10 s | 104/120 | 186, 223, 255, 278 | 6.28 s | 1,378 MiB |

In the second run, the four heuristic contact-fusion scores were respectively 0.8810, 0.6585, 0.8459 and 0.5571; these are candidate scores, not labelled contacts, accuracy or hitter probabilities. The classifier was deliberately given no valid court, flight, or serve evidence and returned `unknown` for all four; this does not test normal engine classification. The unverified nearest track IDs are not participant identities. The source contains embedded historical overlays. The two windows differ in observed detection counts; without labelled data the cause cannot be established. The second window was selected as a putative rally from a draft visual review, not verified ground truth.

These runs operate on uncalibrated full frames without court isolation, scene filtering, match phase or rally construction. TrackNet starts with a cold, single-shot background rather than the production warm-start; pose stride 2 means wrist-speed cues requiring consecutive observations can be absent. ONNX provider listing does not establish that every operator ran on GPU. Peak process memory was sampled every 0.3 s, so it can miss the true peak; PyTorch peak reserved was 794 MiB. Decode and resizing occurred before the measured time. These numbers are not end-to-end latency or labelled accuracy.

The reusable, read-only `research/evaluation/fresh_component_diagnostic.py` takes explicit paths and caps a run at 300 frames. It does not fetch models or write session data. The following server commands run against the original checkout and existing environment; update `task2_checkout`, `task2_source`, and the pose path if the worktree or inputs differ. Output goes into a new temporary directory. Do not run on a GPU used by an unrelated job.

```bash
task2_checkout="$PWD"
task2_root="$HOME/Desktop/sport-analytics/Sports_Analytics"
task2_source="$task2_root/data/task2-review/Test7_Full.mp4"
task2_pose="$task2_root/models/cache/rtmpose_m_body7/extracted/20230831/rtmpose_onnx/rtmpose-m_simcc-body7_pt-body7_420e-256x192-e48f03d0_20230504/end2end.onnx"
task2_output="$(mktemp -d /tmp/task2-fresh-gpu-XXXXXX)"
source "$task2_root/../gpu-env.sh"
export CUDA_VISIBLE_DEVICES=1 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
export PYTHONPATH="$task2_checkout/engine/src:$task2_checkout/sports/badminton/src"
for task2_window in '0 96' '180 120'; do
  read -r task2_start task2_count <<< "$task2_window"
  "$task2_root/.venv/bin/python" "$task2_checkout/research/evaluation/fresh_component_diagnostic.py" \
    --video "$task2_source" --start "$task2_start" --count "$task2_count" --fps 30 \
    --tracknet "$task2_root/models/cache/tracknetv3/TrackNet_best.pt" \
    --detector "$task2_root/models/cache/rfdetr_small/rfdetr_s_v142_512x512.onnx" \
    --pose "$task2_pose" \
    > "$task2_output/run-$task2_start.json" 2> "$task2_output/run-$task2_start.log"
done
```

Weights SHA-256: TrackNet `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a`; RF-DETR `fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e`; RTMPose `5c0a4bf67953e6d2ac43ce15e77dc9d5d354ae18430a47d2c5963a7bc5683e3c`. A subsequent run with the reusable script reproduced the 104 detections and the same four candidates, in 6.56 s with 1,380 MiB sampled process peak. Different drivers, model files or tracking implementation can change results.
