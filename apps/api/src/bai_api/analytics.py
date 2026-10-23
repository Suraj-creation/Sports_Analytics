"""Per-session analytics cache (rebuilt when the event log advances)."""

from __future__ import annotations

import threading
from collections import OrderedDict

from bai_badminton.analytics.match import MatchAnalytics
from bai_badminton.analytics.rebuild import build
from bai_engine.store import SessionRepository


class AnalyticsCache:
    def __init__(self, repo: SessionRepository) -> None:
        self.repo = repo
        self._cache: OrderedDict[str, tuple[tuple[object, ...], MatchAnalytics]] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, session_id: str) -> MatchAnalytics:
        s = self.repo.get(session_id)
        if s is None:
            raise KeyError(session_id)
        store = self.repo.events(session_id)
        # Sequence numbers restart when reanalysis replaces the database. Tracks
        # can also advance without a new rally/event. Both invalidate the fold.
        stat = store.path.stat()
        tracks_dir = self.repo.paths(session_id).tracks
        track_revision = tuple(
            (kind, (tracks_dir / kind).stat().st_mtime_ns if (tracks_dir / kind).exists() else None)
            for kind in ("player", "camera")
        )
        token = (
            store.last_seq(),
            stat.st_ino,
            stat.st_mtime_ns,
            track_revision,
            s.frontier_frame,
            s.analysed_frames,
            s.media.fps_num if s.media else None,
            s.media.fps_den if s.media else None,
        )
        with self._lock:
            hit = self._cache.get(session_id)
            if hit is not None and hit[0] == token:
                self._cache.move_to_end(session_id)
                return hit[1]
        fps = float(s.media.fps) if s.media else 30.0
        a = build(store, self.repo.tracks(session_id), fps)
        with self._lock:
            self._cache[session_id] = (token, a)
            self._cache.move_to_end(session_id)
            while len(self._cache) > 128:
                self._cache.popitem(last=False)
        return a
