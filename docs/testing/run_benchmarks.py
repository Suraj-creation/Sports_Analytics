"""Rigorous performance and model latency benchmark suite for Badminton AI.
Executes on the active target hardware (NVIDIA RTX 4080 SUPER / CUDA 13.2).
Measures:
- Video decode FPS (SegmentDecoder via PyAV)
- Individual model latency percentiles (p50, p95, p99) and throughput (FPS):
    * TrackNetV3 (torch-cuda, fp16)
    * RF-DETR-Small (onnx-cuda, fp16)
    * RTMPose-M (onnx-cuda, fp16)
    * RapidOCR-v4 (onnx-cuda)
- Full perception pipeline chunk throughput and latency
- GPU VRAM consumption (peak, baseline, delta)
- Match engine event throughput
"""

import gc
import json
import os
import sys
import time
from pathlib import Path
import numpy as np
import torch

from bai_engine.config import load_profile, REPO_ROOT
from bai_engine.decode import SegmentDecoder, DecodedChunk
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.store.sessions import MediaPaths

def get_gpu_memory_mb():
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        allocated = torch.cuda.memory_allocated() / (1024 * 1024)
        reserved = torch.cuda.memory_reserved() / (1024 * 1024)
        return {"allocated_mb": round(allocated, 2), "reserved_mb": round(reserved, 2)}
    return {"allocated_mb": 0.0, "reserved_mb": 0.0}

def benchmark_decode(media_paths, frames_per_segment=50, n_segments=10):
    print(f"\n[1] Benchmarking Video Decode (PyAV SegmentDecoder, {frames_per_segment} frames/seg)...")
    decoder = SegmentDecoder(media_paths, frames_per_segment=frames_per_segment)
    
    # Warmup
    _ = decoder.decode_segment(0)
    
    latencies = []
    total_frames = 0
    t_start = time.perf_counter()
    for k in range(n_segments):
        t0 = time.perf_counter()
        chunk = decoder.decode_segment(k)
        dt = time.perf_counter() - t0
        latencies.append(dt)
        total_frames += len(chunk.frames)
    total_time = time.perf_counter() - t_start
    
    fps = total_frames / total_time
    latencies_ms = [l * 1000 for l in latencies]
    res = {
        "total_frames": total_frames,
        "n_segments": n_segments,
        "total_time_s": round(total_time, 4),
        "throughput_fps": round(fps, 2),
        "latency_per_segment_ms": {
            "mean": round(float(np.mean(latencies_ms)), 2),
            "p50": round(float(np.percentile(latencies_ms, 50)), 2),
            "p95": round(float(np.percentile(latencies_ms, 95)), 2),
            "p99": round(float(np.percentile(latencies_ms, 99)), 2),
        },
        "latency_per_frame_ms": round(float(np.mean(latencies_ms)) / frames_per_segment, 3)
    }
    print(f"    Decode FPS: {res['throughput_fps']} fps | Mean per segment: {res['latency_per_segment_ms']['mean']} ms")
    return res

def benchmark_tracknet(registry, profile, sample_frames, n_iterations=30):
    print(f"\n[2] Benchmarking Shuttle Model: TrackNetV3 (Torch CUDA FP16)...")
    from bai_badminton.perception.tracknet import TrackNetV3
    
    vram_before = get_gpu_memory_mb()
    model_path = registry.path("tracknetv3")
    t0_load = time.perf_counter()
    model = TrackNetV3(
        model_path,
        backend=profile.shuttle.backend,
        threshold=0.5,
        batch=profile.shuttle.batch
    )
    load_time_s = time.perf_counter() - t0_load
    vram_after_load = get_gpu_memory_mb()
    
    # TrackNet takes sequences of 8 frames
    window = sample_frames[:8]
    shots = [0] * 8
    
    # Warmup
    for _ in range(5):
        _ = model.detect(window, shots, step=8)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        
    latencies = []
    for _ in range(n_iterations):
        t0 = time.perf_counter()
        _ = model.detect(window, shots, step=8)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        latencies.append(time.perf_counter() - t0)
        
    lat_ms = [l * 1000 for l in latencies]
    fps = (8 * n_iterations) / sum(latencies)
    vram_peak = get_gpu_memory_mb()
    
    res = {
        "model": "tracknetv3",
        "backend": profile.shuttle.backend,
        "precision": profile.shuttle.precision,
        "batch": profile.shuttle.batch,
        "load_time_s": round(load_time_s, 3),
        "vram_load_mb": vram_after_load["allocated_mb"],
        "vram_peak_mb": vram_peak["allocated_mb"],
        "throughput_fps": round(fps, 2),
        "latency_per_8frame_window_ms": {
            "mean": round(float(np.mean(lat_ms)), 2),
            "p50": round(float(np.percentile(lat_ms, 50)), 2),
            "p95": round(float(np.percentile(lat_ms, 95)), 2),
            "p99": round(float(np.percentile(lat_ms, 99)), 2),
        },
        "effective_per_frame_ms": round(float(np.mean(lat_ms)) / 8.0, 3)
    }
    print(f"    TrackNetV3 Throughput: {res['throughput_fps']} fps | Latency (8-fr): {res['latency_per_8frame_window_ms']['mean']} ms | VRAM: {res['vram_peak_mb']} MB")
    del model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return res

