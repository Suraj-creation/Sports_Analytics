"""Finish Test2 evaluation from a genuine completed native NN run into NEW output.

Never starts inference, alters producer ROOT, patches native functions, rewrites
an original failure receipt, deletes media, or advances to Test3. New navigation
links identify the actual original NN run; no NN execution is attributed here.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import subprocess
import time
import traceback
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def verify(mapping):
    for name, digest in mapping.items():
        if sha(name) != digest:
            raise ValueError("Protected input changed: " + name)


def native_environment(root):
    env = os.environ.copy()
    env["PYTHONPATH"] = ":".join(
        str(root / p) for p in ("sports/badminton/src", "engine/src", "agents/src", "apps/api/src", ".")
    )
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--producer-root", type=Path, required=True)
    args = parser.parse_args()
    source = args.run_root.resolve(strict=True)
    root = args.producer_root.resolve(strict=True)
    output = args.output.resolve()
    spec = importlib.util.spec_from_file_location("_comparison_tools", HERE / "run_pre_test03_regression.py")
    tools = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tools)
    tools.require_new_output(output, root)
    if source == output or source in output.parents or output in source.parents:
        raise ValueError("Postprocessing must be separate from original failed orchestration")
    preflight = read(source / "preflight.json")
    if preflight["test"] != 2 or Path(preflight["pipeline_root"]).resolve() != root:
        raise ValueError("Original producer and Test2 preflight binding required")
    worker, parent = read(source / "run/inference.json"), read(source / "run.executor.json")
    tools.require_completed(worker, parent, test=2)
    if sha(source / "run/inference.json") != parent["worker_report_sha256"]:
        raise ValueError("Worker differs from actual completed executor")
    if not (source / "failure.json").is_file() or (source / "completion.json").exists():
        raise ValueError("Requires preserved failed outer workflow, not an invented completion")
    sources = preflight["candidate_sources_sha256"]
    protected = preflight["protected_input_sha256"]
    verify(sources)
    verify(protected)
    if tools.git(root, "rev-parse", "HEAD").strip() != preflight["commit"]:
        raise ValueError("Original producer commit changed")
    if tools.git(root, "status", "--porcelain=v1") != preflight["git_status"]:
        raise ValueError("Original producer working tree changed")
    # The original outer failure and every retained artifact stay byte-identical.
    original = {str(p): sha(p) for p in sorted(source.rglob("*")) if p.is_file()}
    paths = tools.baseline_documents(2)
    baseline = {name: read(path) for name, path in paths.items()}
    source_tool_paths = [
        Path(__file__),
        HERE / "run_pre_test03_regression.py",
        HERE / "analyse_native_completed_run.py",
        HERE / "export_native_completed_heatmaps.py",
        TOOL_ROOT / "research/scene_epoch_audit_v3.py",
    ]
    tool_hashes = {str(p): sha(p) for p in source_tool_paths}
    output.mkdir(parents=True)
    dump(
        output / "continuation_manifest.json",
        {
            "schema": "native-completed-test2-postprocessing:v1",
            "started_utc": datetime.datetime.now(datetime.UTC).isoformat(),
            "original_NN_root": str(source),
            "original_run": str(source / "run"),
            "producer_root": str(root),
            "producer_commit": preflight["commit"],
            "postprocessing_tool_root": str(TOOL_ROOT),
            "new_neural_inference_here": False,
            "original_neural_inference_was_fresh": True,
            "original_outer_failure": read(source / "failure.json"),
            "original_outer_failure_rewritten": False,
            "native_ROOT_reassigned": False,
            "numeric_metric_or_threshold_change": False,
            "original_artifact_sha256": original,
            "tool_sha256": tool_hashes,
            "original_preflight_sha256": sha(source / "preflight.json"),
            "protected_input_sha256": protected,
            "producer_source_sha256": sources,
            "navigation_link_policy": "New output links point to original actual NN receipts; no original files added",
        },
    )
    for name in ("run", "run.executor.json", "environment.json", "preflight.json", "timestamps"):
        (output / name).symlink_to(source / name, target_is_directory=(source / name).is_dir())
    env = native_environment(root)
    executable = root / ".venv/bin/python"

    def call(script, arguments, name):
        start = time.monotonic()
        command = [str(executable), str(script), *map(str, arguments)]
        print(name + " started", flush=True)
        with (output / (name + ".log")).open("x") as stream:
            process = subprocess.run(  # noqa: S603 — explicit argv; native sources pinned above
                command, cwd=root, env=env, stdout=stream, stderr=subprocess.STDOUT
            )
        dump(
            output / (name + ".result.json"),
            {
                "command": command,
                "cwd": str(root),
                "returncode": process.returncode,
                "elapsed_s": time.monotonic() - start,
                "new_neural_inference": False,
                "PYTHONPATH": env["PYTHONPATH"],
                "producer_root": str(root),
            },
        )
        if process.returncode:
            raise RuntimeError(name + " failed; original and partial evidence preserved")
        print(name + " completed", flush=True)

    run = source / "run"
    session = read(run / "session.json")
    sid = session["session_id"]
    if not isinstance(sid, str) or not sid.isalnum() or session["source"]["sha256"] != worker["source_sha256"]:
        raise ValueError("Completed session/source identity required")
    adapter = HERE / "analyse_native_completed_run.py"
    shared = ["--run", run, "--producer-root", root, "--tool-root", TOOL_ROOT]
    started = time.monotonic()
    try:
        call(adapter, [*shared, "--output", output / "analysis"], "analysis")
        call(
            adapter,
            [
                *shared,
                "--mode",
                "components-test2",
                "--output",
                output / "bound_reference_diagnostics",
                "--coordinate-binding",
                tools.WORK / tools.SPEC[2]["binding"],
            ],
            "components",
        )
        call(
            root / tools.COMMON[3],
            [
                "--run",
                run,
                "--session",
                sid,
                "--reference",
                TOOL_ROOT / "Part2/dataset/Test2_Full/Test2_Full_rally.csv",
                "--output",
                output / "rally_reference_evaluation",
            ],
            "primary_evaluation",
        )
        call(root / tools.COMMON[-2], ["--run", run, "--output", output / "downstream_exports"], "downstream")
        call(
            root / tools.COMMON[4],
            [
                "--run",
                run,
                "--session",
                sid,
                "--output",
                output / "diagnostic_replay",
                "--trace-ranges",
                json.dumps([[0, 29296]]),
                "--focus",
                "",
            ],
            "semantic_replay",
        )
        semantic = read(output / "diagnostic_replay/replay_manifest.json")
        tools.require_semantic(semantic, test=2, source_report_sha=sha(run / "inference.json"))
        verify(
            {
                str(output / "diagnostic_replay" / name): digest
                for name, digest in semantic["output_artifact_sha256"].items()
            }
        )
        call(
            HERE / "export_native_completed_heatmaps.py",
            [
                "--run",
                run,
                "--downstream",
                output / "downstream_exports",
                "--output",
                output / "heatmap_exports",
                "--producer-root",
                root,
            ],
            "heatmaps",
        )
        comparison = tools.publish({"output": output, "baseline": baseline, "paths": paths}, 2)
        verify(sources)
        verify(protected)
        verify(original)
        verify(tool_hashes)
        artifacts = {
            str(p.relative_to(output)): sha(p)
            for p in output.rglob("*")
            if p.is_file()
            and not p.is_symlink()
            and p.suffix not in (".sqlite", ".mp4")
            and not p.name.endswith(("-wal", "-shm"))
        }
        dump(
            output / "completion.json",
            {
                "schema": "native-completed-test2-postprocessing-completion:v1",
                "status": "completed_postprocessing_of_original_fresh_run_root_review_pending",
                "test": 2,
                "frames": 29296,
                "source_sha256": worker["source_sha256"],
                "candidate_commit": preflight["commit"],
                "producer_root": str(root),
                "original_NN_root": str(source),
                "new_neural_inference": False,
                "original_neural_inference_was_fresh": True,
                "original_failed_outer_unchanged": True,
                "own_run_semantic_parity": True,
                "annotations_and_baselines_unchanged": True,
                "source_helpers_models_profile_frozen": True,
                "actual_model_identity_equal": comparison["actual_model_identity_equal"],
                "artifact_sha256": artifacts,
                "elapsed_postprocessing_s": time.monotonic() - started,
                "no_cleanup": True,
                "no_test3": True,
                "independent_physical_accuracy_claimed": False,
            },
        )
        print("Postprocessing completed; independent metric/visual/root acceptance still required", flush=True)
    except Exception as error:
        dump(
            output / "failure.json",
            {
                "status": "failed",
                "error": str(error),
                "traceback": traceback.format_exc(),
                "original_NN_root": str(source),
                "new_neural_inference": False,
                "partial_artifacts_preserved": True,
                "no_test3": True,
            },
        )
        raise


if __name__ == "__main__":
    main()
