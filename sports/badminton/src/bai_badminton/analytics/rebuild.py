"""Rebuild match analytics from the canonical store (events + tracks).

Analytics are a pure fold over the live event view, so any process (API, agents, exports) can
reconstruct them — including after corrections — without access to the engine's memory.
"""

from __future__ import annotations

import numpy as np

from bai_badminton.analytics.match import MatchAnalytics, RallyRecord
from bai_engine.schema import Event, TrackObject
from bai_engine.store import EventStore, TrackStore


def lineage_ids(store: EventStore, ev: Event) -> list[str]:
    """``ev``'s id and the ids it superseded, newest first — children (a point's parent_id) may
    still reference an earlier version after a verification or correction."""
    ids = [ev.event_id]
    cur: Event | None = ev
    while cur is not None and cur.supersedes and cur.supersedes not in ids:
        ids.append(cur.supersedes)
        cur = store.get(cur.supersedes)
    return ids


def rally_records(store: EventStore) -> list[RallyRecord]:
    rallies = store.query(types=["rally_end"])
    points = {p.parent_id: p for p in store.query(types=["point"])}
    out: list[RallyRecord] = []
    for r in rallies:
        p = next((points[i] for i in lineage_ids(store, r) if i in points), None)
        pay = r.payload
        if p is not None:
            after = p.payload["state_after"]
            before = p.payload["state_before"]
            if "game_end" in p.payload.get("transitions", []):
                g = after["completed_games"][-1]
                score_after = {"P1": g[0], "P2": g[1]}
            else:
                score_after = dict(after["score"])
            game_no, flags = int(before["game_no"]), dict(p.payload.get("flags_before", {}))
        else:
            score_after, game_no, flags = {"P1": 0, "P2": 0}, 1, {}
        out.append(
            RallyRecord(
                rally_id=r.event_id,
                rally_no=int(pay.get("rally_no", len(out) + 1)),
                start=r.frame_start,
                end=r.frame_end,
                winner=pay.get("winner"),
                loser=pay.get("loser"),
                outcome=str(pay.get("outcome", "unknown")),
                shots=list(pay.get("shots", [])),
                score_after=score_after,
                game_no=game_no,
                flags_before=flags,
                duration_s=float(pay.get("duration_s", 0.0)),
            )
        )
    return out


def build(store: EventStore, tracks: TrackStore | None, fps: float) -> MatchAnalytics:
    a = MatchAnalytics(fps)
    for ev in store.query(types=["stroke"]):
        a.on_stroke(ev)
    for rec in rally_records(store):
        if tracks is not None:
            t = tracks.read([TrackObject.PLAYER], rec.start, rec.end)
            if t.num_rows:
                pid = np.asarray(t["player_id"].to_pylist(), dtype=object)
                cx = np.asarray(t["court_x"].to_pylist(), dtype=float)
                cy = np.asarray(t["court_y"].to_pylist(), dtype=float)
                for player in ("P1", "P2"):
                    m = (pid == player) & np.isfinite(cx) & np.isfinite(cy)
                    if m.any():
                        a.on_presence(player, list(zip(cx[m], cy[m], strict=True)))
        a.on_rally(rec)
    return a