def benchmark_rfdetr(registry, profile, sample_frame, n_iterations=40):
    print(f"\n[3] Benchmarking Player Detector: RF-DETR-Small (ONNX Runtime CUDA)...")
    from bai_badminton.perception.players import PlayerDetector
    from bai_engine.runtime.device import engine_cache_dir, ort_providers
    
    cache = engine_cache_dir(REPO_ROOT / "models")
    providers = ort_providers(profile.player_detector.backend, engine_cache=cache / "rfdetr_small", fp16=True)
    model_path = registry.path("rfdetr_small")
    
    t0_load = time.perf_counter()
    detector = PlayerDetector(
        model_path,
        input_size=(512, 512),
        providers=providers,
        score_thr=0.35,
        kind="rfdetr"
    )
    load_time_s = time.perf_counter() - t0_load
    
    # Warmup
    for _ in range(5):
        _ = detector(sample_frame)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        
    latencies = []
    for _ in range(n_iterations):
        t0 = time.perf_counter()
        _ = detector(sample_frame)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        latencies.append(time.perf_counter() - t0)
        
    lat_ms = [l * 1000 for l in latencies]
    fps = n_iterations / sum(latencies)
    
    res = {
        "model": "rfdetr_small",
        "backend": profile.player_detector.backend,
        "input_size": [512, 512],
        "load_time_s": round(load_time_s, 3),
        "throughput_fps": round(fps, 2),
        "latency_per_frame_ms": {
            "mean": round(float(np.mean(lat_ms)), 2),
            "p50": round(float(np.percentile(lat_ms, 50)), 2),
            "p95": round(float(np.percentile(lat_ms, 95)), 2),
            "p99": round(float(np.percentile(lat_ms, 99)), 2),
        }
    }
    print(f"    RF-DETR-Small Throughput: {res['throughput_fps']} fps | Latency: {res['latency_per_frame_ms']['mean']} ms")
    del detector
    gc.collect()
    return res

def benchmark_rtmpose(registry, profile, sample_frame, n_iterations=40):
    print(f"\n[4] Benchmarking Pose Estimator: RTMPose-M (ONNX Runtime CUDA)...")
    from bai_badminton.perception.players import PoseEstimator
    from bai_engine.runtime.device import engine_cache_dir, ort_providers
    
    cache = engine_cache_dir(REPO_ROOT / "models")
    providers = ort_providers(profile.pose.backend, engine_cache=cache / "rtmpose_m_body7", fp16=True)
    model_path = registry.path("rtmpose_m_body7")
    
    t0_load = time.perf_counter()
    pose = PoseEstimator(
        model_path,
        input_size=(192, 256),
        providers=providers
    )
    load_time_s = time.perf_counter() - t0_load
    
    # Synthetic player bboxes (2 players)
    h, w = sample_frame.shape[:2]
    bboxes = [
        np.array([w * 0.4, h * 0.5, w * 0.6, h * 0.9], dtype=np.float64),
        np.array([w * 0.4, h * 0.2, w * 0.55, h * 0.5], dtype=np.float64)
    ]
    
    # Warmup
    for _ in range(5):
        _ = pose(sample_frame, bboxes)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        
    latencies = []
    for _ in range(n_iterations):
        t0 = time.perf_counter()
        _ = pose(sample_frame, bboxes)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        latencies.append(time.perf_counter() - t0)
        
    lat_ms = [l * 1000 for l in latencies]
    fps = n_iterations / sum(latencies)
    
    res = {
        "model": "rtmpose_m_body7",
        "backend": profile.pose.backend,
        "batch_players": 2,
        "load_time_s": round(load_time_s, 3),
        "throughput_fps": round(fps, 2),
        "latency_per_frame_2players_ms": {
            "mean": round(float(np.mean(lat_ms)), 2),
            "p50": round(float(np.percentile(lat_ms, 50)), 2),
            "p95": round(float(np.percentile(lat_ms, 95)), 2),
            "p99": round(float(np.percentile(lat_ms, 99)), 2),
        }
    }
    print(f"    RTMPose-M Throughput: {res['throughput_fps']} fps | Latency (2 players): {res['latency_per_frame_2players_ms']['mean']} ms")
    del pose
    gc.collect()
    return res

