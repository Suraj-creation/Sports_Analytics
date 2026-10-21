"""Observability: structured logging and Prometheus metrics shared by API and engine."""

from __future__ import annotations

import logging
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager

import structlog
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

REGISTRY = CollectorRegistry(auto_describe=True)

_LAT_BUCKETS = (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10)

DECODE_FPS = Gauge("bai_decode_fps", "Decoded frames per second (rolling)", ["session"], registry=REGISTRY)
INFERENCE_FPS = Gauge("bai_inference_fps", "Model throughput in frames/s", ["model"], registry=REGISTRY)
STAGE_LATENCY = Histogram(
    "bai_stage_latency_seconds", "Per-chunk stage latency", ["stage"], buckets=_LAT_BUCKETS, registry=REGISTRY
)
FRONTIER_LEAD = Gauge("bai_frontier_lead_ms", "Analysis frontier minus playhead (ms)", ["session"], registry=REGISTRY)
ANALYSIS_RATE = Gauge(
    "bai_analysis_rate_x", "Analysis speed as a multiple of real time", ["session"], registry=REGISTRY
)
QUEUE_DEPTH = Gauge("bai_queue_depth", "Pending chunks", ["session"], registry=REGISTRY)
EVENTS_TOTAL = Counter("bai_events_total", "Events appended", ["type", "status"], registry=REGISTRY)
ESCALATIONS = Counter("bai_escalations_total", "Refinement escalations", ["trigger", "action"], registry=REGISTRY)
DEGRADED = Counter("bai_degraded_total", "Degradation transitions", ["reason"], registry=REGISTRY)
GPU_UTIL = Gauge("bai_gpu_util_percent", "GPU utilisation", ["gpu"], registry=REGISTRY)
GPU_MEM = Gauge("bai_gpu_mem_used_mb", "GPU memory used", ["gpu"], registry=REGISTRY)
GPU_POWER = Gauge("bai_gpu_power_w", "GPU power draw", ["gpu"], registry=REGISTRY)
WS_CLIENTS = Gauge("bai_ws_clients", "Connected WebSocket clients", registry=REGISTRY)
WS_SEND_LAG = Histogram("bai_ws_send_lag_seconds", "Publish→send lag", buckets=_LAT_BUCKETS, registry=REGISTRY)
LLM_TOKENS = Counter("bai_llm_tokens_total", "LLM tokens", ["agent", "provider", "kind"], registry=REGISTRY)


def configure_logging(level: str = "INFO", json_logs: bool = False) -> None:
    logging.basicConfig(stream=sys.stdout, level=level.upper(), format="%(message)s")
    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    processors.append(structlog.processors.JSONRenderer() if json_logs else structlog.dev.ConsoleRenderer())
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level.upper())),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)  # type: ignore[no-any-return]


@contextmanager
def timed(stage: str) -> Iterator[None]:
    t0 = time.perf_counter()
    try:
        yield
    finally:
        STAGE_LATENCY.labels(stage=stage).observe(time.perf_counter() - t0)


class RateMeter:
    """Exponentially smoothed rate (events per second)."""

    def __init__(self, alpha: float = 0.2) -> None:
        self.alpha = alpha
        self._rate: float | None = None
        self._t: float | None = None

    def tick(self, n: int = 1) -> float:
        now = time.perf_counter()
        if self._t is not None and now > self._t:
            inst = n / (now - self._t)
            self._rate = inst if self._rate is None else self.alpha * inst + (1 - self.alpha) * self._rate
        self._t = now
        return self._rate or 0.0

    @property
    def rate(self) -> float:
        return self._rate or 0.0
