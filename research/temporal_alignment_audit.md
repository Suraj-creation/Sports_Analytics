# Temporal and video alignment audit — Test 1

Audit B; production revision `301baf08be5e989dd0ed93cb885733c3cf6f356a`,
frozen benchmark revision `b773e20c62d1c398cddc3d23510bd4adf823325b`.
This audit made no production, evaluator, annotation, source-video or baseline
artifact changes. New evidence is under
`artifacts/benchmarking/investigation/audit_b/`.

## Finding B1: offline source/proxy frame drift is ruled out by the available evidence

**Observed symptom.** Matched starts can be hundreds of frames late and ends
hundreds early. A common frame offset, FPS conversion or dropped-frame problem
could produce systematic errors and must be checked independently.

**Independent measured evidence.** Fresh `ffprobe -show_packets` scans, saved as
`original_packet_timeline.json` and `proxy_packet_timeline.json`, establish:

| Video-stream property | Original | Production proxy MP4 |
| --- | --- | --- |
| Resolution | 1920×1080 | 1280×720 |
| Nominal / average FPS | 30/1 / 30/1 | 30/1 / 30/1 |
| Time base | 1/15360 | 1/15360 |
| Presentation timestamp origin | 0 | 0 |
| Video packet count | 17,268 | 17,268 |
| Every sorted PTS increment | 512 ticks | 512 ticks |
| Last presentation timestamp | 8,840,704 ticks | 8,840,704 ticks |
| Video-stream duration | 8,841,216 ticks = 575.6 s | Same |

Thus every source/proxy timestamp is exactly `frame_index / 30`, with no missing
or duplicate PTS, drift, rate conversion or fitted offset. Packet counts here
are independent measurements, not newly claimed full source decode counts;
the baseline additionally records 17,268 decoded frames for each stream.

The audit then sought actual original and proxy frames by **exact PyAV frame
PTS**, checking the returned PTS instead of trusting approximate seek position.
It decoded 32 target samples covering the beginning, TrackNet and HLS boundaries,
GT 2/19/20/27, other missed boundaries, and the final frames. All 32 same-index
HLS frames returned by the actual `SegmentDecoder` are pixel-identical to their
proxy MP4 counterparts. Original-to-proxy grayscale MAE after spatial resizing
is only 0.3147–0.5196 intensity levels in these samples.

As a diagnostic only, moving court/player pixels were compared against proxy
offsets −2..+2. Offset zero was best for 31/32 samples. Frame 7 had a near-tie
favoring +1: motion-region MAE 0.9265 versus 0.9848 at zero. Its source frames 7
and 8 are themselves near duplicates (whole-image grayscale difference 0.00210),
much smaller than resize/encoding error (~0.51). This weak content score does
not establish a dropped/shifted frame. No offset was applied to any annotation
or prediction. Exact timestamp correspondence and the same-index HLS identity
checks are the relevant timeline evidence. Results are in `decoded_alignment.json`
and `ambiguous_frame7_similarity.json`.

**Source path.** `engine/src/bai_engine/media/proxy.py:105` (`plan_proxy`) retains
30 FPS; `build_command` uses spatial `scale=-2:720:flags=bicubic`, the 30/1 `fps`
filter and CFR encoding, without crop/trim. `engine/src/bai_engine/decode.py:55`
(`SegmentDecoder.decode_segment`) emits absolute indices `k*F + local_index`.
`runtime/runner.py:470` uses the planned HLS segment size, then ingests in order.

**Diagnosis / confidence.** High confidence that offline temporal misalignment
is not the cause of the large Test 1 errors. A spatial/model-context issue can
remain despite a correct timeline; alignment checks do not prove shuttle accuracy.

**Alternative explanations.** Fragmentation, minimum-duration cancellation,
temporary missing shuttle evidence and stationary false peaks remain plausible
and are directly investigated by the other audits. Human annotation tooling
history is unavailable; CSV arithmetic supports zero-based indexing but cannot
exclude a one-frame human boundary convention. Such ambiguity cannot explain
the observed 100–442-frame errors.

**Causal experiment / action.** Keep source, proxy, FPS and matcher unchanged;
test semantic interventions on the exact recorded inputs, then rerun production.
Do not fit a frame offset or rewrite ingest to improve this benchmark.
**Expected metric effect:** none from an alignment correction, because no such
correction is justified. **Regression risk:** changing a correct timebase would
corrupt every event and benchmark comparison.

## Finding B2: HLS raw PTS has a small mux origin shift, without benchmark frame drift

`hls_packet_segments.json` independently covers all 288 HLS segments. The first
287 contain 60 video packets and the last contains 48, totaling 17,268. Segment
`k` begins at `323 + k*60*512` ticks; all video PTS increments are 512 ticks.
Consequently the HLS container's first video PTS is **323/15360 = 0.021028646 s**,
or **0.630859375 frame**, rather than MP4/source zero. This is a mux/timing-origin
property, not an extra/missing video frame: sampled HLS frame pixels equal
same-index MP4 pixels exactly. The production decoder deliberately uses `k*F`
frame indices and does not convert this HLS raw PTS into rally indices.

The proxy **container** duration is 575.616 s while its **video stream** duration
is 575.600 s, consistent with an audio/mux tail. Neither discrepancy calls for
changing prediction timestamps. A long container duration is not evidence of
additional video frames.