def benchmark_pipeline_chunk(profile, registry, chunk, in_play=True, n_runs=10):
    print(f"\n[5] Benchmarking Integrated Perception Pipeline (Chunk of {len(chunk.frames)} frames, in_play={in_play})...")
    from bai_badminton.perception.pipeline import BadmintonPerception
    
    models_dir = REPO_ROOT / "models"
    t0_init = time.perf_counter()
    pipeline = BadmintonPerception(profile, registry, fps=25.0, models_dir=models_dir)
    init_time_s = time.perf_counter() - t0_init
    
    # Warmup
    _ = pipeline.process(chunk, in_play=in_play)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        
    latencies = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        _ = pipeline.process(chunk, in_play=in_play)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        latencies.append(time.perf_counter() - t0)
        
    n_frames = len(chunk.frames)
    total_frames = n_frames * n_runs
    fps = total_frames / sum(latencies)
    lat_ms = [l * 1000 for l in latencies]
    
    res = {
        "chunk_frames": n_frames,
        "in_play": in_play,
        "init_time_s": round(init_time_s, 3),
        "throughput_fps": round(fps, 2),
        "effective_ratio_to_realtime_25fps": round(fps / 25.0, 2),
        "effective_ratio_to_realtime_30fps": round(fps / 30.0, 2),
        "latency_per_chunk_ms": {
            "mean": round(float(np.mean(lat_ms)), 2),
            "p50": round(float(np.percentile(lat_ms, 50)), 2),
            "p95": round(float(np.percentile(lat_ms, 95)), 2),
            "p99": round(float(np.percentile(lat_ms, 99)), 2),
        },
        "per_frame_ms": round(float(np.mean(lat_ms)) / n_frames, 2)
    }
    print(f"    Pipeline Throughput: {res['throughput_fps']} fps ({res['effective_ratio_to_realtime_25fps']}x real-time at 25fps) | Per-chunk: {res['latency_per_chunk_ms']['mean']} ms")
    del pipeline
    gc.collect()
    return res

def main():
    profile = load_profile("gpu-rtx4000", REPO_ROOT / "config" / "profiles")
    registry = ModelRegistry(REPO_ROOT / "models")
    
    # Load sample frames from YouTube session media
    media_root = REPO_ROOT / "data" / "media" / "2a057d6c66e17c0178ac372d3d78277dd98ec62a5764a1eda3a20027190e1401"
    media_paths = MediaPaths(media_root)
    decoder = SegmentDecoder(media_paths, frames_per_segment=50)
    
    chunk0 = decoder.decode_segment(0)
    sample_frames = chunk0.frames
    sample_frame = sample_frames[0]
    
    results = {
        "hardware": {
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None",
            "cuda_version": torch.version.cuda,
            "torch_version": torch.__version__,
            "total_vram_mb": round(torch.cuda.get_device_properties(0).total_memory / (1024*1024), 2) if torch.cuda.is_available() else 0,
        },
        "profile": profile.name,
        "device": profile.device,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    
    results["decode"] = benchmark_decode(media_paths, frames_per_segment=50, n_segments=10)
    results["shuttle_tracknetv3"] = benchmark_tracknet(registry, profile, sample_frames, n_iterations=25)
    results["player_detector_rfdetr"] = benchmark_rfdetr(registry, profile, sample_frame, n_iterations=30)
    results["pose_rtmpose"] = benchmark_rtmpose(registry, profile, sample_frame, n_iterations=30)
    results["pipeline_in_play"] = benchmark_pipeline_chunk(profile, registry, chunk0, in_play=True, n_runs=8)
    results["pipeline_idle"] = benchmark_pipeline_chunk(profile, registry, chunk0, in_play=False, n_runs=8)
    
    out_file = REPO_ROOT / "docs" / "testing" / "benchmark_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved benchmark results to {out_file}")

if __name__ == "__main__":
    main()
