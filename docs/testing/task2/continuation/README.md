# Task 2: court and temporal evidence recovery

The 28 October continuation fixes three demonstrated defects in the existing processing path. It is an incremental implementation, with Task 2 still in progress.

## Changes

For a fixed cropped court, verification previously compared the refined fit at six full-court anchors, including the invisible near baseline. In Real Video frame 15, the refined fit retains strong painted-line support and differs by about 1.53 px at visible corners, but by 15.82 px at an offscreen corner. That exceeded the unchanged 15.24 px tolerance and repeatedly lost the court. The locked path now compares distinct reference-visible painted-line samples, checking projection denominators and degeneracy. It retains the exact locked geometry and rejects measured camera shifts or neighboring-court substitutions. The general search/deduplication comparison remains unchanged. The sampling is a consistency check, not a mathematical bound on every viewport pixel.

Contact fusion now uses valid wrists even if the nose is occluded, rejects nonfinite wrist coordinates/confidence, and derives wrist speed across intentionally unsampled pose frames. Every bridged frame must have a known positive schedule and continuous track boxes; a missing scheduled wrist, disabled/unknown cadence, or missing track interrupts the pair. Displacement is divided by the actual frame gap before the existing body-height normalization. Cadence follows the absolute frame schedule through perception, cache, buffers and participant views. Replay and fresh diagnostic tools preserve this metadata. Cache version 8 invalidates prior inference; old observations with unknown cadence retain only the legacy adjacent-frame motion path.

Fresh usable detector frames now advance participant coverage. Carried or missing frames do not extend it. When observations return after the existing two-second gap, the same numeric track gets a new epoch and birth provenance. Brief carries remain provisional. Empty unavailable frames report unknown person count rather than observed zero. These changes prevent unsupported identity continuity; they do not merge episodes into four verified people.

## Full-video GPU comparison

`fresh_session_benchmark.py` runs the application runner without a server or tunnel. It reads source session metadata/calibration through read-only SQLite connections, copies media into a fresh output directory, then runs new perception and semantic analysis there. The compared source, proxy and calibration hashes match. Baseline code is `a555260`; `implementation-manifest.json` records the changed source hashes. The original five event-ledger body hashes remained unchanged (`integrity-verification.json`).

Both versions completed all 4,462 Real Video frames on GPU 1 with the existing environment.

| Diagnostic | Before | After |
| --- | ---: | ---: |
| Valid court frames | 2,947 | 4,460 |
| Lost court frames | 1,111 | 0 |
| Reacquiring frames | 404 | 2 |
| Active-play frames | 7 | 2,499 |
| Rally candidates | 0 | 9 |
| Stroke/contact candidates | 0 / 0 | 42 / 42 |
| Unknown stroke labels | 0 candidates | 32 / 42 |
| Analysis wall time, seconds | 225.986 | 259.708 |
| Sampled peak process GPU memory, MiB | 2,126 | 2,128 |

The new run has more usable frames and more detector work (1,571 versus 857 detector-run frames). Timing includes model loading/seeding and overlapped CPU regression tests; it is a single-run resource diagnostic, not a controlled speed claim. Sampled GPU memory may miss peaks. Camera availability and event output are not labelled event accuracy.

On **identical new-run box/pose observations**, `pose_motion_availability.py` compared old and new wrist-motion calculations over 17,696 temporary-track local windows. Finite motion evidence was available in 10,251 before and 12,684 after: 2,433 additional windows. These are track/frame windows, not shots, verified hits or persistent identities.

## Visual inspection and limits

A model-guided AI review sampled source proxy frames 460–490 after observing the first recovered candidate labels. It did not establish exact contact, serve/push correctness, or a durable hitter identity. The source-bound draft is `../annotations/real-video-recovered-candidates-ai-review.json`; the source montage stays in the private evaluation folder. This review is non-exhaustive and not human-verified. No precision, recall, F1, class confusion or player-attribution accuracy can be calculated from it.

The remaining requirements need exhaustive contact/family/hitter labels and validation of four stable identities through crossings and occlusion. Current shot families and episode links remain provisional. A larger event count is not evidence of better classification accuracy. No new large model, learned classifier, runtime dependency or public service was introduced.

## Validation

The final server regression suite passed **740 tests**, with 27 existing FastAPI/Starlette deprecation warnings. Focused failing-first regressions cover cropped-court jitter, camera shifts, numerical projection failure, sparse pose scheduling, missing/invalid observations, cache rejection, detector outages and returned birth provenance. Changed Python files pass Ruff and `git diff --check`. The frontend and API contracts were not extended in this continuation; API regressions are included in the suite.

## Reproduction

Use a fresh output for each invocation. Existing outputs are refused; source paths may not overlap the output. From the isolated source checkout:

```bash
source /home/administrator/Desktop/sport-analytics/gpu-env.sh
export CUDA_VISIBLE_DEVICES=1
export PYTHONPATH="$PWD/engine/src:$PWD/sports/badminton/src"
/home/administrator/Desktop/sport-analytics/Sports_Analytics/.venv/bin/python \
  docs/testing/task2/continuation/fresh_session_benchmark.py \
  --source-data /home/administrator/Desktop/sport-analytics/Sports_Analytics/data \
  --session-id 01M5MBR3087FH07N5B1XR5VGHW \
  --output /tmp/fresh-real-video-evaluation --label current
```

For the baseline, archive `a555260`'s `engine/src` and `sports/badminton/src` into a separate folder and put those two source paths first in `PYTHONPATH`, using the same harness and a different fresh output. The saved full runs, source archive, original harness/logs, hashes and private montage are in `/home/administrator/Desktop/sport-analytics/task2-continuation.ZBsh8B/`. To reproduce the same-observation motion diagnostic, pass that directory to `pose_motion_availability.py`; it reads its `baseline-source/` and `real-after/data/` subdirectories.
