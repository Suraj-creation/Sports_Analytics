"""Codec22 preserves bounded scene-only observations independently of athletes."""

from dataclasses import replace
from types import SimpleNamespace

import msgpack
import pytest
from test_perception_diagnostic_provenance import _non30_cache_session
from test_scene_decision_cache import source_frame as legacy_source_frame
from test_scene_witness_layout import decision_for, make_probe, make_v3_raw

from bai_badminton.perception.scene_change import ForegroundRegion
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.plugin import CODEC_VERSION, BadmintonSession, StaleCacheError


@pytest.fixture
def cache_session(tmp_path):
    session = _non30_cache_session(tmp_path)
    yield session
    session.close()


def regions(frame=25):
    return (
        ForegroundRegion(frame, "scene:0", (100.0, 100.0, 200.0, 300.0), True, True),
        ForegroundRegion(frame, "scene:1", (400.0, 100.0, 500.0, 300.0), False, False),
    )


def payload(session):
    frame = replace(legacy_source_frame(), foreground_regions=regions())
    return session.encode_perception(ChunkPerception(25, 25, [frame], models={"player_detector": "detector@1"}))


def unpack(session):
    return msgpack.unpackb(payload(session), raw=False)


def decode(session, record):
    return session.decode_perception(msgpack.packb(record, use_bin_type=True), diagnostic=True)


def test_codec22_non30_foreground_is_exact_typed_and_detached_from_people(cache_session):
    record = unpack(cache_session)
    assert record["v"] == CODEC_VERSION
    assert record["ci"]["fps"] == 25
    decoded = decode(cache_session, record).frames[0]
    assert decoded.frame_idx == 25 and decoded.persons == []
    assert decoded.foreground_regions == regions()
    assert decoded.foreground_regions[0].detector_matched is True
    assert decoded.foreground_regions[1].detector_matched is False
    assert all(isinstance(region, ForegroundRegion) for region in decoded.foreground_regions)


@pytest.mark.parametrize("kind", ["missing", "null", "dict", "duplicate", "overflow"])
def test_codec22_rejects_missing_untyped_duplicate_or_unbounded_foreground(cache_session, kind):
    record = unpack(cache_session)
    frame = record["frames"][0]
    if kind == "missing":
        del frame["fg"]
    elif kind == "null":
        frame["fg"] = None
    elif kind == "dict":
        frame["fg"] = {"scene:0": frame["fg"][0]}
    elif kind == "duplicate":
        frame["fg"] = [frame["fg"][0], frame["fg"][0]]
    else:
        frame["fg"] = [{**frame["fg"][0], "key": f"scene:{i}"} for i in range(9)]
    with pytest.raises(StaleCacheError):
        decode(cache_session, record)


@pytest.mark.parametrize(
    "field,value",
    [
        ("frame", 24),
        ("frame", 26),
        ("frame", 25.0),
        ("key", ""),
        ("detector_matched", 1),
        ("detector_observed", "true"),
        ("bbox", [100.0, 100.0, 99.0, 300.0]),
        ("bbox", [float("nan"), 100.0, 200.0, 300.0]),
        ("bbox", [True, 100.0, 200.0, 300.0]),
    ],
)
def test_codec22_rejects_changed_source_types_or_invalid_geometry(cache_session, field, value):
    record = unpack(cache_session)
    record["frames"][0]["fg"][0][field] = value
    with pytest.raises(StaleCacheError):
        decode(cache_session, record)


@pytest.mark.parametrize("change", ["extra", "missing"])
def test_codec22_requires_exact_foreground_schema(cache_session, change):
    record = unpack(cache_session)
    region = record["frames"][0]["fg"][0]
    if change == "extra":
        region["named_player"] = "invented"
    else:
        del region["detector_observed"]
    with pytest.raises(StaleCacheError):
        decode(cache_session, record)


