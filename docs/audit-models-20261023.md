# Model decisions and hardware evidence — 23 October 2026

No new model or dependency was installed. The most defensible changes address
event acceptance, lineage and measurement policy before choosing stronger models.
Published benchmark scores do not establish accuracy on these wide CCTV recordings.

## Candidate matrix

| Task | Incumbent / candidate | License and weights | Integration / compatibility | Decision, limitation and validation gate |
|---|---|---|---|---|
| Shuttle trajectory | TrackNetV3 + optional InpaintNet | [Upstream MIT explicitly covers pretrained checkpoints](https://raw.githubusercontent.com/qaz812345/TrackNetV3/master/LICENSE); cached weights and hashes available | Existing Torch CUDA adapter; 8-frame context, background input; interpolation must be distinguished from observation | Retain. [Published model](https://github.com/qaz812345/TrackNetV3) uses trajectory/background evidence; label target-court shuttle visibility and pixel positions, evaluate localization+recall independently |
| Person detection | RF-DETR Small; cached Nano/Medium alternatives | Repository manifest records Apache-2.0 upstream and mirrored ONNX provenance; local bytes hashed in timing artifact | Already supported same detector interface; real CUDA timings below; no dependency change | Retain Small. Nano faster does not prove sufficient far-player recall. Annotate boxes on independent frames per camera/depth, then evaluate precision/recall and downstream identity switches |
| Tracking / four-person association | Current ByteTrack-style tracker + two-slot identity; MMTracking | [Apache-2.0, model zoo](https://github.com/open-mmlab/mmtracking); checkpoint/data terms require per-weight review | High integration cost. [Master requirements](https://raw.githubusercontent.com/open-mmlab/mmtracking/master/requirements/mminstall.txt) pin mmcv-full<1.7, mmdet<3 and mmcls<1; install into isolated experimental environment if investigated | Defer framework installation. Label four target players and occlusions; compare switches, fragmentation, attribution and unresolved rate. Toolbox presence alone does not solve match identity |
| Pose | Current RTMPose-M ONNX; MMPose larger variants | [MMPose Apache-2.0 and pretrained model catalog](https://github.com/open-mmlab/mmpose); existing M/X artifacts cached | Current ONNX adapter avoids adding whole training framework; crops depend on detection/association | Retain M. Review wrists/ankles under blur and occlusion; test keypoint visibility/error and effect on contact timing before promoting a larger model |
| Temporal shot classification | Existing bounded-confidence rule preview; MMAction2 temporal / skeleton models | [MMAction2 Apache-2.0, pretrained zoo](https://github.com/open-mmlab/mmaction2); exact checkpoint and training dataset terms still require selection | High cost; generic action classes do not establish shuttle contact or badminton subtype. Needs task taxonomy and verified temporal labels | Research candidate only. Evaluate class confusion and abstention on independent rallies, including smash/jump, clear/lift and net/kill ambiguity; no generic weights promoted |
| Court / occlusion segmentation | Existing line fit and fixed-camera lock; SAM2.1 | [SAM2 code/checkpoints Apache-2.0 and official downloads](https://raw.githubusercontent.com/facebookresearch/sam2/main/README.md) | Requires Python>=3.10, Torch>=2.5.1; optional CUDA extension. Official examples use BF16 which requires adaptation on Pascal. Prompted segmentation is not calibrated court geometry | Defer. Suitable experiment: annotate court/person masks; test camera registration or occlusion assistance. Do not replace tiny-shuttle tracker with generic masks without localization evidence |
| Detector / pose alternative | Ultralytics YOLO family | [Upstream AGPL-3.0 or enterprise licensing](https://github.com/ultralytics/ultralytics#-license); model deployment terms require project review | Would add overlapping capabilities and potential runtime/licensing changes | Not adopted. Compare independent detector/pose evidence first; resolve exact weight license and deployment compatibility before integration |
| Racket/contact | Manifest candidates RacketVision / transformer stroke weights | Candidate names/URLs in existing manifest are declarations, not proof installed or evaluated | Racket candidate currently unwired; no detector-independent contact truth | Retain explicit limitation. Annotate racket/shuttle contact and visible wrists before adding another model |

Upstream source/license pages above were fetched during this audit. Repository activity
dates, support commitments and exact current release compatibility were not independently
verified for every candidate; no claim of active maintenance is made. Pin commits,
weight digests and dataset terms as part of any subsequent candidate promotion.

## Actual GPU measurements

Hardware is **GTX1080Ti**,11GiB per GPU, Torch2.14.1+cu126. The deployment profile's
name `gpu-rtx4000` does not change the physical GPU. These were small warm-cache
development samples, not sustained service capacity or a final model acceptance test.

Source `90d1f399c05312ede173de2f2c8cd2fee09f1d201df46b476119660a00039ff0`,
canonical frames0,900,3600,7200,12000,18000,22000; three warmups then two passes.
Full-frame detection precedes court admission; observed person counts include adjacent
courts and cannot be interpreted as precision/recall.

| Detector | p50ms | p95ms | Own-process GPU memory snapshot |
|---|---:|---:|---:|
| RF-DETR Nano384 |14.98|15.18|416MiB|
| RF-DETR Small512 |24.98|25.49|416MiB|
| RF-DETR Medium576 |32.28|33.07|674MiB|

These snapshots include retained allocations, not isolated peak VRAM. CUDA and CPU
providers were enabled; node-level placement would require ORT profiling. Local
weight SHA256s and all sampled timings are in
`testing/audit-20261023/detector-benchmark.json`.

Additional incumbent smoke timings using existing `docs/testing/run_benchmarks.py`
functions, with10 timed repetitions: TrackNetV3 mean83.91ms per8-frame window
(95.34fps; p95 89.87ms); RTMPose-M mean12.19ms per frame with two synthetic
person crops (82.03fps). These repeat a single real CCTV window/frame, so do not
measure accuracy or whole-video throughput. The old script's `vram_peak_mb` field
actually samples current Torch allocation after inference; its22.54MiB result is
**not** total or peak model memory and must not be used for capacity planning.

## Reproduce without disturbing the configured runtime

```sh
source ../gpu-env.sh
.venv/bin/python research/benchmark_cached_models.py --session 01M5EXGZNEVGYAJ3AR6CJS5ZG9
```

The reusable command refuses missing/ambiguous cached artifacts rather than downloading
weights. Complete runtime acceptance still needs sustained pipeline throughput,
per-process peak VRAM including ONNX allocations, simultaneous analysis load, bounded
queues/failure recovery and held-out labels. Model-accuracy improvements are not claimed.
