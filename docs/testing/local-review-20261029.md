# Review of `fix/pipeline-tracking-reliability` — real-clip probes and identity repair

Reviewed at `c929301` on the GTX 1080 Ti server (second GPU only, `gpu-rtx4000` profile, ONNX
Runtime CUDA / torch cu126). The server's own checkout and running services were not touched; all
work ran in a separate clone. Nothing here is precision/recall: no labelled ground truth was
available for these clips, so every number is a coverage or consistency diagnostic.

## Verification of the PR as submitted

| Check | Result |
| --- | --- |
| Full Python suite (`engine`, `sports/badminton`, `agents`, `apps/api`, `research`) | 1039 passed, 28 warnings, 208 s |
| Real inference completes end to end (16 s singles clip) | yes: status `analysed`, no degraded stages |

Tests passing does not establish the numbers below; they come from `research/evaluation/run_clip_probe.py`
(added here), which runs the real `SessionRunner` on a clip in an isolated data directory.

## Real-clip diagnostics (PR code, before the identity change)

| Clip | Frames | Boxes/frame (hist.) | Distinct track IDs | Poses valid (17×3, finite) | Shuttle visible | Implausible shuttle steps | Strokes (unknown) |
| --- | ---: | --- | ---: | --- | ---: | ---: | --- |
| Singles, 30 fps, 16 s | 479 | 2: 450, 1: 24 | 6 | 454/454 | 19.8 % | 0/80 | 2 (2) |
| Doubles footage, 25 fps, 120 s (run with a *singles* roster by mistake: identity ambiguity events and zero strokes are not representative) | 2999 | 4: 1644, 3: 97 | 18 | 4672/4672 | 33.3 % | 13/959 | 0 |
| Doubles, 60 fps, 120 s | 7199 | 1–6 | 62 | 4349/4349 | 21.1 % | 7/1433 | 7 (6) |

Conclusions supported by these runs: detection and pose now execute and emit structurally valid
output on real footage; the shuttle is seen in only ~20–33 % of frames; track IDs fragment heavily
(2 players → 6 IDs in 16 s; 62 IDs in 120 s of doubles); most strokes are honestly `unknown`.

## Defect found and repaired: permanent loss of singles identity after one track break

`IdentityResolver.assign` refused to bind a participant to a new track once that participant had
*ever* been bound (`bound_pids` included dead tracks). On the singles clip the far player's track
ended at frame 137 and was reborn as track 2 seven frames later; from then on every body had
`player_id=None`, so named analytics (P2) covered 132 of 479 frames.

Repair (`sports/badminton/src/bai_badminton/identity.py`): a replacement track inherits the
participant only when its bound track is absent this frame, was last seen within 2 s, and exactly
one unbound candidate overlaps that last box (IoU ≥ 0.3) while no other candidate does. Such rows
carry `identity_method="spatial_rebind_v1"`. The default (`rebind_gap_frames=0`) keeps the old
behaviour; the engine enables it for singles. Side alone or colour alone still never re-binds.
Three tests cover a unique successor, no overlap / beyond the gap, and two competing candidates.

Same 16 s clip, same models: P2 named frames 132 → 420 of 479 (all re-bound rows flagged); P1 stays
300 because its successor tracks did not meet the overlap evidence, so they remain unresolved.
Correctness of the re-bound identities is supported by position (far half, consistent mean y) and
has **not** been checked against labelled identities.

## Not fixed (needs data, retraining or hardware, or a design decision)

* Shuttle recall (20–33 % of frames). Earlier PR diagnostics show whole 17-frame windows with no
  observation; this is detector coverage and needs a recall benchmark on labelled shuttle positions.
* Shot classification: the active classifier is the heuristic `stroke_rules_v0` (pixel-speed and
  depth rules). There is no trained doubles model and no racket-contact detector. Calibrating it
  needs a labelled evaluation set; no thresholds were tuned here.
* Persisted shuttle rows carry only `visible` and `conf`. Interpolation stays inside the engine, so
  nothing interpolated is shown as observed, but "occluded / out of frame / inferred" are not
  represented as separate states.
* Profile files still declare models (BST stroke, racket pose, live/second-opinion shuttle) that the
  PR's own audit lists as not wired into the runtime.
* Doubles identity across crossings and track fragmentation (62 IDs / 120 s) remain unresolved.

## Reproduce

```sh
source ~/Desktop/sport-analytics/gpu-env.sh   # server only
python research/evaluation/run_clip_probe.py --source clip.mp4 --output /tmp/probe --runtime-root . [--format doubles]
```
