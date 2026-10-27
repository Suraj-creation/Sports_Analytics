from types import SimpleNamespace

import numpy as np

from bai_badminton.identity import IdentityResolver
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs
from bai_badminton.plugin import BadmintonSession
from bai_engine.schema import TrackObject


def test_seek_preview_emits_all_people_without_claiming_identity():
    session = BadmintonSession.__new__(BadmintonSession)
    session.perception = SimpleNamespace(ref_id=None)
    session.engine = SimpleNamespace(
        identity=IdentityResolver(frame_height=720),
        state=SimpleNamespace(ends={"P1": SimpleNamespace(value="near"), "P2": SimpleNamespace(value="far")}),
    )
    people = [PersonObs(track_id=i, bbox=np.array([10.0, 20.0, 30.0, float(100 + i)]), conf=0.9) for i in range(4)]
    fp = FramePerception(frame_idx=0, shuttle_xy=None, shuttle_conf=0.0, persons=people)
    rows = session.tracks_from_perception(ChunkPerception(start=0, end=0, frames=[fp]))
    players = [r for r in rows if r.obj == TrackObject.PLAYER]
    assert len(players) == 4
    assert {r.track_id for r in players} == {0, 1, 2, 3}
    assert all(r.player_id is None for r in players)
