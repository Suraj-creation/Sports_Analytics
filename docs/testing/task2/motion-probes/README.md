# Task 2: bounded unlabelled motion diagnostics

These are source-bound component probes, **not accuracy benchmarks**. Contact candidates are hypotheses, not verified hits. The analysis uses no court calibration, rally segmentation, scorer identity, or flight evidence. Shot classification intentionally receives no supporting context and returns `unknown`; this does not establish the accuracy of the full application. The processed TrackNet detections are not verified shuttle positions. Pixel-per-second estimates are image motion, not physical speed.

| Recording | Clip (frames inclusive) | Processed frames | Shuttle detections | Candidate contacts | Available old/new motion |
| --- | --- | ---: | ---: | ---: | ---: |
| Test7 original | 180–449 at 30 fps | 270 | 254 | 12 | 11 / 11 |
| He/Ren vs Rankireddy/Shetty doubles proxy | 1500–1749 at 25 fps | 250 | 214 | 11 | 11 / 11 |
| Antonsen vs Farhan singles proxy | 1500–1749 at 25 fps | 250 | 219 | 9 | 9 / 8 |

The new estimator declined one singles candidate at frame 1711. Whether that candidate or rejection is correct is unknown. Test7's three AI-draft motion windows are neither confirmed contacts nor an exhaustive annotation; one candidate falls inside one window. Candidates outside the windows are not false positives. Source-bound coverage is in `test7-draft-coverage.json`.

Files ending in `observations.json` contain cached per-frame shuttle observations and candidate frames, checkpoint and implementation hashes, video SHA-256, and inference timings. `before.json` and `after.json` are outputs from the actual old and new engine motion methods applied to that **same** saved input; `comparison.json` pairs results per frame. This isolates the motion method only: it does not re-run changed contact detection or test full before/after shot classification. The Test7 observation candidates were generated with baseline code; the two other observations used the modified snapshot. All candidates then remain frozen for both motion methods.

The old implementation came from commit `b480584`; engine SHA-256 `32962f5f34b384a6f90c705e3ec117a34feb9d83225a1050a937a5c3d570f505`, stroke SHA-256 `2d0ab87fcceabd49b44d446278cd146c284c728f3e1e376a4414ea71fda5cbe2`. The new snapshot had engine SHA-256 `31b6dc17fb85088b6d12823bacfe63295c7b34196392ec986dd0ec51d4779689` and stroke SHA-256 `875b7239b6ccf662ca2489260c53da5d17ca7779c19380b2fa77ab7f0a7ac8aa`. Check both files against the report before reproducing; a subsequent code change can produce different results.

Inputs on the configured server:

- `data/task2-review/Test7_Full.mp4`, SHA-256 `1ad1eac44150a0a23e2bad1f3d4204bd41f2d257ff6b35156234d38cfa2b9d9c`.
- `data/media/f9a419327a85b4e17d524d2fae24245ae9fc862b06a05c8fc11ed457eb487cba/proxy.mp4`, SHA-256 `205132cc64f0d269ca67bd0eea1dfc9e08352f68202cdb8754a19a58217d958f`.
- `data/media/314b4997fde9670c17cde76a256ff64c9a5f565317078f1d9826f5ffee8602c0/proxy.mp4`, SHA-256 `a940a9441d48eb09d758b82dc7f53bdb4a1dac9c69b4e7c7e67cffcbe5486d54`.

Replaying saved observations is CPU-only and does not update session results. From the repository, source `../gpu-env.sh`, then set `PYTHONPATH` to an isolated snapshot's `engine/src` and `sports/badminton/src` and run:

```sh
.venv/bin/python research/evaluation/inspect_shuttle_motion.py \
  --probe docs/testing/task2/motion-probes/test7-observations.json \
  --video data/task2-review/Test7_Full.mp4 > /tmp/test7-motion.json
```

Repeat with the other implementation and compare with `research.evaluation.inspect_shuttle_motion.compare_motion`; it validates the matching probe hash, video hash, candidate frames and timing. Obtain the old source via `git archive b480584 engine/src sports/badminton/src` into an isolated directory. Extract or snapshot the new version separately, verify the listed source hashes, and never overwrite active sessions. To recreate observations, run `research/evaluation/fresh_component_diagnostic.py --help` with the listed source, frame bounds, model checkpoints from the existing cache, and `--include-observations`, after confirming GPU availability and setting `CUDA_VISIBLE_DEVICES`. The GPU1 runs took 12.12 s, 11.81 s and 9.90 s respectively including model load; sampled process peaks were 1376, 1378 and 1376 MiB. These timings are isolated diagnostic timings, not end-to-end throughput.

Reliable accuracy evaluation still requires independent, human-reviewed and exhaustive contact times, shot categories and player identities for the same clips, including no-contact intervals and documented matching tolerances. Existing per-rally Part2 labels cannot supply those per-shot targets.
