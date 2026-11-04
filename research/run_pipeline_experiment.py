"""Fresh full-video production experiment with isolated evidence and telemetry.

The worker has no annotation argument and reads no annotation values. The parent
evaluates only after the worker has durably written production predictions.
"""

from __future__ import annotations

import argparse
import collections
import importlib.metadata
import json
import os
import subprocess
import sys
import threading
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.benchmarking.production_inference import digest, dump  # noqa: E402


def worker(video, output):
    import psutil

    from bai_engine.bus import LocalBus
    from bai_engine.config import Settings
    from bai_engine.runtime.registry import ModelRegistry
    from bai_engine.runtime.runner import SessionRunner
    from bai_engine.schema import Session, SessionStatus, Source, SourceKind
    from bai_engine.store import SessionRepository

    stages = collections.defaultdict(float)
    samples = []
    stop = threading.Event()
    process = psutil.Process()
    process.cpu_percent()

    def sample():
        with (output / "resources.jsonl").open("x") as stream:
            while not stop.is_set():
                row = {
                    "elapsed_s": time.monotonic() - started,
                    "process_cpu_percent": process.cpu_percent(),
                    "process_rss_bytes": process.memory_info().rss,
                }
                try:
                    result = subprocess.check_output(
                        ["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"],
                        text=True,
                        timeout=5,
                    )
                    row["process_gpu_memory_mib"] = sum(
                        float(line.split(",")[1])
                        for line in result.splitlines()
                        if line.split(",")[0].strip() == str(os.getpid())
                    )
                except (subprocess.SubprocessError, ValueError, OSError) as exc:
                    row["gpu_sample_error"] = type(exc).__name__
                samples.append(row)
                stream.write(json.dumps(row) + "\n")
                stream.flush()
                stop.wait(2)

    class ObservedRunner(SessionRunner):
        def _create_sport(self):
            sport = super()._create_sport()
            original_scene = sport.perception._scene
            original_ingest = sport.ingest

            def scene(*args, **kwargs):
                before = time.monotonic()
                try:
                    return original_scene(*args, **kwargs)
                finally:
                    stages["court_scene_wall_seconds"] += time.monotonic() - before

            def ingest(*args, **kwargs):
                before = time.monotonic()
                try:
                    return original_ingest(*args, **kwargs)
                finally:
                    stages["semantic_ingest_wall_seconds"] += time.monotonic() - before

            sport.perception._scene = scene
            sport.ingest = ingest
            return sport

        def _perceive(self, *args, **kwargs):
            before = time.monotonic()
            try:
                return super()._perceive(*args, **kwargs)
            finally:
                stages["decode_perception_cache_wall_seconds"] += time.monotonic() - before

    data = output / "runtime"
    data.mkdir(exist_ok=False)
    sha = digest(video)
    repo = SessionRepository(data)
    sid = "Test1Experiment"
    repo.save(
        Session(
            session_id=sid,
            title="Exploratory Test 1 rally experiment",
            profile="experiment",
            source=Source(kind=SourceKind.UPLOAD, uri=str(video), original_name=video.name, sha256=sha),
        )
    )
    settings = Settings(
        _env_file=None,
        data_dir=data,
        models_dir=ROOT / "models",
        profiles_dir=output / "profiles",
        profile="experiment",
        proxy_height=720,
    )
    registry = ModelRegistry(settings.models_dir)
    runner = ObservedRunner(sid, repo, LocalBus(), settings, registry)
    started = time.monotonic()
    monitor = threading.Thread(target=sample, daemon=True)
    monitor.start()
    try:
        before = time.monotonic()
        runner._ensure_media()
        stages["media_ready_wall_seconds"] = time.monotonic() - before
        runner._analyse()
        if runner._transcode_thread:
            runner._transcode_thread.join(timeout=60)
            if runner._transcode_thread.is_alive():
                raise RuntimeError("media job still running")
        state = repo.get(sid)
        if state is None or state.status is not SessionStatus.ANALYSED or state.frontier_frame != 17267:
            raise RuntimeError(f"incomplete production inference: {state}")
        events = repo.events(sid).query()
        ends = sorted((e for e in events if e.type == "rally_end"), key=lambda e: (e.frame_start, e.frame_end))
        from scripts.benchmarking.evaluate_rallies import write_predictions

        write_predictions(
            output / "predicted_rallies.csv", [(e.frame_start, e.frame_end) for e in ends], float(state.media.fps)
        )
        with (output / "events.jsonl").open("x") as stream:
            for event in repo.events(sid).query(live_only=False):
                stream.write(event.model_dump_json() + "\n")
        stats = runner.sport.perception.stats
        import torch

        resource = {
            "sampling_interval_s": 2,
            "samples": len(samples),
            "peak_process_rss_bytes": max((s["process_rss_bytes"] for s in samples), default=None),
            "mean_process_cpu_percent": sum(s["process_cpu_percent"] for s in samples) / len(samples)
            if samples
            else None,
            "peak_sampled_process_gpu_memory_mib": max(
                (s.get("process_gpu_memory_mib", 0) for s in samples), default=None
            ),
            "torch_peak_allocated_bytes": torch.cuda.max_memory_allocated() if torch.cuda.is_initialized() else None,
            "scope_note": (
                "CPU/RSS=current worker process; GPU=nvidia-smi current PID sum, sampled not instantaneous peak; "
                "Torch allocator excludes ORT/FFmpeg. CPU percent may exceed100 for multiple cores."
            ),
        }
        dump(
            output / "inference.json",
            {
                "status": state.status.value,
                "elapsed_seconds": time.monotonic() - started,
                "frames_per_second": state.media.n_frames / (time.monotonic() - started),
                "media": state.media.model_dump(mode="json"),
                "frontier_frame": state.frontier_frame,
                "configured_chunk_frames": runner.sport.perception.profile.chunk_frames,
                "effective_chunk_frames": runner.plan.frames_per_segment,
                "per_stage_seconds": {**stages, **{f"perception_{k}": v for k, v in stats.seconds.items()}},
                "timing_note": (
                    "Stage wall aggregates overlap (parent/child) and must not be summed; "
                    "no extra CUDA synchronization inserted."
                ),
                "resources": resource,
                "pipeline": runner.sport.describe_pipeline(),
                "effective_profile": runner.sport.perception.profile.model_dump(mode="json"),
                "execution_backends": runner.sport.perception.runtimes,
                "degraded": runner.sport.degraded(),
                "models": registry.status(),
                "event_counts": dict(collections.Counter(e.type for e in events)),
                "rally_events": [
                    {
                        "start": e.frame_start,
                        "end": e.frame_end,
                        "end_reason": e.payload.get("end_reason"),
                        "event_id": e.event_id,
                    }
                    for e in ends
                ],
                "proxy_sha256": digest(repo.media_paths(sha).proxy),
            },
        )
        print(f"FRESH_INFERENCE_COMPLETE {len(ends)} intervals", flush=True)
    finally:
        stop.set()
        monitor.join(timeout=6)
        if runner.sport:
            runner.sport.close()
        repo.close()


