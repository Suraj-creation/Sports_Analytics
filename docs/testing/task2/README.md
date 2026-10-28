# Task 2 cached semantic replay

The before and after JSON reports are verbatim copies of the replay summaries. Their provenance includes the engine source hash, media hashes and cached-observation hashes. The before implementation is revision `d932684`; the after report captures the working-tree implementation used in the original run. The saved source paths point to the original temporary directory and are historical provenance, not portable paths. The engine hash does not by itself identify every dependency or uncommitted source file: retain the corresponding working-tree changes to reproduce the after implementation.

These reports replay cached perception into fresh temporary event stores using CPU. They are semantic regression evidence, not human labels, shot accuracy metrics or a new GPU inference benchmark. They use initial calibration and do not apply human corrections. They do not modify historical session results. Changed cached data, session catalogue, dependencies or working-tree implementation can alter results; compare the source and input hashes in each new summary before comparing outputs. Durations and timestamps naturally vary.

From the repository root on the GPU server, with the existing environment and cached data available:

```bash
source ../gpu-env.sh
task2_replay_dir=$(mktemp -d /tmp/bai-task2-replay.XXXXXX)
mkdir "$task2_replay_dir/baseline-source"
git archive d932684 sports/badminton/src engine/src | tar -x -C "$task2_replay_dir/baseline-source"
PYTHONPATH="$task2_replay_dir/baseline-source/sports/badminton/src:$task2_replay_dir/baseline-source/engine/src" .venv/bin/python research/replay_cached_observations.py --data-dir data --output-dir "$task2_replay_dir/before" --implementation-label task2-baseline
PYTHONPATH="$PWD/sports/badminton/src:$PWD/engine/src" .venv/bin/python research/replay_cached_observations.py --data-dir data --output-dir "$task2_replay_dir/after" --implementation-label task2-working-tree
```

Each `--output-dir` is fresh and outside source sessions. The script writes a `summary.json`, `manifest.json`, and isolated event stores there. Inspect the summaries and the event stores rather than copying or overwriting them into the session data directory. Reproduction uses the current replay script and working tree, so it is a comparable run only if the relevant code, cache inputs and environment are the same.
