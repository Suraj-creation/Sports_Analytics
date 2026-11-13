"""Unresolved canonical ownership must not discard independent visible boxes."""

from bai_engine.schema.tracks import TrackObject, TrackSample
from bai_engine.wire import decode_tracks, encode_tracks


def person(frame, raw, *, context="camera:0", track=-1):
    return TrackSample(
        frame_idx=frame, obj=TrackObject.PLAYER, track_id=track,
        raw_track_id=raw, context_id=context, bbox=(1, 2, 30, 40),
        detector_observed=True, detector_matched=True,
        identity_method="ambiguous_assignment",
    )


def test_four_unresolved_bodies_remain_four_independent_browser_series():
    rows = [person(frame, raw) for frame in (1, 2) for raw in (10, 11, 12, 13)]
    wire = decode_tracks(encode_tracks(rows, 1, 2))
    assert wire["players"] == {}
    assert len(wire["anonymous"]) == 4
    assert sum(len(p["f"]) for p in wire["anonymous"].values()) == 8
    for p in wire["anonymous"].values():
        assert p["f"] == [1, 2]
        assert p["t"] == [-1, -1]
        assert len(set(p["raw"])) == 1
        assert p["obs"] == [None, None]


def test_missing_raw_ownership_has_no_cross_frame_display_series():
    wire = decode_tracks(encode_tracks([person(1, None), person(1, None), person(2, None)], 1, 2))
    assert len(wire["anonymous"]) == 3
    assert sorted(p["f"] for p in wire["anonymous"].values()) == [[1], [1], [2]]


def test_raw_id_reuse_across_contexts_does_not_join_display_series():
    wire = decode_tracks(encode_tracks([person(1, 10), person(2, 10, context="camera:1")], 1, 2))
    assert len(wire["anonymous"]) == 2


def test_duplicate_unresolved_raw_rows_cannot_overwrite_same_frame():
    wire = decode_tracks(encode_tracks([person(1, 10), person(1, 10)], 1, 1))
    assert len(wire["anonymous"]) == 2
    assert all(p["f"] == [1] for p in wire["anonymous"].values())


def test_known_canonical_group_key_remains_compatible():
    wire = decode_tracks(encode_tracks([person(1, 10, track=7)], 1, 1))
    assert list(wire["anonymous"]) == ["track:7"]
