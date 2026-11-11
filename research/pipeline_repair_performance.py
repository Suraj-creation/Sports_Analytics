"""Wall-clock stage observations for controlled fresh-upload experiments.

Samples describe existing completed stage scopes, which can overlap. These are
not CUDA-event kernel timings and must not be added to estimate total runtime.
"""

from __future__ import annotations

import math

import numpy as np


def summarize_stage_samples(samples):
    result = {}
    for stage, rows in samples.items():
        if not rows:
            continue
        seconds = np.asarray([row["seconds"] for row in rows], dtype=float)
        if not np.isfinite(seconds).all() or (seconds < 0).any():
            raise ValueError("stage latency must be finite nonnegative wall seconds")
        if any(type(row["frames"]) is not int or row["frames"] < 0 for row in rows):
            raise ValueError("stage sample frame population must be a nonnegative integer")
        result[stage] = {
            "calls": len(rows),
            "seconds": float(seconds.sum()),
            "p50_ms": float(np.percentile(seconds, 50) * 1000),
            "p95_ms": float(np.percentile(seconds, 95) * 1000),
            "min_ms": float(seconds.min() * 1000),
            "max_ms": float(seconds.max() * 1000),
            "scope": "existing pipeline stage invocation; scopes may overlap",
            "frame_population_sum": sum(row["frames"] for row in rows),
        }
        assert all(math.isfinite(result[stage][key]) for key in ("seconds", "p50_ms", "p95_ms"))
    return result


def observe_perception_rates(perception, samples):
    """Observe the exact duration already recorded by perception, without rescheduling."""
    original = perception._rate

    def record(stage, n, began):
        previous = perception.stats.seconds.get(stage, 0.0)
        original(stage, n, began)
        delta = perception.stats.seconds[stage] - previous
        samples.setdefault(stage, []).append({"seconds": delta, "frames": n})

    perception._rate = record
