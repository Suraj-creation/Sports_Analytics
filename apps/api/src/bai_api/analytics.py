"""Per-session analytics cache (rebuilt when the event log advances)."""

from __future__ import annotations

import threading

from bai_badminton.analytics.match import MatchAnalytics
from bai_badminton.analytics.rebuild import build
from bai_engine.store import SessionRepository


class AnalyticsCache:
    def __init__(self, repo: SessionRepository) -> None:
        self.repo = repo
        self._cache: dict[str, tuple[int, MatchAnalytics]] = {}
        self._lock = threading.Lock()

    def get(self, session_id: str) -> MatchAnalytics:
        s = self.repo.get(session_id)
        if s is None:
            raise KeyError(session_id)
        store = self.repo.events(session_id)
        seq = store.last_seq()
        with self._lock:
            hit = self._cache.get(session_id)
            if hit is not None and hit[0] == seq:
                return hit[1]
        fps = float(s.media.fps) if s.media else 30.0
        a = build(store, self.repo.tracks(session_id), fps)
        with self._lock:
            self._cache[session_id] = (seq, a)
        return a