def test_codec22_empty_foreground_is_explicitly_valid(cache_session):
    record = unpack(cache_session)
    record["frames"][0]["fg"] = []
    assert decode(cache_session, record).frames[0].foreground_regions == ()


def test_historical_codec21_without_foreground_keeps_unknown_diagnostic_context(cache_session):
    record = unpack(cache_session)
    record["v"] = 21
    frame = record["frames"][0]
    del frame["fg"]
    frame["cc"].pop("supporting_region_keys", None)
    frame["cc"].pop("witness_parameters", None)
    frame["cd"].pop("supporting_region_keys", None)
    frame["cd"].pop("layout_indices", None)
    decoded = decode(cache_session, record).frames[0]
    assert decoded.foreground_regions == ()
    assert decoded.content_change.version == "foreground-scene-hypothesis:v2"
    assert decoded.content_decision.version == "detector-layout-scene-decision:v1"


@pytest.mark.parametrize("change", ["not_typed", "wrong_frame", "duplicate"])
def test_typed_frame_rejects_invalid_foreground_before_serialization(change):
    value = regions()
    if change == "not_typed":
        value = ({"frame": 25},)
    elif change == "wrong_frame":
        value = regions(24)
    else:
        value = (value[0], value[0])
    with pytest.raises(ValueError):
        FramePerception(25, None, 0.0, foreground_regions=value)


def v3_record(session, monkeypatch):
    raw = make_v3_raw(monkeypatch, adaptive_ratio=4.0, minimum_discontinuity=19.0)
    frame = replace(
        legacy_source_frame(),
        content_change=raw,
        content_decision=decision_for(raw, make_probe(raw)),
        foreground_regions=regions(),
    )
    record = msgpack.unpackb(
        session.encode_perception(ChunkPerception(25, 25, [frame], models={"player_detector": "detector@1"})), raw=False
    )
    # This controlled V3 measurement exercises historical codec22 semantics;
    # the current writer must not relabel it as codec24's exclusive-origin V5.
    record["v"] = 22
    record["ci"]["profile"]["components"]["content_continuity"] = {
        "implementation": "foreground-content-continuity-v2",
        "params": {"mode": "barrier_detector_layout_v2", "adaptive_ratio": 4.0, "minimum_discontinuity": 19.0},
    }
    receiver = SimpleNamespace(perception=SimpleNamespace(ref_id=record["cr"]), _isolation_id=lambda: record["ci"])
    return record, receiver


def test_codec22_v3_layout_roundtrip_binds_custom_parameters_and_full_region_indices(cache_session, monkeypatch):
    record, receiver = v3_record(cache_session, monkeypatch)
    frame = BadmintonSession.decode_perception(
        receiver, msgpack.packb(record, use_bin_type=True), diagnostic=True
    ).frames[0]
    assert frame.content_change.witness_parameters == (4.0, 19.0)
    assert frame.content_decision.matched_pairs == ((1, 3), (2, 0))
    assert frame.content_decision.admitted_indices == (0,)
    assert frame.content_decision.layout_indices == (0, 1, 2, 3)


@pytest.mark.parametrize("change", ["parameters", "witnesses", "pairs", "layout_subset"])
def test_codec22_v3_cannot_forge_profile_witness_or_layout_binding(cache_session, monkeypatch, change):
    record, receiver = v3_record(cache_session, monkeypatch)
    frame = record["frames"][0]
    if change == "parameters":
        frame["cc"]["witness_parameters"] = [3.0, 15.0]
    elif change == "witnesses":
        frame["cd"]["supporting_region_keys"] = ["scene:static", "scene:B"]
    elif change == "pairs":
        frame["cd"]["matched_pairs"] = [[0, 3], [1, 0]]
    else:
        frame["cd"]["layout_indices"] = [0, 3]
    with pytest.raises(StaleCacheError):
        BadmintonSession.decode_perception(receiver, msgpack.packb(record, use_bin_type=True), diagnostic=True)
