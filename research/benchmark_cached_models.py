"""Benchmark existing detector artifacts on source-bound real frames without downloads.

Outputs JSON to stdout. Detection counts are diagnostics, never precision/recall.
Source ../gpu-env.sh first. Samples are a development workload, not a held-out set.
"""

from __future__ import annotations

import argparse
import contextlib
import gc
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import cv2
import numpy as np
import torch

from bai_badminton.perception.players import PlayerDetector
from bai_engine.runtime.device import ort_providers
from bai_engine.schema.session import Session


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", required=True)
    parser.add_argument("--frames", default="0,900,3600,7200,12000,18000,22000")
    parser.add_argument("--repeats", type=int, default=2)
    args = parser.parse_args()
    indices = [int(item) for item in args.frames.split(",")]
    if args.repeats < 1 or not indices or min(indices) < 0:
        parser.error("positive repeats and nonnegative frame indices required")
    with sqlite3.connect("file:data/sessions.sqlite?mode=ro", uri=True) as connection:
        row = connection.execute("SELECT body FROM sessions WHERE session_id=?", (args.session,)).fetchone()
    if row is None:
        parser.error("unknown session")
    session = Session.model_validate_json(row[0])
    if session.media is None or max(indices) >= session.media.n_frames:
        parser.error("sample frame outside canonical media")
    proxy = Path("data/media") / str(session.source.sha256) / "proxy.mp4"
    capture = cv2.VideoCapture(str(proxy))
    frames = []
    try:
        for index in indices:
            capture.set(cv2.CAP_PROP_POS_FRAMES, index)
            ok, frame = capture.read()
            if not ok:
                raise RuntimeError(f"cannot decode canonical frame {index}")
            frames.append(frame)
    finally:
        capture.release()
    results = []
    for name, size in (("rfdetr_nano", 384), ("rfdetr_small", 512), ("rfdetr_medium", 576)):
        paths = list((Path("models/cache") / name).glob("*.onnx"))
        if len(paths) != 1:
            results.append({"model": name, "status": "unavailable", "reason": "one cached ONNX artifact required"})
            continue
        with contextlib.redirect_stdout(sys.stderr):
            detector = PlayerDetector(paths[0], (size, size), ort_providers("onnx-cuda"), score_thr=0.35)
            for _ in range(3):
                detector(frames[0])
            timings, counts = [], []
            for frame in frames * args.repeats:
                started = time.perf_counter()
                boxes, _ = detector(frame)
                timings.append((time.perf_counter() - started) * 1000)
                counts.append(len(boxes))
        memory = subprocess.check_output(
            ["nvidia-smi", "--query-compute-apps=pid,used_gpu_memory", "--format=csv,noheader"], text=True
        ).splitlines()
        results.append(
            {
                "model": name,
                "status": "measured",
                "weight_sha256": hashlib.sha256(paths[0].read_bytes()).hexdigest(),
                "providers": detector.tool.session.get_providers(),
                "score_threshold": 0.35,
                "p50_ms": float(np.median(timings)),
                "p95_ms": float(np.percentile(timings, 95)),
                "all_latency_ms": timings,
                "person_counts_first_pass": counts[: len(frames)],
                "process_vram_snapshot": [line for line in memory if line.split(",")[0].strip() == str(os.getpid())],
            }
        )
        del detector
        gc.collect()
    print(
        json.dumps(
            {
                "schema_version": 1,
                "timestamp_utc": datetime.now(UTC).isoformat(),
                "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                "torch": torch.__version__,
                "cuda": torch.version.cuda,
                "session_id": session.session_id,
                "media_sha256": session.source.sha256,
                "frame_indices": indices,
                "repeats": args.repeats,
                "warmup_calls": 3,
                "accuracy_measured": False,
                "limitations": (
                    "Full-frame detections before court admission. No player labels. "
                    "Process VRAM snapshots include retained allocations, not per-model peak memory. "
                    "CUDA provider listing permits CPU fallback; use ORT profiling for node placement."
                ),
                "models": results,
            },
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