def main():
    import yaml

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--video", type=Path, default=ROOT / "data/benchmarking/test1/Test1_Full_rev.mp4")
    parser.add_argument("--rally-implementation", default="rally-fsm-v1")
    parser.add_argument("--rally-params", type=json.loads, default={})
    parser.add_argument("--shuttle-step", type=int, choices=[1, 4, 8], default=8)
    parser.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if args.worker:
        worker(args.video.resolve(), output)
        return
    output.mkdir(parents=True, exist_ok=False)
    baseline = ROOT / "outputs/benchmarking/test1"
    base_metadata = json.loads((baseline / "benchmark_metadata.json").read_text())
    if digest(args.video) != base_metadata["source_video_sha256"]:
        raise ValueError("not the frozen Test 1 source")
    profile = yaml.safe_load((baseline / "profiles/gpu-rtx4000.yaml").read_text())
    profile.setdefault("components", {})["rally"] = {
        "model": "none",
        "backend": "none",
        "implementation": args.rally_implementation,
        "params": args.rally_params,
    }
    profile["shuttle"]["params"]["step"] = args.shuttle_step
    (output / "profiles").mkdir()
    (output / "profiles/experiment.yaml").write_text(yaml.safe_dump(profile, sort_keys=False))
    source_files = {
        str(p.relative_to(ROOT)): digest(p)
        for root in ("engine/src", "sports/badminton/src")
        for p in sorted((ROOT / root).rglob("*.py"))
    }
    metadata = {
        "status": "running",
        "exploratory": True,
        "dataset_role": "development; no held-out claim",
        "execution_date": datetime.now(UTC).isoformat(),
        "git_commit_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "active_branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
        "source_hashes": source_files,
        "runner_sha256": digest(Path(__file__)),
        "source_video_sha256": base_metadata["source_video_sha256"],
        "ground_truth_sha256": base_metadata["ground_truth_sha256"],
        "ground_truth_path": base_metadata["ground_truth_path"],
        "video_fps": 30,
        "frame_count": 17268,
        "configuration": profile,
        "baseline_commit": "b773e20c62d1c398cddc3d23510bd4adf823325b",
        "baseline_metrics": base_metadata["artifact_hashes"]["metrics.json"],
        "runtime_versions": {
            name: importlib.metadata.version(name) for name in ["torch", "numpy", "scipy", "av", "onnxruntime-gpu"]
        },
    }
    dump(output / "benchmark_metadata.json", metadata)
    (output / "source.diff").write_text(
        subprocess.check_output(["git", "diff", "HEAD", "--", "engine", "sports"], cwd=ROOT, text=True)
    )
    try:
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--worker",
            "--video",
            str(args.video.resolve()),
            "--output",
            str(output),
        ]
        with (output / "execution.log").open("x") as stream:
            stream.write("Command: " + json.dumps(command) + "\n")
            stream.flush()
            subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)
        if any(digest(ROOT / name) != value for name, value in source_files.items()):
            raise RuntimeError("production source changed during inference")
        if digest(args.video) != base_metadata["source_video_sha256"] or (
            digest(ROOT / base_metadata["ground_truth_path"]) != base_metadata["ground_truth_sha256"]
        ):
            raise RuntimeError("source or annotations changed during inference")
        from scripts.benchmarking.evaluate_rallies import read_csv, save_evaluation

        gt = read_csv(ROOT / base_metadata["ground_truth_path"], 30)
        pred = read_csv(output / "predicted_rallies.csv", 30)
        metrics = save_evaluation(output, gt, pred, 30)
        metadata.update(
            status="completed",
            prediction_sha256=digest(output / "predicted_rallies.csv"),
            inference=json.loads((output / "inference.json").read_text()),
        )
        dump(output / "benchmark_metadata.json", metadata)
        from research.compare_rally_experiments import compare_experiment

        compare_experiment(output, baseline)
        print(json.dumps(metrics["detection"], indent=2))
    except Exception as exc:
        metadata.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        dump(output / "benchmark_metadata.json", metadata)
        raise


if __name__ == "__main__":
    main()
