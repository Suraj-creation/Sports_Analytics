"""Transport regressions, including observations emitted on real badminton footage."""

import json
from pathlib import Path

from bai_engine.schema import TrackObject, TrackSample
from bai_engine.wire import decode_tracks, encode_tracks


def test_real_anonymous_player_poses_survive_transport() -> None:
    fixture = json.loads((Path(__file__).parent / "fixtures" / "anonymous_real_tracks.json").read_text())
    samples = [TrackSample.model_validate(row) for row in fixture["samples"]]
    assert len(samples) == 4 and all(row.player_id is None and row.keypoints for row in samples)
    wire = decode_tracks(encode_tracks(samples, 10200, 10201))
    assert wire["players"] == {}  # No invented named player identity.
    assert sum(len(p["f"]) for p in wire["anonymous"].values()) == len(samples)
    assert {p["t"][0] for p in wire["anonymous"].values()} == {32, 34}
    for p in wire["anonymous"].values():
        assert len(p["k"]) == 51 * len(p["f"])
        assert p["m"] == [True, False]
        assert all(p["obs"])


def test_four_players_and_reused_tracker_ids_remain_distinct() -> None:
    samples = [
        TrackSample(
            frame_idx=0,
            obj=TrackObject.PLAYER,
            track_id=i,
            participant_observation_id=f"episode-{i}",
            bbox=(i, 0, i + 1, 2),
        )
        for i in range(4)
    ]
    samples.append(samples[0].model_copy(update={"frame_idx": 1, "participant_observation_id": "new-epoch"}))
    wire = decode_tracks(encode_tracks(samples, 0, 1))
    assert len(wire["anonymous"]) == 5
    assert sum(p["f"].count(0) for p in wire["anonymous"].values()) == 4


def test_missing_or_malformed_pose_cannot_shift_next_person_frame() -> None:
    bad = TrackSample(frame_idx=0, obj=TrackObject.PLAYER, player_id="P1", bbox=(0, 0, 1, 2), keypoints=((1, 2, 0.9),))
    good = bad.model_copy(update={"frame_idx": 1, "keypoints": tuple((1, 2, 0.9) for _ in range(17))})
    p = decode_tracks(encode_tracks([bad, good], 0, 1))["players"]["P1"]
    assert p["k"][:51] == [0.0] * 51
    assert p["k"][51:] == [1.0, 2.0, 0.9] * 17