**Relevant consumers.** `apps/web/src/lib/frameClock.ts:35` uses
`floor(mediaTime*fps + 1e-4)`. At the observed HLS frame PTS this still maps frame
`k` to `k`, because the fractional shift is below one frame. The presented-frame
callback path in `VideoStage.tsx:149` passes `meta.mediaTime`. However, evidence
seeks use `(frame+0.5)/fps` (`VideoStage.tsx:95`), which is before raw HLS frame
`k`'s PTS if the browser retains the measured origin. Browser/MSE/HLS normalization
can change that relationship. This is a **playback-seek hypothesis requiring a
real browser seek/callback test**, not a proven UI defect. The offline benchmark
does not consume a browser clock, so it cannot explain its large boundary errors.

**Action / risk.** Retain explicit canonical-frame versus encoded-PTS origin
metadata and test frame stepping/seeks with a real HLS presentation before a
playback change. Do not subtract this origin from benchmark CSV values. Expected
benefit is review/evidence accuracy at sub-frame boundaries, not improved Test 1
detection metrics. Altering the shared clock without testing MP4/HLS/live sources
risks introducing a real offset.

## Finding B3: direct original-frame inspection supports continuation failures

The following montages were generated from **original 1920×1080 decoded frames**.
Yellow circles show existing model observations mapped from proxy coordinates
by the known spatial factor 1.5. They are model outputs, not pixel ground truth.
No annotation was added, moved or used to generate a prediction.

| Case / evidence file | Direct observation | Interpretation and limits |
| --- | --- | --- |
| GT 20: `gt20_top_exit.jpg`, source 9523,9525,9530,9540,9543,9544 | Near player prepares and performs an overhead action during the model's missing run; preceding/following observed points are near the image top. Camera view and court remain continuous. | Strong diagnostic support that stopping at 9525 is an activity-continuation failure. A high trajectory leaving/re-entering the visible image is plausible. Without independently labeled shuttle pixels, exact physical exit or preceding peak correctness is not proven. |
| GT 27: `gt27_stationary_point.jpg`, source12748,12753,12763,12768,12771,12780 | Repeated low-confidence peaks near proxy(645,393), original(968,590), coincide with the center-service painted T while the far player performs overhead action; a later peak moves near the player/racket region. | Strong visual evidence of unreliable static-position evidence during an exchange; compatible with a court-line attractor. It is not evidence that the players or the rally are stationary. Formal detector false-positive accuracy still needs pixel labels. |
| GT 2: `gt2_gap.jpg`, source891,1023,1030,1040,1064,1066 | Players continue positioning/overhead exchange during the 1024–1064 missing run; first fragment begins near the GT onset. | Supports fragmentation rather than a six-second source timestamp shift. Missing observations are not proof that the rally ended. |
| GT 19: `gt19_gap.jpg`, source8110,8266,8275,8285,8305,8308 | The same continuous court view shows preparation and overhead exchange through the missing run. | Supports the earlier-fragment / later-selected-match explanation; exact source index comparisons passed. |
| Missed cases: `missed_boundaries.jpg` | Original frames at GT5,25,28,29,31 starts and selected fragments are available for review. | Diagnostic support only; root-cause claims should rely on exact semantic trace plus temporal visual evidence, not a still image alone. |

**Action / expected effect.** Test observation-quality-aware continuation and
the validity of stationary evidence, preserving genuine between-rally breaks.
These mechanisms can reduce splits and therefore extreme *selected-match*
start/end errors. Do not claim that player motion alone proves a rally, and do
not indiscriminately merge all intervals overlapping one label. Causal acceptance
requires the unchanged full benchmark and control cases, not montage appearance.

## Finding B4: temporal context size differs from the configured chunk field

The profile declares `chunk_frames:64`, but VOD `SessionRunner._analyse` uses
`plan.frames_per_segment`, which is `round(2*30)=60`. Cached evidence independently
contains 287×60-frame chunks plus one48-frame chunk. TrackNet `detect` emits one
heatmap-derived result for **every real frame**, including its tail; `step=8` is
window stride, not observing only every eighth frame (`tracknet.py:479–529`).

At 60-frame boundaries the 8-frame model needs a tail window with overlap; model
context/phase therefore differs from a hypothetical64-frame batching scheme.
This is a **configuration/context discrepancy**, not missing video frames or
timestamp drift. Auditor C owns its inference-quality measurement.

**Experiment.** Same checkpoint, precision and same original frames, vary only
window stride or context-boundary strategy; report all-frame outputs, runtime,
continuity and downstream boundaries. Never relabel the inputs or describe the
baseline as eightfold temporal frame skipping. A more expensive overlap strategy
has no established benefit until measured. Regression risk includes compute cost,
duplicate heatmap accumulation and context leakage across cuts.

## General-source risks, outside the demonstrated Test 1 root cause

`plan_proxy` maps unsupported source rates to30 and high rates above60 to60;
`ProbeResult.variable_frame_rate` compares aggregate rates rather than inspecting
all PTS (`media/probe.py:42`). Such future sources require explicit original-frame
to canonical-frame mappings and packet-based validation. Test1 is exact CFR30,
so neither behavior changed this video. Source rotation and selected stream are
recorded and applied by ingest; no rotation/crop is present here. Generic source
mapping should be hardened through focused fixtures, not a broad ingest rewrite
attributed to this benchmark without evidence.

## Validation and limitations

`research/audit_b_temporal.py` is the read-only reproduction helper. It checks
exact frame PTS, same-index HLS/proxy pixels and source/proxy similarity, then
creates the visual evidence. Independent full packet scans and HLS segment
packet checks are recorded separately. The selected existing temporal/media
test suite passed **36 tests in5.06 s**, with no skips, on the required server
environment; see `temporal_alignment_tests.md` for the precise configuration.
No real browser seek test or new VFR/high-FPS experiment was executed. No model
or extra source video was downloaded, and no inference improvement is claimed.
