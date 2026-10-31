from bai_engine.schema import TrackObject, TrackSample
from bai_engine.wire import decode_tracks, encode_tracks


def test_racket_observation_is_transmitted_separately_from_player_and_shuttle():
    sample = TrackSample(
        frame_idx=3,
        obj=TrackObject.RACKET,
        track_id=4,
        x=123,
        y=45,
        bbox=(110, 30, 136, 60),
        conf=0.8,
        model="opencv_ellipse_shaft_v1",
        participant_observation_id="birth",
    )
    wire = decode_tracks(encode_tracks([sample], 0, 10))
    assert wire["rackets"]["f"] == [3]
    assert wire["rackets"]["t"] == [4]
    assert wire["rackets"]["obs"] == ["birth"]
    assert wire["rackets"]["b"] == [110, 30, 136, 60]
    assert wire["players"] == {} and wire["shuttle"]["f"] == []
