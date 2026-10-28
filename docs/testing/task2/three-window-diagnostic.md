# Three bounded GPU diagnostic windows

The first results below are historical: they predate the final contact policy. See the final-policy comparison at the end of this document.

These are fresh component-level diagnostic runs on 28 October 2026, not event-accuracy benchmarks or end-to-end application performance. They do not establish that the proposed contacts, shuttle detections, track IDs, or shot labels are correct. Inputs and existing session data were not modified. GPU 1 was idle before the runs; GPU 0's unrelated process was left alone.

| Recording and actual input | Frame indices and half-open time | Shuttle detections | Contact candidates: frame (seconds) | Wall time, including model load but excluding decode | Sampled peak GPU process memory |
|---|---|---:|---|---:|---:|
| Broadcast singles, original AV1 decoded to a temporary lossless clip | 1043–1162, 41.72–46.52 s at 25 fps | 119/120 | 1059 (42.36), 1079 (43.16), 1102 (44.08), 1133 (45.32) | 5.69 s | 1390 MiB |
| Broadcast doubles, original VP9 | 1110–1229, 44.40–49.20 s at 25 fps | 112/120 | 1112 (44.48), 1118 (44.72), 1128 (45.12), 1140 (45.60), 1152 (46.08), 1165 (46.60), 1175 (47.00), 1198 (47.92), 1214 (48.56), 1226 (49.04) | 6.38 s | 1378 MiB |
| Amateur multi-court, normalized proxy | 886–1005, 29.533–33.533 s at 30 fps, proxy timebase | 58/120 | 921 (30.70), 941 (31.367), 979 (32.633), 993 (33.10), 1004 (33.467) | 6.85 s | 1382 MiB |

The doubles candidate at frame 1118 has an unresolved nearest-track hypothesis because the two proximity scores were close; this is a heuristic abstention, not calibrated hitter confidence. All candidates have `unknown` shot family because this component probe deliberately supplies no court or flight evidence to the rules classifier. It does not measure normal pipeline classification coverage or shot accuracy. The amateur source uses variable-rate timestamps; its listed positions refer to the existing 30 fps H.264 proxy, not raw source frame indices.

The three raw JSON reports, sanitized model-load logs and original/temporary pixel-frame hash lists are saved next to this note as `three-window-{singles,doubles,amateur}.json`, `three-window-{singles,doubles,amateur}-model-log.txt` and `three-window-singles-{original,clip}.framemd5`. **The singles raw JSON reports local temporary clip frames 0–119 and clip-relative times; add 1043 frames or 41.72 s for original frame/time.** The table already applies this offset. The source AV1 could not be decoded by the existing OpenCV build; the installed FFmpeg `libdav1d` decoder selected original decoded frames 1043–1162 into a temporary FFV1 clip. All 120 pixel frame MD5 values match between independent original-source decoding and FFV1 clip decoding. This does not imply any labelled accuracy or identical behavior under different decoder/model versions.

Input hashes (SHA-256):

- Singles original: `314b4997fde9670c17cde76a256ff64c9a5f565317078f1d9826f5ffee8602c0`.
- Doubles original: `f9a419327a85b4e17d524d2fae24245ae9fc862b06a05c8fc11ed457eb487cba`.
- Amateur source identity: `90d1f399c05312ede173de2f2c8cd2fee09f1d201df46b476119660a00039ff0`; actual normalized proxy input: `a4eaaf0551bec33ecf3b8ffbe9b002c8bad9dcdbc1be894e39356c60b7436aee`.
- Temporary lossless singles clip: `d2dacfdff1dea98fb762772a68dc2f59bd7e31fbd5ce5275422bc73c47a4218d`.
- TrackNetV3 weights: `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a`; RF-DETR small: `fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e`; RTMPose M: `5c0a4bf67953e6d2ac43ce15e77dc9d5d354ae18430a47d2c5963a7bc5683e3c`.
- Diagnostic script SHA-256: `2817d2a59cd9e6bc45920f98ea150b8acbe4bae27abfd089b154829f3c783278`.

The runs used GPU 1, existing `.venv` and `gpu-env.sh`, 1280×720 resized input, FP16 TrackNet (batch 2, step 8), RF-DETR small and RTMPose M with 2-frame detector/pose stride, ONNX CUDA with CPU fallback listed. ONNX provider listing does not prove every operator ran on GPU. Pose stride 2 can make the consecutive-frame wrist-speed cue unavailable. No court isolation, camera calibration, scene gating, rally segmentation or match rules were applied; detections can include other courts or bystanders. TrackNet starts with a cold single-shot background. GPU memory was sampled every 0.3 s and may miss the true peak; PyTorch reserved peak was 794 MiB for each run. Decode and resize were performed before the timed region.

## Reproduce

On the authoritative server, from a checkout containing `research/evaluation/fresh_component_diagnostic.py`, run the following with a free GPU 1 and the existing configured environment. The original sessions are read-only inputs and output is a new temporary directory. Frame hash evidence may be rechecked with `ffmpeg -f framemd5` on both the selected source frames and lossless clip.

