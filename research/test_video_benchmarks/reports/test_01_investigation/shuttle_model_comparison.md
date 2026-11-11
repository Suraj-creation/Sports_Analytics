# Shuttle model comparison and adoption gates

Audit C; research checked 2026-11-05 local time. This is a suitability/licensing/source audit. **Only the existing TrackNetV3 baseline has measured Test1 production results.** No alternative weights were downloaded or run; no model superiority on Test1 is claimed. Published localization scores are not rally-boundary scores and are not comparable across different datasets, splits, tolerances and hardware.

## Candidate comparison

| Candidate | Compatibility and expected engineering cost | Weights and licensing | Measured Test1 / cost evidence | Decision |
| --- | --- | --- | --- | --- |
| Existing TrackNetV3, step8 | Current typed shuttle port;8RGB frames+median→8heatmaps,512×288; preserves deployed CUDAFP16 checkpoint. Step4/1 available already. | Official code **and checkpoints explicitly MIT**. Dataset footage rights remain separate. Current136,190,877-byte checkpoint pinned by SHA256 in benchmark metadata. | Real baseline49rallies/30TP/19FP/6FN; full pipeline1469.24s, including all stages, not isolated TrackNet latency. | Preserve as baseline. First test continuation/evidence semantics; lower-risk than replacing the backbone. |
| TrackNetV3 + official InpaintNet | Same detector with16-position trajectory repair; needs adapter separating observed and reconstructed coordinates and uncertainty. A filled point cannot become an observed contact. | Official MIT grant includes checkpoints. Checkpoint availability in registry does not prove installed/validated runtime integration. | No Test1 InpaintNet inference. Current spline interpolation already marks974frames estimated in global diagnostic; simply improving the drawn path will not change FSM observation evidence. | Research-only until continuity consumers handle estimates correctly and an ablation separates detector vs repair effect. |
| RacketVision BallTrack | Recent multisport TrackNetV3 variant;official config4frames+median,512×288. Different checkpoint dimensions/preprocessing; not a weight swap into the8-frame27-channel model. Existing profile names do not prove this optional provider ran. | Repository MIT. Official linked HF model repository has weights but no model-card license metadata at inspected revision; a separate unambiguous checkpoint/data grant was not independently verified. Dataset/YouTube content rights need their own review. | No Test1 measurement. Four-frame architecture suggests shorter context; actual latency/VRAM and amateur-domain gain unmeasured. | Promising adapter-level challenger after license/provenance gate and fixed-input localization/boundary comparison. Official per-frame heatmap protocol is not itself a guarantee of causal live operation. |
| TrackNetV4 motion attention | Official TensorFlow/Keras framework and model-integration code; requires isolated runtime/export adapter, preprocessing parity and Pascal compatibility validation. | MIT source license inspected. Official pretrained download links exist; source MIT alone does not independently establish every externally hosted weight/data license. | Authors report a small gain for a3in/3out TrackNetV3+motion comparison on their badminton test set, not our8-frame checkpoint or source. No Test1 result or local runtime/VRAM measurement. | Avoid immediate production stack replacement. Test in isolated environment only after artifact grant and export equivalence checks. |
| WASB badminton | Official cross-sport high-resolution/temporal-consistency baseline; requires its own checkpoint adapter and coordinate/normalization contract. | MIT source LICENSE.md confirmed; official model zoo links a badminton checkpoint. Separate checkpoint/data distribution terms remain to verify before adoption. | No Test1 result. Published cross-sport study supports an independent challenger but supplies no direct rally-boundary evidence here. | Candidate second-opinion detector; measure same masks, source frames and boundary consumer before deciding. |

Approximate network-forward cost of overlapping current8-frame windows:60-frame input uses8windows atstep8,14 atstep4,53 atstep1. Whole-pipeline cost is not proportional because court/player/pose/OCR and CPU processing remain. Larger overlap does not guarantee a detection when the shuttle is physically outside the image. A high-resolution model does not solve end-state semantics by itself.

## Primary sources and pinned revisions

Fetched only small upstream documentation/license files into `artifacts/benchmarking/investigation/audit_c/external_sources/` for this audit, outside production packages. The adjacent `manifest.json` records pinned raw URLs and SHA256 digests. No external implementation was imported or installed.

