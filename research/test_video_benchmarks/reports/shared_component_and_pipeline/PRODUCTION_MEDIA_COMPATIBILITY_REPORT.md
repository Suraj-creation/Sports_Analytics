# Production media compatibility — 5 November 2026

Two generic defects were reproduced and corrected: equal container frame-rate headers could hide genuinely variable source PTS, and HLS muxing could shift the physical video away from the canonical frame clock. The HLS correction changes container timestamps; it preserves encoded pixels, frame-rate policy, GOP, MP4 bytes and the existing analysis decoder. Existing HLS assets have not been modified. Their migration and routing remain a release gate.

This work uses tiny generated barcode footage, the authorized Test1 source for read-only packet timing, and an isolated local Firefox/server. It does not access held-out match contents, score badminton accuracy, deploy the application or change annotations/evaluation. `Benchmarking` began at `181cb917dd923524c48772b55ecc71a49ae68518`; exact executed dirty source bytes and commands accompany the experiments.

## Contracts and actual paths

`media/probe.py` selects a real video stream, excludes attached pictures and reports original metadata. `media/proxy.py` plans one CFR encode, teeing the same encoded packets to fMP4 HLS and MP4. `SegmentDecoder` decodes init plus each segment and assigns canonical indices `k*F`; it does not expose a raw container origin as an annotation offset. The browser uses the actual `VideoStage`, `useHls`, `frameClock` and playback store: frame indices floor the presentation time, and seeks target the center of a canonical frame. Physical image identity therefore has to agree with that clock, not merely with another offline decoder.

The existing proxy policy remains unchanged: 24 FPS converts to 30; 25, 30, 50, 60, 30000/1001 and 60000/1001 remain their planned rates. VFR is resampled through the existing FFmpeg FPS filter. For arbitrary VFR footage the platform still lacks an explicit complete original-frame-to-proxy correspondence table. Barcode correspondences in these experiments establish fixture identity only. They are not a general VFR annotation-mapping solution.

## Source cadence: equal headers do not establish CFR

The generated irregular Matroska source reports `r_frame_rate=avg_frame_rate=30` while its actual presentation intervals alternate approximately 1/60 and 1/20 second. The original header-only implementation declares it CFR. The original implementation failed three new tests, including real irregular timestamps and duplicate PTS; red evidence is preserved in `prod_20261105_media_packet_probe/`. Coarsely quantized true CFR remains a negative control.

The final implementation streams **only the selected video's packet PTS**. A fixed 16-line queue, maximum 256-byte read and 256-entry reorder heap bound Python memory. It scans through EOF before certifying constant cadence, permits one source clock tick of rational-rate quantization, and detects duplicate timestamps. A late packet beyond the reorder window, missing PTS, malformed data, insufficient observations, failed tool or expired shared probe deadline remains explicitly unknown through `packet_cadence_complete`, `packet_cadence_reason`, count and nullable result. Unknown actual scans conservatively request CFR handling; they do not certify whole-video CFR. The child process is terminated and reaped on timeout. Original source FPS, duration and dimensions stay unchanged.

A full read-only selected-video scan of Test1 observed all **17,268 packets**, confirmed constant cadence, and preserved 1920×1080, 30 FPS and 575.6 seconds. It took **0.952 s** with Python tracing enabled; Python peak traced allocation was **67,409 bytes**. Process RSS includes imports and FFprobe's own container/index memory is separate. Coverage and timing are in `prod_20261105_media_stream_scan/test1_scan.json`. A 100,000-observation test checks the bounded heap; timeout and excessive-reorder controls cannot certify CFR.

The preliminary whole-packet-JSON implementation is retained as historical experiment evidence but was rejected for duration-dependent Python memory. The final probe does not materialize all audio/video packet JSON or sort the whole recording.

## H20: the browser displayed a different frame from its clock

The first real browser experiment revealed a systematic physical image lag in HLS. Stabilized negative controls remove initial queued-callback races and wait for the tiny full buffer. Across eight fixtures, legacy muxing produced **40 wrong images in 96 seek observations**; eight initial HLS seeks had no usable new-frame callback and remain missing rather than invented evidence. MP4 controls were correct. Examples at 30 FPS: request frame 59, reported frame 59, displayed barcode 57; request 60, displayed 58. The same original/proxy/HLS frame sequence was correctly indexed by `SegmentDecoder`, so final-CSV inspection alone could not expose this playback defect.

Five one-variable container arms tested the actual CPU x264 command while preserving `-bf 2`, GOP, cadence and the MP4 output. `negative_cts_offsets`, explicit edit lists and their combination did not solve the zero-origin contract. Setting **`avoid_negative_ts=disabled` on the HLS tee slave** did. All five arms produced the same independent MP4 SHA. The applied production correction makes HLS's physical presentation start at zero while retaining representable negative decode/AAC timestamps. No frame-clock offset or encoder replacement is introduced.

A separate CPU x264 `bf=0` + AAC control reproduces the exact historical Test1 HLS origin **323/15360 second**. Its legacy HLS displays the wrong image at five of six seeks; the corrected HLS is correct at all six. Both MP4 byte hashes are identical. This isolates AAC priming independently of B-frame reorder delay and supports the explanation of Test1's recorded origin. It is **not** fresh NVENC regeneration or a GPU playback claim.

FFmpeg documents that the `auto` option can shift timestamps and that `disabled` prevents that shift. The alternative negative-CTS option concerns composition offsets and was tested separately. Primary documentation: [FFmpeg format options](https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/doc/formats.texi), [MOV/fMP4 muxer options](https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/doc/muxers.texi).

## Actual browser, decoder and rate validation

