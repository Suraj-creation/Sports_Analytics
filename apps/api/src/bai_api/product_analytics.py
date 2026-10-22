"""Product projections over the same canonical analytics used by reports/agents.

No inferred athlete identity or model accuracy claims live here. Cross-session
identity is explicitly a normalized user-entered display name, not a biometric
identity. Point win rates divide known points won by known points played.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from bai_api.analytics import AnalyticsCache
from bai_api.public import public_session
from bai_badminton.analytics.match import MatchAnalytics, RallyRecord
from bai_engine.schema import Session, SessionStatus
from bai_engine.store import SessionRepository


class Availability(BaseModel):
    analytics: bool
    partial: bool
    reason: str | None


class Lineage(BaseModel):
    event_seq: int
    source: Literal["canonical_events_and_tracks"] = "canonical_events_and_tracks"
    metric_version: int = 1


class Capabilities(BaseModel):
    doubles_individual_tracking: bool = False
    shot_speed: bool = False
    player_identity: Literal["explicit_session_names"] = "explicit_session_names"
    challenges: bool = False


class ProductMatch(BaseModel):
    session: Session
    analytics: dict[str, Any] | None
    availability: Availability
    highlights: list[dict[str, Any]]
    lineage: Lineage


class PlayerHistory(BaseModel):
    session_id: str
    title: str
    created_at: datetime
    player_id: str
    points_won: int | None
    points_lost: int | None
    win_rate: float | None
    rallies: int | None
    strokes: dict[str, int] | None
    distance_m: float | None


class Person(BaseModel):
    person_id: str
    name: str
    matches: int
    session_ids: list[str]
    points_won: int | None
    points_lost: int | None
    win_rate: float | None
    strokes: dict[str, int] | None
    distance_m: float | None
    history: list[PlayerHistory]


class ProgressHistory(BaseModel):
    session_id: str
    created_at: datetime
    rallies: int
    active_play_s: float
    avg_rally_shots: float | None


class ProgressRecord(BaseModel):
    key: str
    label: str
    value: float
    unit: str
    session_id: str
    frame: int | None = None


class Progress(BaseModel):
    named_players: int
    analysed_matches: int
    total_rallies: int
    active_play_s: float
    history: list[ProgressHistory]
    records: list[ProgressRecord] = Field(default_factory=list)


class OverviewScope(BaseModel):
    limit: int
    returned_matches: int
    truncated: bool


class Overview(BaseModel):
    schema_version: int = 1
    generated_at: datetime
    matches: list[ProductMatch]
    people: list[Person]
    progress: Progress
    scope: OverviewScope
    capabilities: Capabilities = Field(default_factory=Capabilities)
    identity_note: str = "People are grouped by explicit session names; matching names do not verify identity."


def availability(session: Session, analytics: MatchAnalytics | None) -> Availability:
    partial = session.status != SessionStatus.ANALYSED
    if partial:
        return Availability(analytics=False, partial=True, reason="Analysis is not complete for this recording.")
    if analytics is None or not (analytics.rallies or analytics.unofficial):
        return Availability(analytics=False, partial=False, reason="No segmented rally evidence is available.")
    return Availability(analytics=True, partial=False, reason=None)


def _public_analytics(analytics: MatchAnalytics) -> dict[str, Any]:
    data: dict[str, Any] = analytics.to_public()
    for pid, stats in data["players"].items():
        if (pid, "presence") not in analytics.heatmaps.grids:
            stats["distance_m"] = None
    return data


def _point_rate(won: int, lost: int) -> float | None:
    return round(won / (won + lost), 3) if won + lost else None


def _people(matches: list[ProductMatch]) -> list[Person]:
    grouped: dict[str, tuple[str, list[PlayerHistory]]] = {}
    for item in reversed(matches):  # histories are chronological
        for player in item.session.players:
            name = " ".join((player.name or "").split())
            if not name or name.casefold() in {"p1", "p2", "player 1", "player 2"}:
                continue
            key = name.casefold()
            stats = (item.analytics or {}).get("players", {}).get(player.player_id)
            row = PlayerHistory(
                session_id=item.session.session_id,
                title=item.session.title,
                created_at=item.session.created_at,
                player_id=player.player_id,
                points_won=stats["points_won"] if stats is not None else None,
                points_lost=stats["points_lost"] if stats is not None else None,
                win_rate=stats["win_rate"] if stats is not None else None,
                rallies=item.analytics["rallies"] if item.analytics is not None else None,
                strokes=stats["strokes"] if stats is not None else None,
                distance_m=stats["distance_m"] if stats is not None else None,
            )
            if key not in grouped:
                grouped[key] = (name, [])
            grouped[key][1].append(row)
    people = []
    for key, (name, history) in grouped.items():
        known = [h for h in history if h.points_won is not None]
        won = sum(h.points_won or 0 for h in known)
        lost = sum(h.points_lost or 0 for h in known)
        strokes: Counter[str] = Counter()
        for row in known:
            strokes.update(row.strokes or {})
        distances = [h.distance_m for h in known if h.distance_m is not None]
        session_ids = list(dict.fromkeys(h.session_id for h in history))
        people.append(
            Person(
                person_id=hashlib.sha256(key.encode()).hexdigest()[:20],
                name=name,
                matches=len(session_ids),
                session_ids=session_ids,
                points_won=won if known else None,
                points_lost=lost if known else None,
                win_rate=_point_rate(won, lost) if known else None,
                strokes=dict(strokes) if known else None,
                distance_m=round(sum(distances), 1) if distances else None,
                history=history,
            )
        )
    return sorted(people, key=lambda p: p.name.casefold())


def overview(repo: SessionRepository, cache: AnalyticsCache, limit: int = 500) -> Overview:
    matches: list[ProductMatch] = []
    history: list[ProgressHistory] = []
    longest: tuple[Session, RallyRecord] | None = None
    active_record: tuple[Session, float] | None = None
    sessions = repo.list(limit + 1)
    for session in sessions[:limit]:
        fold = cache.get(session.session_id) if session.status == SessionStatus.ANALYSED else None
        available = availability(session, fold)
        data = _public_analytics(fold) if fold is not None and available.analytics else None
        # Media is delivered only through authorized /hls or /proxy.mp4 routes.
        matches.append(
            ProductMatch(
                session=public_session(session),
                analytics=data,
                availability=available,
                highlights=[h.to_public() for h in fold.highlights(k=10)] if fold and data is not None else [],
                lineage=Lineage(event_seq=repo.events(session.session_id).last_seq()),
            )
        )
        if fold is not None and data is not None:
            history.append(
                ProgressHistory(
                    session_id=session.session_id,
                    created_at=session.created_at,
                    rallies=data["rallies"],
                    active_play_s=data["active_play_s"],
                    avg_rally_shots=data["avg_rally_shots"],
                )
            )
            for rally in fold.rallies:
                if rally.n_shots > 0 and (longest is None or rally.n_shots > longest[1].n_shots):
                    longest = (session, rally)
            if active_record is None or data["active_play_s"] > active_record[1]:
                active_record = (session, data["active_play_s"])
    people = _people(matches)
    records = []
    if longest is not None:
        records.append(
            ProgressRecord(
                key="longest_rally",
                label="Longest observed rally",
                value=longest[1].n_shots,
                unit="shots",
                session_id=longest[0].session_id,
                frame=longest[1].start,
            )
        )
    if active_record is not None:
        records.append(
            ProgressRecord(
                key="active_play",
                label="Most active play in a recording",
                value=active_record[1],
                unit="seconds",
                session_id=active_record[0].session_id,
            )
        )
    return Overview(
        generated_at=datetime.now(UTC),
        matches=matches,
        people=people,
        scope=OverviewScope(limit=limit, returned_matches=len(matches), truncated=len(sessions) > limit),
        progress=Progress(
            named_players=len(people),
            analysed_matches=len(history),
            total_rallies=sum(h.rallies for h in history),
            active_play_s=round(sum(h.active_play_s for h in history), 1),
            history=list(reversed(history)),
            records=records,
        ),
    )


def _tactics(analytics: MatchAnalytics, pid: str) -> dict[str, Any]:
    served = [
        r for r in analytics.rallies if r.shots and r.shots[0].get("is_serve") and r.shots[0].get("player_id") == pid
    ]
    returned = [
        r
        for r in analytics.rallies
        if len(r.shots) > 1
        and r.shots[0].get("is_serve")
        and r.shots[0].get("player_id") != pid
        and r.shots[1].get("player_id") == pid
    ]
    known_serves = [r for r in served if r.winner in ("P1", "P2")]
    known_returns = [r for r in returned if r.winner in ("P1", "P2")]
    stats = analytics.players.get(pid)
    strokes = stats.strokes if stats is not None else Counter()
    total = sum(strokes.values())
    serve_won = sum(r.winner == pid for r in known_serves)
    return_won = sum(r.winner == pid for r in known_returns)
    buckets = []
    for label, low, high in (("1–4 shots", 1, 4), ("5–8 shots", 5, 8), ("9+ shots", 9, 10**9)):
        rallies = [r for r in analytics.rallies if low <= r.n_shots <= high and r.winner in ("P1", "P2")]
        won = sum(r.winner == pid for r in rallies)
        buckets.append(
            {
                "label": label,
                "rallies": len(rallies),
                "points_won": won,
                "win_rate": round(won / len(rallies), 3) if rallies else None,
            }
        )
    return {
        "serves": len(served),
        "serve_rallies": len(known_serves),
        "serve_points_won": serve_won,
        "serve_win_rate": round(serve_won / len(known_serves), 3) if known_serves else None,
        "returns": len(returned),
        "return_rallies": len(known_returns),
        "return_points_won": return_won,
        "return_win_rate": round(return_won / len(known_returns), 3) if known_returns else None,
        "shot_distribution": [
            {"stroke": stroke, "count": count, "share": round(count / total, 3)}
            for stroke, count in sorted(strokes.items())
            if count > 0
        ],
        "rally_length": buckets,
    }


def insights(repo: SessionRepository, cache: AnalyticsCache, session: Session) -> dict[str, Any]:
    fold = cache.get(session.session_id)
    available = availability(session, fold)
    store = repo.events(session.session_id)
    evidence = {ev.event_id: ev for ev in store.query(types=["rally_end"])}
    rows = []
    for rally in sorted(fold.rallies + fold.unofficial, key=lambda r: (r.start, r.end)):
        event = evidence[rally.rally_id]
        rows.append(
            {
                "rally_id": rally.rally_id,
                "rally_no": rally.rally_no,
                "frame_start": rally.start,
                "frame_end": rally.end,
                "start_s": round(rally.start / fold.fps, 3),
                "end_s": round(rally.end / fold.fps, 3),
                "duration_s": rally.duration_s,
                "n_shots": rally.n_shots,
                "winner": rally.winner,
                "loser": rally.loser,
                "outcome": rally.outcome,
                "official": rally.official,
                "game_no": rally.game_no,
                "score_after": rally.score_after,
                "shots": rally.shots,
                "confidence": event.confidence,
                "band": event.band.value,
                "status": event.status.value,
            }
        )
    return {
        "schema_version": 1,
        "session_id": session.session_id,
        "availability": available.model_dump(),
        "lineage": Lineage(event_seq=store.last_seq()).model_dump(),
        "rallies": rows,
        "tactics": {pid: _tactics(fold, pid) for pid in ("P1", "P2")} if available.analytics else None,
        "capabilities": Capabilities().model_dump(),
        "definitions": {
            "serve_win_rate": "Points won / rallies with a known winner whose first shot is this player's serve.",
            "return_win_rate": (
                "Points won / rallies with a known winner and this player's observed second-shot return."
            ),
            "rally_length": "Official rallies with a known winner, grouped by the number of observed shots.",
            "distance_m": (
                "Sum of accepted court-coordinate displacements during official rallies; "
                "displacements over 1.5 m between adjacent observed positions are rejected."
            ),
        },
    }
