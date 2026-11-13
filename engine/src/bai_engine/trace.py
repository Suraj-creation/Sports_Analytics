"""Opt-in bounded wall-clock spans for one session's real execution.

No GPU synchronization is inserted: durations include host waits and are not
device kernel timings. Trace failure must be visible without failing analysis.
"""

from __future__ import annotations

import json
import time
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, TextIO
from uuid import uuid4

from bai_engine.obs import get_logger

log = get_logger(__name__)


@dataclass
class _Trace:
    stream: TextIO
    session_id: str
    source_sha256: str | None
    failed: bool = False


_TRACE: ContextVar[_Trace | None] = ContextVar("execution_trace", default=None)
_FRAME: ContextVar[tuple[int, int] | None] = ContextVar("trace_frame_range", default=None)
_PARENT: ContextVar[str | None] = ContextVar("trace_parent_span", default=None)


@contextmanager
def trace_session(directory: Path | None, session_id: str, source_sha256: str | None) -> Iterator[None]:
    stream = None
    trace_token = _TRACE.set(None)
    frame_token = _FRAME.set(None)
    parent_token = _PARENT.set(None)
    try:
        if directory is not None:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                # An arbitrary plugin/session identifier cannot become a filesystem path.
                filename = sha256(session_id.encode()).hexdigest()[:24]
                stream = (directory / f"{filename}.jsonl").open("a", encoding="utf-8")
                _TRACE.set(_Trace(stream, session_id, source_sha256))
            except OSError as error:
                log.warning("trace.unavailable", session=session_id, error=str(error))
        yield
    finally:
        _TRACE.reset(trace_token)
        _FRAME.reset(frame_token)
        _PARENT.reset(parent_token)
        if stream is not None:
            try:
                stream.close()
            except OSError as error:
                log.warning("trace.close_failed", session=session_id, error=str(error))


@contextmanager
def trace_frames(start: int, end: int) -> Iterator[None]:
    token = _FRAME.set((start, end))
    try:
        yield
    finally:
        _FRAME.reset(token)


@contextmanager
def trace_span(component: str, **attributes: Any) -> Iterator[dict[str, Any]]:
    trace = _TRACE.get()
    if trace is None or trace.failed:
        yield attributes
        return
    started, wall_started = time.perf_counter_ns(), time.time_ns()
    parent, span_id = _PARENT.get(), uuid4().hex
    token = _PARENT.set(span_id)
    failure = None
    try:
        yield attributes
    except BaseException as error:
        failure = {"type": type(error).__name__, "message": str(error)[:1000]}
        raise
    finally:
        duration = time.perf_counter_ns() - started
        _PARENT.reset(token)
        bounds = _FRAME.get()
        record = {
            "schema": "execution-span:v1", "session_id": trace.session_id,
            "source_sha256": trace.source_sha256, "span_id": span_id, "parent_id": parent,
            "component": component, "frame_start": bounds[0] if bounds else None,
            "frame_end": bounds[1] if bounds else None,
            "started_unix_ns": wall_started, "ended_unix_ns": wall_started + duration,
            "duration_ms": duration / 1_000_000, "timing_semantics": "host_wall_time_no_device_sync",
            "error": failure, "attributes": attributes,
        }
        try:
            line = json.dumps(record, allow_nan=False, separators=(",", ":"))
            if len(line) > 16384:
                record["attributes"] = {"omitted": "metadata_exceeded_16KiB_bound"}
                line = json.dumps(record, allow_nan=False, separators=(",", ":"))
            trace.stream.write(line + "\n")
            trace.stream.flush()
        except (OSError, TypeError, ValueError) as error:
            trace.failed = True
            log.warning("trace.write_failed", session=trace.session_id, error=str(error))