Firefox **158.0**, geckodriver **0.37.1**, installed FFmpeg **n8.1.3-18-g46d899d7a0-20261016**, actual MSE/H.264 support and `requestVideoFrameCallback` were used. WebDriver runs the Firefox ELF directly in its own profile. No browser or dependency was installed. A separately built local harness imports the real application player/hooks/stores; it does not contact an existing deployment, authentication endpoint, model service or match database. Exact source, built JS/source maps, commands, browser capabilities and fixture results are preserved.

| Validation | Observations | Wrong images | Missing callbacks |
| --- | ---: | ---: | ---: |
| Legacy eight-fixture MP4/HLS negative control | 96 | 40 | 8 |
| Corrected nine-fixture MP4/HLS | 108 | 0 | 0 |
| Corrected growing EVENT → full EVENT → ENDLIST | 108 | 0 | 0 |
| New-root migrated video-only/AAC candidates | 24 | 0 | 0 |
| AAC bf0 comparison, both mux arms | 24 | 5, all in legacy HLS | 0 |
| Corrected 30000/1001 and 60000/1001 | 24 | 0 | 0 |

The nine integer/VFR/offset/audio production-command fixtures have exact raw HLS `PTS=i/fps` and identical HLS/MP4/SegmentDecoder barcode sequences across boundaries and the partial final segment. All eight pre-existing fixture MP4 hashes remain identical after the mux correction. The two fractional-rate regression cases also check raw HLS PTS and physical images. Original fixture sources remain unchanged. VFR resampling may duplicate/drop original images as the existing policy prescribes; an irregular Matroska control has 11 duplicated and 11 absent source IDs, rather than an invented one-to-one correspondence.

The growing EVENT experiment serves one segment, then appends the final segment, then publishes ENDLIST through the actual Hls.js integration. It proves progressive buffering/append and subsequent seeks. It does not measure continuous-playback latency, network loss, audible synchronization or live analytics. The source-kind enum alone does not establish a live ingestion implementation: the current runner's `_ensure_media` explicitly handles YouTube and otherwise treats the source as a local file. Real RTSP/SRT/WebRTC ingestion remains unvalidated/unwired here. No future evidence was used to generate sporting events in these media tests.

Meaningful tests: six raw-HLS/image regressions **failed before the mux fix** and **passed after**. The broad generic media/stream-selection/shared-cache/probe-isolation/timeline set passed **51 tests in 9.53 s**. The final owned compatibility file, including two fractional-rate additions, passed **17 tests in 4.23 s**. Three migration tests pass separately; the added negative control rejects a CFR file without the required two-second keyframe boundaries while retaining the failed candidate and untouched original. These synthetic checks establish software/media contracts, not badminton accuracy.

## Preserving migration and release gates

The existing runner reuses an ended media root keyed by source hash, including HLS generated under older mux behavior. Merely changing `build_command` does not repair those assets. The accepted Test1 source, proxy, HLS, inference caches and historical artifacts remain immutable.

`research/production_hls_migration.py` creates a candidate in a **new, non-existing root outside the old root**. It copies the unchanged canonical MP4 and stream-copies H.264/audio into new HLS. It requires a fully inspected CFR H.264 input, hashes all old media files before/after, snapshots executed sources, verifies every video packet's bytes and PTS against MP4, and checks canonical segment counts/boundaries. Failure retains the candidate and a failure manifest. The tool refuses existing or nested output paths and never changes session pointers, URLs or deployment configuration. Video-only and AAC candidates pass the actual browser controls above.

Example, after selecting the exact authorized media root:

```bash
source ../gpu-env.sh
python -m research.production_hls_migration \
  --media-root /absolute/path/to/immutable/media/root \
  --output /absolute/path/to/new/unique/migration/candidate
```

Release still requires review of the candidate manifest, preservation of immutable prior URLs and an explicit versioned media/cache routing policy. No actual accepted data root is migrated or pointer changed in this work. Other browsers, fresh NVENC-generated HLS, audible A/V synchronization, rotation/browser combinations, network interruption and true live ingestion remain separate gates. Current container correction and deterministic contracts do not establish generalization or production promotion.

## Reproducible evidence and rejected controls

The aggregate is `artifacts/benchmarking/experiments/prod_20261105_media_final_summary/{summary.json,summary.md}`. It pins per-case browser outcomes, executed source snapshots, complete packet coverage, results/log hashes, capabilities and the experiment catalog. Rebuild it with `python -m research.production_media_report --output NEW_UNIQUE_DIRECTORY`.

Important source-bound directories under `artifacts/benchmarking/experiments/`:

- `prod_20261105_media_initial`, `media_packet_probe`, `media_verified`, `media_stream_scan`, `media_release`, `media_fractional_release`, `media_fractional_regression`: source cadence, immutable fixtures, final production commands and focused tests (each name carries the full `prod_20261105_` prefix).
- `prod_20261105_hls_container_arms`, `hls_zero_origin_component_v2`, `hls_regression`, `hls_audio_bf0_control`: one-variable mux alternatives, passing raw-PTS controls and red/green evidence.
- `prod_20261105_browser_media_control_stable`, `browser_media_zero_origin`, `browser_media_growing_release`, `browser_media_fractional`, `browser_media_audio_bf0`, `browser_media_migrated`: real isolated Firefox runs.
- `prod_20261105_hls_migration_control_v2`, `hls_migration_audio`, `hls_migration_regression_final`: unchanged-input remux candidates and tests.

Rejected/preliminary work is retained. The first WebDriver session used the shell wrapper instead of the ELF and failed. The first seek harness could read a queued prior-image callback; the stable harness supersedes it. `prod_20261105_hls_zero_origin_component` recorded `fix=true` but its harness modified the wrong command argument, leaving the actual tee command unchanged; it is an invalid experiment, explicitly rejected, and superseded by `_v2`. The complete recorded commands expose that error. No historical result was overwritten to hide it.
