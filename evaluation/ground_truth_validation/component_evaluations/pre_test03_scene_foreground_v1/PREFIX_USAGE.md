# Bounded scene-only source controls

Launch only after the orchestrator freezes the new scene worktree and authorizes inference. The helper creates a new output directory with exclusive writes; failed outputs remain. It loads original dacc05e and frozen c7cf871 source implementations independently, hashes exact copied control files against their Git blobs, and guards candidate production source/configuration throughout the run. Model SHA and completed original proxy/cache catalogues must match.

```bash
source ../gpu-env.sh
export CUDA_VISIBLE_DEVICES=1
PYTHONPATH=/home/administrator/Desktop/sport-analytics/test03-scene-continuity-20261112/sports/badminton/src:/home/administrator/Desktop/sport-analytics/test03-scene-continuity-20261112/engine/src:/home/administrator/Desktop/sport-analytics/test03-scene-continuity-20261112/agents/src:/home/administrator/Desktop/sport-analytics/test03-scene-continuity-20261112/apps/api/src \
.venv/bin/python evaluation/ground_truth_validation/component_evaluations/pre_test03_scene_foreground_v1/probe_prefixes_v1.py
```

The execution directory is MAIN `Sports_Analytics`. ONNX device0 is physical GPU1 under this explicit visibility mask. Do not stop unrelated jobs or change model/profile settings. Root controls whether the GPU is available. `--test 1` or `--test 2` selects one dataset; default runs all ten specified bounded source windows across Tests1–2. `--output` must be an absent child of this diagnostic directory, e.g. `prefix_v2` for a retry. Do not overwrite `prefix_v1`.

Each case preserves all three arms, source frame/PTS/pixel hashes, detector crop hashes and predictions, current raw-content evidence including every region and supporting keys, exact layout decisions, player authority outputs and detached foreground outputs, frozen rate/geometry state, and source panels at acceptance instants. Existing exact source/crop detector observations are reused; missing proposals are inferred once per shared crop and counted separately from retained/shared reuses. Control arms do not use approximate membership rewrites or tracker-class monkeypatches.

The helper intentionally uses original recorded scheduling/geometry instead of downstream FSM feedback. It does not run pose, shuttle, contacts, classes, scoring, analytics, or end-to-end evaluation; no prefix result is a fresh full-video benchmark or independently labelled accuracy result. Fresh source guards and full Test1–2 evaluation remain required after these controls.
