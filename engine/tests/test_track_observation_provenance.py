from pathlib import Path

import pyarrow.parquet as pq

from bai_engine.schema import TrackObject, TrackSample
from bai_engine.schema.tracks import samples_to_table, table_to_samples
from bai_engine.store import TrackStore


def test_participant_observation_id_round_trips_and_legacy_parquet_reads(tmp_path: Path):
    sample = TrackSample(
        frame_idx=10, obj=TrackObject.PLAYER, track_id=7, bbox=(1, 2, 3, 4), participant_observation_id="birth-123"
    )
    assert table_to_samples(samples_to_table([sample])) == [sample]
    store = TrackStore(tmp_path)
    path = store.write_chunk(TrackObject.PLAYER, 0, 20, samples_to_table([sample]))
    legacy = pq.read_table(path).drop(["participant_observation_id"])
    pq.write_table(legacy, path)
    rows = store.read([TrackObject.PLAYER], 10, 10).to_pylist()
    assert len(rows) == 1 and rows[0]["participant_observation_id"] is None


def test_detector_observation_flag_round_trips_and_legacy_is_unknown(tmp_path: Path):
    samples = [
        TrackSample(frame_idx=0, obj=TrackObject.PLAYER, track_id=4, detector_observed=True),
        TrackSample(frame_idx=1, obj=TrackObject.PLAYER, track_id=4, detector_observed=False),
        TrackSample(frame_idx=2, obj=TrackObject.PLAYER, track_id=4),
    ]
    assert table_to_samples(samples_to_table(samples)) == samples
    store = TrackStore(tmp_path)
    path = store.write_chunk(TrackObject.PLAYER, 0, 3, samples_to_table(samples))
    legacy = pq.read_table(path).drop(["detector_observed"])
    pq.write_table(legacy, path)
    rows = store.read([TrackObject.PLAYER], 0, 2).to_pylist()
    assert [row["detector_observed"] for row in rows] == [None, None, None]
