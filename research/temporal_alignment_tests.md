# Temporal alignment validation evidence

Audit B; source/media commands used the existing GPU-server environment:

```bash
cd /home/administrator/Desktop/sport-analytics/Sports_Analytics
source ../gpu-env.sh
```

All new artifacts are under `artifacts/benchmarking/investigation/audit_b/`.
Baseline files, original media/annotations, ingestion/proxy implementation and
the production evaluator were only read. No dependency installation was performed.

## Executed checks

| Check | Inputs and method | Measured outcome |
| --- | --- | --- |
| Original presentation timeline | Fresh `ffprobe` video packet PTS/duration and stream metadata |17268 packets, PTS0..8840704, every increment512 at1/15360, duration8841216ticks |
| Proxy presentation timeline | Same independent scan | Exactly the same PTS grid/count/video duration |
| All HLS packet segment boundaries | PyAV demux of init+each `.m4s` |288 segments;287×60+48 packets; every segment starts323+k*60*512 and ends at start+(count−1)*512 |
| Exact frame seek | PyAV seeks each target PTS and asserts returned decoded PTS equals index*512 |32 target source/proxy samples passed |
| Production decoder identity | `SegmentDecoder.decode_frame(index)` versus same-index proxy MP4 decoded image |32/32 pixel-identical, maximum channel error0 |
| Original/proxy spatial comparison | Original resized1920×1080→1280×720, grayscale Gaussian comparison |Whole-image MAE0.3147–0.5196 across32 samples |
| Tested offsets−2..+2 | Compare only moving court/player pixels; no correction applied |31/32 best offset0; frame7 weak near-tie+1 with near-duplicate source7/8 |
| Near-tie control | Independently compare source7/8 and proxy7/8 |Source adjacent difference0.00210; proxy difference0.04381, below cross-encode error≈0.51 |
| Boundary visual review | Original decoded frames for GT2/19/20/27 and missed cases |Source montages inspected; supports ongoing exchange through several missing/stationary model runs, with pixel-GT limitations stated |
| Helper lint / formatting | `ruff check research/audit_b_temporal.py`; `ruff format` | Passed |

Target frame samples:

```text
0,7,8,59,60,119,120,243,887,891,1023,1024,1064,1066,
8106,8110,8266,8308,9523,9525,9530,9543,9544,9967,
12451,12748,12763,12768,12771,12966,17226,17267
```

Reproduce exact-PTS sample comparisons and original-frame montages:

```bash
python research/audit_b_temporal.py \
  > artifacts/benchmarking/investigation/audit_b/execution.log 2>&1
```

The helper intentionally permits regenerating **its own diagnostic artifacts**;
it does not write baseline outputs or media. To preserve previous audit runs,
copy its output directory to a new investigation revision before repeating it.
Its offset selection is a diagnostic similarity test, never an annotation or
prediction alignment adjustment.

## Existing temporal/media tests executed

```bash
pytest -q \
  engine/tests/test_timeline.py \
  engine/tests/test_media.py \
  engine/tests/test_media_stream_selection.py \
  engine/tests/test_ffmpeg_probe_isolation.py \
  engine/tests/test_shared_media_preparation.py \
  > artifacts/benchmarking/investigation/audit_b/tests.log 2>&1
```

Result: **36 passed in5.06 s**, exit0, no skips.

`test_media.py` includes real FFmpeg source→proxy/HLS→decode integration with
synthetic frame barcodes and verifies actual frame identity across segment
boundaries and the partial final segment. Its fixture explicitly selects the
CPU `libx264` encoding path (`prefer_gpu=False`) on the GPU server. Those tests
are **not** a claim that the same synthetic fixture exercised baseline NVENC.
The actual Test1 NVENC outputs are independently checked by the packet and
decoded-pixel comparisons above. Other tests include controlled subprocess and
shared-writer mocks; passing them establishes their isolation/lifecycle contracts,
not real model inference or sporting accuracy.

## Artifacts

- `original_packet_timeline.json`, `proxy_packet_timeline.json`: fresh packet scans.
- `hls_packet_segments.json`: all288 HLS packet ranges.
- `decoded_alignment.json`:32 exact-index sampled comparisons.
- `ambiguous_frame7_similarity.json`:near-duplicate control.
- `gt2_gap.jpg`, `gt19_gap.jpg`, `gt20_top_exit.jpg`,
  `gt27_stationary_point.jpg`, `missed_boundaries.jpg`:original-frame diagnostics.
- `execution.log`, `tests.log`:actual command results.

## Not executed / unresolved

No browser HLS seek/callback test was run. Therefore the small raw HLS origin
shift's effect on center-of-frame seeks remains a hypothesis. No full new source
decode-count scan was performed by AuditB; this audit independently enumerated
all video packets and decoded the listed samples, while the frozen baseline
records full source/proxy decode counts. No VFR, unsupported-rate, rotation or
high-FPS source was newly synthesized for this audit. Existing tests cover their
declared fixtures only. No independently labeled shuttle pixels or contact events
were available; model circles and visual observations remain diagnostic evidence.