```bash
TASK2_ROOT=/home/administrator/Desktop/sport-analytics/Sports_Analytics
TASK2_CHECKOUT="$PWD"
source "$TASK2_ROOT/../gpu-env.sh"
export CUDA_VISIBLE_DEVICES=1 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
export PYTHONPATH="$TASK2_CHECKOUT/engine/src:$TASK2_CHECKOUT/sports/badminton/src"
TASK2_POSE="$TASK2_ROOT/models/cache/rtmpose_m_body7/extracted/20230831/rtmpose_onnx/rtmpose-m_simcc-body7_pt-body7_420e-256x192-e48f03d0_20230504/end2end.onnx"
TASK2_OUT="$(mktemp -d /tmp/task2-three-windows.XXXXXX)"
SINGLES="$TASK2_ROOT/data/media/314b4997fde9670c17cde76a256ff64c9a5f565317078f1d9826f5ffee8602c0/source.mp4"
ffmpeg -hide_banner -loglevel error -c:v libdav1d -i "$SINGLES" \
  -vf "select='between(n,1043,1162)'" -fps_mode passthrough -frames:v 120 -an \
  -c:v ffv1 -level 3 "$TASK2_OUT/singles-lossless.mkv"
for spec in 'singles 0 25' 'doubles 1110 25' 'amateur 886 30'; do
  read -r name start fps <<< "$spec"
  case "$name" in
    singles) video="$TASK2_OUT/singles-lossless.mkv" ;;
    doubles) video="$TASK2_ROOT/data/media/f9a419327a85b4e17d524d2fae24245ae9fc862b06a05c8fc11ed457eb487cba/source.mp4" ;;
    amateur) video="$TASK2_ROOT/data/media/90d1f399c05312ede173de2f2c8cd2fee09f1d201df46b476119660a00039ff0/proxy.mp4" ;;
  esac
  "$TASK2_ROOT/.venv/bin/python" "$TASK2_CHECKOUT/research/evaluation/fresh_component_diagnostic.py" \
    --video "$video" --start "$start" --count 120 --fps "$fps" \
    --tracknet "$TASK2_ROOT/models/cache/tracknetv3/TrackNet_best.pt" \
    --detector "$TASK2_ROOT/models/cache/rfdetr_small/rfdetr_s_v142_512x512.onnx" \
    --pose "$TASK2_POSE" > "$TASK2_OUT/$name.json" 2> "$TASK2_OUT/$name.log"
done
```

## Final contact policy rerun

The same three inputs and frame windows were rerun on GPU 1 after the final contact-attribution policy, `relative_proximity_gap_v1`. The earlier JSON and sanitized logs above are preserved as historical artifacts; the new reports and sanitized logs are `final-three-window-{singles,doubles,amateur}.json` and `final-three-window-{singles,doubles,amateur}-model-log.txt`. Each new candidate records the attribution policy and reason. These outputs remain unlabelled component hypotheses, not precision, recall or evidence of a classification improvement.

| Window | Earlier candidate frames | Final candidate frames | Unattributed final hypotheses and reason | Total runtime | Sampled peak GPU process memory |
|---|---|---|---|---:|---:|
| Singles original frames 1043–1162 | 1059, 1079, 1102, 1133 | 1059, 1079, 1102, **1122**, 1133 | 1122: `insufficient_proximity` | 5.45 s | 1376 MiB |
| Doubles frames 1110–1229 | 1112, 1118, 1128, 1140, 1152, 1165, 1175, 1198, 1214, 1226 | same ten | 1118: `ambiguous_proximity` | 6.34 s | 1376 MiB |
| Amateur proxy frames 886–1005 | 921, 941, 979, 993, 1004 | same five | none | 6.83 s | 1376 MiB |

Singles frame 1122 is local clip frame 79: its strongest proximity score is 0.016, below the final minimum of 0.05. Its contact score is 0.6116 and the hitter remains unresolved. The changed candidate set may reflect interactions with temporal same-player suppression; it has not been independently validated. Doubles frame 1118's best and runner-up proximity scores are 0.4994 and 0.4850, with relative gap 0.0287 below 0.05. Other final candidates use `nearest_proximity`; that remains a temporary track hypothesis, not verified participant identity. All shot-family fields are `unknown` because this harness supplies no valid court or flight context. Shuttle detections are unchanged at 119/120, 112/120 and 58/120. Load, shuttle and player/pose times were respectively 1.58/1.33/2.52 s (singles), 1.59/1.31/3.31 s (doubles), and 1.80/1.26/3.75 s (amateur); total includes contact processing, excludes decoding and resizing, and sampled memory can miss a peak.

Provenance: checkout `3cc74e241b00f98beb25e76cc109f492d29248c4` with local uncommitted final policy changes, so the commit alone is insufficient to reconstruct the run. SHA-256 of the exact files used:

- `sports/badminton/src/bai_badminton/events/contact.py`: `9db0c068d9b0b61506e075511ce48c182c54532d9358ccdbfb4420449ee34efc`.
- `research/evaluation/fresh_component_diagnostic.py`: `b8b591823f544262d4c4aa1748c3cc5becfd47ff43babb9cb0a3b669b6fe874f`.
- `sports/badminton/src/bai_badminton/events/stroke.py`: `2d0ab87fcceabd49b44d446278cd146c284c728f3e1e376a4414ea71fda5cbe2`.
- `sports/badminton/src/bai_badminton/perception/tracknet.py`: `8962bd6de8080b23e0eaa0e5bbcb06a6fa16c3dbc586cbef4f10272f32151f2d`.
- `sports/badminton/src/bai_badminton/perception/players.py`: `01f5204596cfda5a429bb86fca41103de90a86a7b6004cec2cef8ed599a4bb9a`.
- `sports/badminton/src/bai_badminton/perception/shuttle_post.py`: `f14e12e2f9ee3d2f12e62be7004cd2c1ccb42372f6057ab686b721db8afb0075`.
- `sports/badminton/src/bai_badminton/observations.py`: `b7b7bfe03877ec4f9b47386f5e2023f1567d32dddd95eb71180d7567d0bfb5e6`.

The reproduction commands above use the current policy and script. This rerun used the already prepared lossless singles clip with the same SHA-256 and pixel-frame hashes specified above; no original session, source, or pre-existing output was modified. All earlier limitations continue to apply.
