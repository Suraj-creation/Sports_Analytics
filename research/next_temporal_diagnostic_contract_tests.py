"""Trace/cache identity controls; no model inference or sporting labels."""

import json

import pytest

from research.next_temporal_diagnose import sha, verify_trace_cache_identity


def evidence(tmp_path):
    cache_dir = tmp_path / "perception"
    cache_dir.mkdir()
    cache = cache_dir / "seg_00000.msgpack"
    cache.write_bytes(b"controlled-cache-byte-fixture")
    semantic = tmp_path / "semantic"
    semantic.mkdir()
    trace = semantic / "fsm_trace.jsonl"
    trace.write_text('{"call":"controlled-fixture"}\n')
    metadata = {"source_video_sha256": "a" * 64, "ground_truth_sha256": "b" * 64}
    manifest = {
        "cache_sha256": {cache.name: sha(cache)},
        "trace_sha256": sha(trace),
        "video_sha256": metadata["source_video_sha256"],
        "ground_truth_sha256": metadata["ground_truth_sha256"],
        "source_unchanged": True,
    }
    (semantic / "replay_metadata.json").write_text(json.dumps(manifest))
    return metadata, trace, [cache]


def test_equal_intervals_do_not_authorize_a_changed_cache(tmp_path):
    metadata, trace, caches = evidence(tmp_path)
    assert verify_trace_cache_identity(metadata, trace, caches) == {caches[0].name: sha(caches[0])}
    caches[0].write_bytes(b"different-perception-with-the-same-intervals")
    with pytest.raises(ValueError, match="cache bytes"):
        verify_trace_cache_identity(metadata, trace, caches)


def test_trace_bytes_and_video_identity_are_independent_controls(tmp_path):
    metadata, trace, caches = evidence(tmp_path)
    with pytest.raises(ValueError, match="different original video"):
        verify_trace_cache_identity({**metadata, "source_video_sha256": "c" * 64}, trace, caches)
    trace.write_text('{"call":"changed-fixture"}\n')
    with pytest.raises(ValueError, match="trace bytes"):
        verify_trace_cache_identity(metadata, trace, caches)


def test_missing_provenance_and_multiple_cache_roots_abstain(tmp_path):
    metadata, trace, caches = evidence(tmp_path)
    other = tmp_path / "another_perception"
    other.mkdir()
    extra = other / "seg_00001.msgpack"
    extra.write_bytes(b"other-session")
    with pytest.raises(ValueError, match="unambiguous"):
        verify_trace_cache_identity(metadata, trace, [*caches, extra])
    (trace.parent / "replay_metadata.json").unlink()
    with pytest.raises(ValueError, match="provenance manifest"):
        verify_trace_cache_identity(metadata, trace, caches)
