"""Spatial evidence revisions must invalidate the public analytics fold."""

from test_api import _seed_match

from bai_api.analytics import AnalyticsCache
from bai_engine.config import Settings
from bai_engine.schema import TrackObject, TrackSample, samples_to_table
from bai_engine.store import SessionRepository


def test_camera_quality_revision_invalidates_without_new_player_or_event(settings: Settings) -> None:
    sid = _seed_match(settings)
    repo = SessionRepository(settings.data_dir)
    try:
        cache = AnalyticsCache(repo)
        before = cache.get(sid)
        tracks = repo.tracks(sid)
        sample = TrackSample(frame_idx=0, obj=TrackObject.CAMERA, track_id=0, conf=0.9, cam=(1, 0, 0, 0, 1, 0, 0, 0, 1))
        tracks.write_chunk(TrackObject.CAMERA, 0, 0, samples_to_table([sample]))
        assert cache.get(sid) is not before
    finally:
        repo.close()