| Source | Pinned revision | Facts verified |
| --- | --- | --- |
| [Official TrackNetV3](https://github.com/qaz812345/TrackNetV3) | `6eda442ada1740573f200f836d93edc9a541ee86` | Eight-frame concat training recipe, auxiliary background, separate InpaintNet, explicit checkpoint license grant in README/LICENSE. |
| [Official TrackNetV4](https://github.com/TrackNetV4/TrackNetV4) | `cb7eea7988474771ceac7e880bbffc35bfa87bca` | TensorFlow implementation, motion-attention variants, official result/checkpoint links, MIT source. |
| [Official WASB](https://github.com/nttcom/WASB-SBDT) | `923462cacdeb3353b84ddebdedb3f4b7a8553b0f` | Multi-sport detection/tracking evaluation, badminton model-zoo link, MIT LICENSE.md. |
| [Official RacketVision](https://github.com/OrcustD/RacketVision) | `c44af2a08524d3cb54d818f19686f4cdea4d2793` | BallTrack based on TrackNetV3;4-frame512×288 config; official model-download references; MIT repository license. |
| [Author-linked RacketVision model files](https://huggingface.co/linfeng302/RacketVision-Models/tree/a3760773233a0988c9605259743fbdd87c59d3a3) | `a3760773233a0988c9605259743fbdd87c59d3a3` | `checkpoints/balltrack_best.pth` is listed. HF API returned no cardData/license metadata; weights were not fetched. |

Specific primary documentation: [TrackNetV3 license](https://github.com/qaz812345/TrackNetV3/blob/6eda442ada1740573f200f836d93edc9a541ee86/LICENSE), [TrackNetV4 results](https://github.com/TrackNetV4/TrackNetV4/blob/cb7eea7988474771ceac7e880bbffc35bfa87bca/docs/RESULT.md), [TrackNetV4 source license](https://github.com/TrackNetV4/TrackNetV4/blob/cb7eea7988474771ceac7e880bbffc35bfa87bca/LICENSE), [WASB model zoo](https://github.com/nttcom/WASB-SBDT/blob/923462cacdeb3353b84ddebdedb3f4b7a8553b0f/MODEL_ZOO.md), [WASB source license](https://github.com/nttcom/WASB-SBDT/blob/923462cacdeb3353b84ddebdedb3f4b7a8553b0f/LICENSE.md), [RacketVision BallTrack contract](https://github.com/OrcustD/RacketVision/blob/c44af2a08524d3cb54d818f19686f4cdea4d2793/source/BallTrack/README.md).

## Why backbone replacement is not yet the strongest intervention

Observed Test1 failure chains include a temporary upper-image disappearance duringGT20, a likely static court-line attractor atGT27, and fragments separated by gaps. A stronger detector might improve weak or ambiguous locations, but cannot observe a physically out-of-view shuttle. Current trajectory interpolation also does not feed independent-observation evidence to the FSM. Fixing a detector alone could leave the same17-frame continuation failure intact. Conversely, an unsafe merge rule could improve this video's IoU while joining legitimate separate rallies. These are distinct causal questions requiring separate ablations.

The most informative sequence is: preserve the original detector; measure an uncertainty-aware continuation change with exact cached observations; add bounded peak/candidate diagnostics; then conduct pairedstep8/4 sampling and alternative-model experiments. Each challenger must retain raw candidate provenance, court masking, source-frame timestamps, single/doubles capability declarations and an explicit unavailable-provider outcome.

## Required controlled comparison

1. Freeze source/video/label/proxy hashes, baseline checkpoint, matching protocol and stage configuration. Test1 remains exploratory development data.
2. Obtain a small independently reviewed set of shuttle-location/visibility labels around the diagnosed fragments plus correct controls. Rally CSV labels alone cannot establish detector localization precision or confidence calibration.
3. Run paired windows with fixed background/masks on the same images. Log peak, second peak, rejected threshold/mask, per-window votes, runtime and peak VRAM. Distinguish source nonvisibility from detector false negatives.
4. Compare localization and continuity first, then full production inference with unchanged segmentation to measure detector-only effect. Run segmentation-only and combined ablations separately.
5. Report all detection, start/end bias/MAE/P90/max, duration and fragmentation metrics alongside cost. Do not promote only a matched IoU improvement.
6. Require independent held-out annotated video before default replacement; include amateur view, doubles, top-of-frame flight, stationary spare shuttles and white line/background distractors where independently labeled evidence is available.

No extra models, environment replacement, fabricated predictions, or production edits were made in this audit.

## Actual controlled follow-up: existing TrackNet step8 versus step4

This follow-up was run after the diagnosis gate at Git revision `3859f832fcb05d8c2560d3ed665e971ad263d954`. It is **real CUDA FP16 inference**, not the earlier synthetic window-contract test, and it evaluates the existing checkpoint rather than an alternative pretrained model. Production TrackNet source and the frozen baseline were unchanged. The orchestrator's concurrent FSM edits do not enter this component experiment.

Reproduction script: `research/audit_c_paired_inference.py`. Evidence: `artifacts/benchmarking/experiments/tracknet_window_pair/{manifest.json,case_metrics.json,metrics.json,observations_step8.csv,observations_step4.csv,execution.log,frozen_background.png}`. The script refuses to overwrite the experiment directory.

```bash
source ../gpu-env.sh
CUDA_VISIBLE_DEVICES=1 python research/audit_c_paired_inference.py
```

Physical GPU1 was confirmed idle before execution; the environment exposes it as logicalCUDA0. It was released at completion. The first GPU was left free. Model runtime confirms torch-cuda, torch.float16 and no fallback; checkpointSHA256 remains `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a`.

### Controlled inputs and interpretation

Twelve fixed180-frame windows (2,160frames per strategy) cover GT2,5,19,20,23,25,27,28,29,31 plus control cases7 and32 from the55 recorded failure packages. Case annotations select the review windows only; no annotated boundaries, target counts or positions are passed to the detector. Exact frame ranges and case-file/input/cache/checkpoint hashes are in the manifest.

Within every pair, decoded720p proxy frames, cached camera-shot IDs, production `flight_mask` masks reconstructed from the fixed baseline calibration, checkpoint, threshold0.5, FP16 and batch4 are identical. Only temporal window step changes8→4. Inference order alternates across cases. Background is one immutableRGB median from24 uniformly sampled proxy frames; rolling updates are disabled identically in both strategies. This freezes a confound but differs from the original baseline's rolling background. The180-frame window context also differs from the baseline's60-frame chunks. Consequently, this is a paired **component** experiment, not a rerun of the original detector context or a full rally benchmark.

| Measure | Step8 | Step4 |
| --- | ---: | ---: |
| Real input/output frames | 2160 | 2160 |
| Accepted detections (coverage, not recall) | 1582 | 1567 |
| Accepted fraction | 73.24% | 72.55% |
| Total component walltime | 20.355s | 29.722s |
| Aggregate component throughput | 106.11frames/s | 72.67frames/s |
| Peak CUDA allocated bytes | 1,133,421,056 | 1,133,421,056 |
| Peak CUDA reserved bytes | 1,874,853,888 | 1,874,853,888 |

Step4 cost1.46× the measured component walltime. Timings include preparation, actual model forwards and coordinate extraction, but exclude video decoding, model loading, background construction and other pipeline stages. A first8-frame warmup was excluded; differing final batch shapes and short-window timing noise remain limitations. These component rates must not be presented as full-pipeline rates.

| Review case | Step8 accepted /180 | Step4 accepted /180 | Step4-only / step8-only accepted frames | Median / maximum shared-point disagreement (proxy px) |
| --- | ---: | ---: | --- | --- |
| GT2 | 136 | 136 | 0 /0 | .271 /2.320 |
| GT5 | 127 | 126 | 0 /1 | .272 /1.766 |
| GT19 | 130 | 124 | 2 /8 | .274 /12.829 |
| GT20 | 131 | 131 | 2 /2 | .300 /5.004 |
| GT23 | 140 | 140 | 0 /0 | .276 /2.162 |
| GT25 | 118 | 114 | 0 /4 | .343 /5.135 |
| GT27 | 142 | 143 | 2 /1 | .335 /21.963 |
| GT28 | 44 | 43 | 1 /2 | .227 /2.907 |
| GT29 | 140 | 142 | 2 /0 | .365 /35.736 |
| GT31 | 131 | 132 | 1 /0 | .284 /204.508 |
| Control GT7 | 177 | 174 | 0 /3 | .262 /4.771 |
| Control GT32 | 166 | 162 | 1 /5 | .271 /2.233 |

The large204.5px maximum disagreement in GT31 means candidate identity can change abruptly even when most shared predictions barely move. Neither candidate can be called correct from these results without independent shuttle-location labels. More accepted outputs are not automatically better outputs.

### The two decisive regions

- **Upper-image gap9526–9542:** both strategies accept **0/17** detections. Overlapping windows do not recover this diagnosed temporary observation loss. Original-frame/trajectory evidence supports upper-image flight; component inference alone cannot prove physical invisibility.
- **Baseline static T cluster12748–12768:** both strategies accept **0/21** detections under the common fixed background/window context. Thus step4 is not responsible for removing the old static T predictions: step8 also removes them under these controls. Background and chunk context differ from the original run, so their separate contributions require a further controlled factorial experiment. Missing coordinates here also do not demonstrate recovered correct shuttle locations.
- Step4 does not uniformly reduce dropouts. Counts of≥10-frame missing runs stay unchanged in the ten selected failure windows and control7; control32 gains one such run (0→1). This argues against changing overlap as the default solely to improve coverage.

No rally CSV or F1 improvement is claimed from these component outputs. They contain per-frame positions/confidence/visibility with original indices; the primary seven-column rally schema and matching protocol were untouched. Retain step8 while investigating the proven continuation mechanisms. If pursuing perception improvements, isolate background construction, chunk alignment and temporal peak association before adopting an overlap policy or new backbone. A held-out localization/boundary evaluation remains required.
