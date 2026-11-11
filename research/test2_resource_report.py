"""Completed-run measurements with explicit worker/GPU and timing scopes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def worker_gpu_memory(rows: str, uuid: str, worker_pid: int) -> int | None:
    """Never sum another run or another process into this worker's peak."""
    for line in rows.splitlines():
        cells = [value.strip() for value in line.split(",")]
        if len(cells) != 3:
            raise ValueError("unexpected nvidia-smi compute-app sample")
        if cells[0] == uuid and cells[1] == str(worker_pid):
            return int(cells[2]) if cells[2].isdigit() else None
    return None


def report(run: Path, output: Path):
    info = json.loads((run / "inference.json").read_text())
    executor = json.loads(run.with_suffix(".executor.json").read_text())
    if info.get("status") != "completed" or executor.get("status") != "completed":
        raise ValueError("completed worker and parent receipts required")
    samples = [json.loads(line) for line in run.with_suffix(".gpu_process_samples.jsonl").open()]
    series = []
    for sample in samples:
        if "elapsed_s" not in sample:
            continue
        gpu = worker_gpu_memory(sample.get("rows", ""), executor["allocated_gpu_uuid"], executor["worker_pid"])
        series.append({**sample, "worker_gpu_mib": gpu})
    gpu = [row["worker_gpu_mib"] for row in series if row["worker_gpu_mib"] is not None]
    rss = [row["worker_tree_rss_bytes"] for row in series if "worker_tree_rss_bytes" in row]
    frames = info["frames_processed"]
    disk = {
        "total_logical_bytes": 0,
        "total_allocated_bytes": 0,
        "perception_logical_bytes": 0,
        "staged_model_logical_bytes": 0,
        "file_count": 0,
    }
    for path in run.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        stat = path.stat()
        disk["file_count"] += 1
        disk["total_logical_bytes"] += stat.st_size
        disk["total_allocated_bytes"] += stat.st_blocks * 512
        if "perception" in path.relative_to(run).parts:
            disk["perception_logical_bytes"] += stat.st_size
        if path.is_relative_to(run / "models"):
            disk["staged_model_logical_bytes"] += stat.st_size
    result = {
        "status": "completed",
        "run": str(run),
        "physical_gpu_index": executor["physical_gpu_index"],
        "allocated_gpu_uuid": executor["allocated_gpu_uuid"],
        "worker_pid": executor["worker_pid"],
        "frames": frames,
        "source_duration_s": frames * info["media"]["fps_den"] / info["media"]["fps_num"],
        "worker_elapsed_s": info["elapsed_s"],
        "executor_elapsed_s": executor["elapsed_s"],
        "worker_throughput_fps": frames / info["elapsed_s"],
        "executor_throughput_fps": frames / executor["elapsed_s"],
        "media_ready_s": info["media_ready_s"],
        "model_staging_s": info.get("model_staging_s"),
        "runner_stage_seconds": info.get("runner_stage_seconds", {}),
        "perception_stage_seconds": info["perception_stage_seconds"],
        "perception_stage_ms_per_source_frame": {
            key: value * 1000 / frames for key, value in info["perception_stage_seconds"].items()
        },
        "worker_cpu_s": info["worker_cpu_s"],
        "worker_maxrss_bytes": info["worker_maxrss_kib"] * 1024,
        "sampled_worker_tree_peak_rss_bytes": max(rss, default=None),
        "sampled_worker_gpu_peak_mib": max(gpu, default=None),
        "samples": len(samples),
        "sampling_error_count": sum("sampling_error" in row for row in samples),
        "disk": disk,
        "execution_backends": info["execution_backends"],
        "limitations": [
            "Both Test2 runs execute concurrently on separate physical GPUs, sharing CPU/RAM/storage.",
            "Timing is descriptive; historical Test1 concurrency and measurement scopes differ.",
            "Stage scopes overlap and must not be summed; per-frame values are not per-model invocation times.",
            "Component initialization includes model loading; no isolated model-only loading timer is claimed.",
            "GPU peak is sampled worker PID memory, excluding FFmpeg and other processes; it can miss short peaks.",
            "Tree RSS sums process RSS and may count shared pages more than once; exiting children may be absent.",
            "ORT provider lists do not establish per-node placement; no node-level profiler was enabled.",
            "Configured profile precision is requested precision; inspect staged ONNX graph types separately.",
        ],
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / "resource_measurements.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    axes[0].plot([s["elapsed_s"] for s in series], [s.get("worker_tree_rss_bytes", np.nan) / 2**30 for s in series])
    axes[0].set_ylabel("Worker tree RSS (GiB)")
    axes[1].plot(
        [s["elapsed_s"] for s in series],
        [s["worker_gpu_mib"] if s["worker_gpu_mib"] is not None else np.nan for s in series],
    )
    axes[1].set(xlabel="Executor elapsed seconds", ylabel="Worker GPU memory (MiB)")
    fig.suptitle(f"Test2 physical GPU {executor['physical_gpu_index']} resource samples")
    fig.tight_layout()
    fig.savefig(output / "resource_timeline.png", dpi=150)
    plt.close(fig)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(report(args.run.resolve(), args.output.resolve()), indent=2))
