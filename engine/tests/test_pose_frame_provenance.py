from pathlib import Path

import msgpack
import pyarrow.parquet as pq
import pytest

from bai_engine.schema import TrackObject, TrackSample
from bai_engine.schema.tracks import samples_to_table, table_to_samples
from bai_engine.store import TrackStore
from bai_engine.wire import decode_tracks, encode_tracks


def player(frame=10, pose=7, track=1):
    return TrackSample(
        frame_idx=frame, obj=TrackObject.PLAYER, track_id=track, bbox=(0, 0, 10, 20), pose_frame_idx=pose
    )


@pytest.mark.parametrize("count", [2, 4])
def test_pose_source_roundtrip_arrow_and_wire(count):
    samples = [player(track=i, pose=6 + i) for i in range(count)]
    assert table_to_samples(samples_to_table(samples)) == samples
    wire = decode_tracks(encode_tracks(samples, 10, 10))
    assert wire["v"] == 2
    assert [p["pf"][0] for p in wire["anonymous"].values()] == list(range(6, 6 + count))


@pytest.mark.parametrize("pose", [-1, 11, True, 1.5])
def test_invalid_or_future_pose_frame_is_rejected(pose):
    with pytest.raises(ValueError):
        player(pose=pose)


def test_mixed_legacy_and_new_store_parts_remain_unknown_or_exact(tmp_path: Path):
    store = TrackStore(tmp_path)
    old = store.write_chunk(TrackObject.PLAYER, 0, 9, samples_to_table([player(frame=5, pose=3)]))
    pq.write_table(pq.read_table(old).drop(["pose_frame_idx"]), old)
    store.write_chunk(TrackObject.PLAYER, 10, 19, samples_to_table([player()]))
    samples = table_to_samples(store.read([TrackObject.PLAYER], 0, 19))
    assert [s.pose_frame_idx for s in samples] == [None, 7]
    assert table_to_samples(samples_to_table(samples).drop(["pose_frame_idx"]))[0].pose_frame_idx is None


def test_legacy_wire_without_pose_column_backreads_without_invented_source():
    legacy = {"v": 1, "from": 0, "to": 0, "shuttle": {"f": [], "x": [], "y": [], "c": []}, "players": {}}
    assert decode_tracks(msgpack.packb(legacy)) == legacy
    sample = TrackSample(frame_idx=10, obj=TrackObject.PLAYER, player_id="P1", bbox=(0, 0, 10, 20))
    assert decode_tracks(encode_tracks([sample], 10, 10))["players"]["P1"]["pf"] == [None]


@pytest.mark.parametrize("version", [0, 3, True, "2", None])
def test_unknown_wire_version_is_not_treated_as_current(version):
    with pytest.raises(ValueError):
        decode_tracks(msgpack.packb({"v": version}))


def test_wire_rejects_future_pose_source_before_consumption():
    wire = decode_tracks(encode_tracks([player()], 10, 10))
    next(iter(wire["anonymous"].values()))["pf"] = [11]
    with pytest.raises(ValueError):
        decode_tracks(msgpack.packb(wire))
