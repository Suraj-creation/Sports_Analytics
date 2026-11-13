# Actual runtime model-asset fingerprints

The three RapidOCR model files are already fingerprinted in preserved worker runtime declarations and independently verified technical analyses. Their current bytes match the recorded hashes for Test1 baseline/improved, Test2 baseline/improved and the failed c7 Test1 control. The actual extracted RTMPose graph also matches the separately retained historical graph hash. This audit adds a source-bound snapshot of those assets during the running c585e35 Test1 job; it reports no evaluation result or accuracy gain.

The authoritative [metadata receipt](metadata_receipt.json) records full paths, resolved paths, byte sizes, package metadata, local release-checksum declarations, historical comparisons and every consumed-file hash. The [live log snapshot](run.execution.asof_v2.log) captures exactly4,026bytes at2026-11-11T20:27:21.631035UTC (2026-11-12,01:57:21IST). Its hash binds that finite prefix; it does not pretend the growing original log is immutable. The corresponding [closed first-segment runtime metadata](first_closed_cache_runtime_metadata_v2.json) identifies actual loaded models/providers for frames0–59 while the overall run remains live.

| Actual asset | Bytes | SHA256 |
|---|---:|---|
| OCR detection: `PP-OCRv6_det_small.onnx` | 9,929,594 | `090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f` |
| OCR classifier: `ch_ppocr_mobile_v2.0_cls_mobile.onnx` | 585,532 | `e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c` |
| OCR recognition: `PP-OCRv6_rec_small.onnx` | 21,234,383 | `6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884` |
| Actual RTMPose graph: `end2end.onnx` | 54,330,655 | `5c0a4bf67953e6d2ac43ce15e77dc9d5d354ae18430a47d2c5963a7bc5683e3c` |
| RF-DETR: `rfdetr_s_v142_512x512.onnx` | 119,619,156 | `fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e` |
| TrackNet: `TrackNet_best.pt` | 136,190,877 | `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a` |
| RTMPose source ZIP container (not a second executed pose model) | 50,799,818 | `f7fbb6c5c11a1bb70f3d445e4ddec5d144ea89ad5649c081ef976f9b24a0b741` |

The OCR files reside under the shared environment's `.venv/lib/python3.12/site-packages/rapidocr/models/`. The six executed checkpoint/graph assets are distinguished from the extra ZIP container. Every extracted archive member—including the actual pose graph—is checked against both its extraction manifest and the exact pinned ZIP member. Supporting extraction files are listed separately; they are not all claimed to be executed models.

RapidOCR is3.10.0. All three current OCR models match their installed `RECORD` base64SHA256/size entries and the release checksums in the installed, RECORD-verified `default_models.yaml`. That file identifies releasev3.10.0 model URLs; those URLs were not fetched. The installed `RECORD` itself is retained by hash`76c0649c1db1976dfb03dde4097819bacb875304d395212e65ce2f5c1d663cae`. These are current local package/checksum bindings, not an independently authenticated online release or signature.

Historical model-byte identity is supported by stored runtime and analysis SHA256 values in all five reviewed runs. Their [preserved execution-log bindings](historical_log_bindings.json) separately retain initialization filenames/engines and exact log hashes. **Historical whole-package RECORD/source-code byte identity remains UNAVAILABLE**: an equal version string and equal model hashes do not establish equality of every installed Python package file. If an additional historical asset or dictionary lacks a stored fingerprint, its identity must remain unavailable. The current ONNX recognition graph hash covers embedded metadata; no separate dictionary path is declared in the runtime receipt, and this audit instantiated no OCR session to infer additional state.

Actual first-segment backends remain TrackNetCUDAFP16, RF-DETR/poseONNXCUDA and OCRONNXCPU. Current installed versions are recorded separately from historical evidence. Scene continuity, court lines, tracking, racket geometry and rule-based semantics do not introduce additional learned checkpoints in the recorded loaded-model set. Optional OSNet/BallTrack/WASB/InpaintNet are not claimed to have executed.

All bound files were rehashed unchanged, and the captured live-log prefix was rechecked at the end. No model or OCR object was imported/initialized by this audit; no network, download, inference, model write, lock change, candidate edit or Test3 access occurred. The running GPU job and unrelated processes were left untouched.
