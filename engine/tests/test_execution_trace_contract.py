"""Opt-in session traces must never corrupt analysis or cross evidence scopes."""

import io
import json
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest

from bai_engine import trace


def records(directory):
    return [json.loads(line) for path in directory.glob("*.jsonl") for line in path.read_text().splitlines()]


def test_disabled_tracing_creates_no_artifacts(tmp_path):
    directory = tmp_path / "unused"
    with (
        trace.trace_session(None, "disabled", "a" * 64), trace.trace_frames(3, 5),
        trace.trace_span("decode", count=3) as attrs,
    ):
        attrs["output_count"] = 3
    assert not directory.exists()
    assert not list(tmp_path.iterdir())


def test_session_source_frames_shapes_and_parentage_are_retained(tmp_path):
    with (
        trace.trace_session(tmp_path, "video-session", "a" * 64), trace.trace_frames(8, 15),
        trace.trace_span("pipeline", version="2"),
        trace.trace_span("detector", shape=[1, 3, 384, 384], dtype="float32") as attrs,
    ):
        attrs["output_count"] = 4
    spans = {row["component"]: row for row in records(tmp_path)}
    assert set(spans) == {"pipeline", "detector"}
    parent, child = spans["pipeline"], spans["detector"]
    assert parent["parent_id"] is None
    assert child["parent_id"] == parent["span_id"]
    assert child["session_id"] == "video-session" and child["source_sha256"] == "a" * 64
    assert (child["frame_start"], child["frame_end"]) == (8, 15)
    assert child["attributes"] == {"shape": [1, 3, 384, 384], "dtype": "float32", "output_count": 4}
    assert child["duration_ms"] >= 0
    assert child["ended_unix_ns"] - child["started_unix_ns"] == pytest.approx(child["duration_ms"] * 1e6)
    assert child["timing_semantics"] == "host_wall_time_no_device_sync"
    assert child["error"] is None


def test_processing_error_is_recorded_without_replacing_original_exception(tmp_path):
    original = RuntimeError("provider failed")
    with trace.trace_session(tmp_path, "failed-video", None):
        with pytest.raises(RuntimeError) as captured, trace.trace_span("pose"):
            raise original
        with trace.trace_span("recovery"):
            pass
    assert captured.value is original
    spans = {row["component"]: row for row in records(tmp_path)}
    assert spans["pose"]["error"] == {"type": "RuntimeError", "message": "provider failed"}
    assert spans["recovery"]["parent_id"] is None


def test_metadata_is_bounded_without_dumping_large_input(tmp_path):
    with trace.trace_session(tmp_path, "bounded", None), trace.trace_span("model", mistaken_large_value="x" * 100_000):
        pass
    paths = list(tmp_path.glob("*.jsonl"))
    assert len(paths) == 1 and paths[0].stat().st_size <= 16384
    assert records(tmp_path)[0]["attributes"] == {"omitted": "metadata_exceeded_16KiB_bound"}


@pytest.mark.parametrize("bad_metadata", [object(), float("nan")])
def test_invalid_trace_metadata_is_visible_and_does_not_fail_analysis(tmp_path, monkeypatch, bad_metadata):
    warnings = []
    monkeypatch.setattr(trace, "log", SimpleNamespace(warning=lambda event, **attrs: warnings.append((event, attrs))))
    with trace.trace_session(tmp_path, "bad-metadata", None):
        with trace.trace_span("model", mistaken_value=bad_metadata):
            pass
        with trace.trace_span("later"):
            pass
    assert len(warnings) == 1 and warnings[0][0] == "trace.write_failed"
    assert warnings[0][1]["session"] == "bad-metadata"


def test_output_write_failure_is_reported_once_without_failing_analysis(tmp_path, monkeypatch):
    class BrokenStream(io.StringIO):
        def write(self, value):
            raise OSError("disk full")

    stream, warnings = BrokenStream(), []
    monkeypatch.setattr(type(tmp_path), "open", lambda *args, **kwargs: stream)
    monkeypatch.setattr(trace, "log", SimpleNamespace(warning=lambda event, **attrs: warnings.append((event, attrs))))
    with trace.trace_session(tmp_path, "disk-failure", None):
        for _ in range(2):
            with trace.trace_span("chunk"):
                pass
    assert len(warnings) == 1 and warnings[0][0] == "trace.write_failed"
    assert "disk full" in warnings[0][1]["error"]


def test_trace_open_failure_is_visible_and_analysis_continues(tmp_path, monkeypatch):
    warnings = []

    def fail_open(*args, **kwargs):
        raise OSError("read-only filesystem")

    monkeypatch.setattr(type(tmp_path), "open", fail_open)
    monkeypatch.setattr(trace, "log", SimpleNamespace(warning=lambda event, **attrs: warnings.append((event, attrs))))
    with trace.trace_session(tmp_path, "cannot-open", None), trace.trace_span("perceive"):
        pass
    assert warnings[0][0] == "trace.unavailable"


def test_new_session_does_not_inherit_another_sessions_parent_or_frame_range(tmp_path):
    with (
        trace.trace_session(tmp_path, "outer", "a" * 64), trace.trace_frames(10, 20),
        trace.trace_span("outer-work"),
    ):
        with trace.trace_session(tmp_path, "inner", "b" * 64), trace.trace_span("inner-work"):
            pass
        with trace.trace_span("outer-resumed"):
            pass
    spans = {row["component"]: row for row in records(tmp_path)}
    assert spans["inner-work"]["parent_id"] is None
    assert spans["inner-work"]["frame_start"] is None
    assert spans["inner-work"]["frame_end"] is None
    assert spans["outer-resumed"]["parent_id"] == spans["outer-work"]["span_id"]
    assert spans["outer-resumed"]["frame_start"] == 10


def test_disabled_inner_session_cannot_write_into_an_enabled_outer_session(tmp_path):
    with (
        trace.trace_session(tmp_path, "outer", None), trace.trace_span("outer-work"),
        trace.trace_session(None, "disabled", None), trace.trace_span("disabled-work"),
    ):
        pass
    assert {row["component"] for row in records(tmp_path)} == {"outer-work"}


@pytest.mark.parametrize("processing_error", [False, True])
def test_trace_close_failure_cannot_fail_or_mask_analysis(tmp_path, monkeypatch, processing_error):
    class BrokenClose(io.StringIO):
        def close(self):
            super().close()
            raise OSError("close failed")

    warnings = []
    monkeypatch.setattr(type(tmp_path), "open", lambda *args, **kwargs: BrokenClose())
    monkeypatch.setattr(trace, "log", SimpleNamespace(warning=lambda event, **attrs: warnings.append((event, attrs))))

    def process():
        with trace.trace_session(tmp_path, "close-failure", None), trace.trace_span("work"):
            if processing_error:
                raise ValueError("original processing failure")

    if processing_error:
        with pytest.raises(ValueError, match="original processing failure"):
            process()
    else:
        process()
    assert any(event == "trace.close_failed" for event, _ in warnings)


def test_threaded_session_contexts_and_unsafe_identifiers_are_isolated(tmp_path):
    def work(identifier):
        with (
            trace.trace_session(tmp_path, identifier, None), trace.trace_frames(1, 2),
            trace.trace_span("session-work", worker=identifier),
        ):
            pass

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(work, ["../../unsafe/session", "other-session"]))
    output = records(tmp_path)
    assert len(output) == 2
    assert {row["session_id"] for row in output} == {"../../unsafe/session", "other-session"}
    assert all(row["session_id"] == row["attributes"]["worker"] and row["parent_id"] is None for row in output)
    assert len(list(tmp_path.glob("*.jsonl"))) == 2
