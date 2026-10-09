"""Read-only tools the agents use to ground every claim in the event store.

Every tool returns JSON that lists the ``event_id`` s it was computed from; the answer validator
only accepts citations to ids that some tool actually returned in the conversation.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from bai_agents.kb import get_kb
from bai_agents.providers import ToolSpec
from bai_engine.schema import Session
from bai_engine.store import EventStore, TrackStore


def _obj(props: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    # strict tools: every property listed in required; optional ones accept null
    return {
        "type": "object",
        "properties": props,
        "required": required if required is not None else list(props),
        "additionalProperties": False,
    }


def _nullable(t: str, **kw: Any) -> dict[str, Any]:
    return {"type": [t, "null"], **kw}


@dataclass
class ToolContext:
    session: Session
    store: EventStore
    tracks: TrackStore | None
    seen_ids: set[str] = field(default_factory=set)
    kb_refs: set[str] = field(default_factory=set)
    _analytics: Any = None

    @property
    def names(self) -> dict[str, str]:
        return {p.player_id: p.name or p.player_id for p in self.session.players}

    def resolve_player(self, who: str | None) -> str | None:
        if not who:
            return None
        w = who.strip().lower()
        if w in ("p1", "p2"):
            return w.upper()
        for pid, name in self.names.items():
            n = name.lower()
            if w == n or w in n or (n.split() and n.split()[-1] == w.split()[-1]):
                return pid
        return None

    def analytics(self) -> Any:
        if self._analytics is None:
            from bai_badminton.analytics.rebuild import build

            fps = float(self.session.media.fps) if self.session.media else 30.0
            self._analytics = build(self.store, self.tracks, fps)
        return self._analytics

    def t(self, frame: int) -> str:
        return self.session.media.timeline().format_frame(frame) if self.session.media else str(frame)

    def cite(self, ids: list[str]) -> list[str]:
        self.seen_ids.update(i for i in ids if i)
        return ids


def match_overview(ctx: ToolContext) -> dict[str, Any]:
    from bai_badminton.analytics.rebuild import rally_records

    recs = rally_records(ctx.store)
    snap = ctx.store.state_at(10**12)
    games = [e for e in ctx.store.query(types=["game_end"])]
    degraded = [e.payload for e in ctx.store.query(types=["degraded"])]
    unknown = sum(1 for r in recs if r.winner is None)
    return {
        "players": ctx.names,
        "status": ctx.session.status.value,
        "rallies_analysed": len(recs),
        "rallies_without_winner": unknown,
        "current_state": snap.state if snap else None,
        "games": [
            {
                "game_no": g.payload.get("game_no"),
                "winner": ctx.names.get(g.payload.get("winner"), None),
                "score": g.payload.get("score"),
                "event_id": g.event_id,
            }
            for g in games
        ],
        "data_quality": {"degraded": degraded, "calibrated": bool(ctx.store.query(types=["calibration"]))},
        "evidence_ids": ctx.cite([g.event_id for g in games]),
    }


def list_rallies(
    ctx: ToolContext,
    winner: str | None = None,
    outcome: str | None = None,
    min_shots: int | None = None,
    game: int | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    from bai_badminton.analytics.rebuild import rally_records

    pid = ctx.resolve_player(winner)
    rows = []
    for r in rally_records(ctx.store):
        if winner and r.winner != pid:
            continue
        if outcome and r.outcome != outcome:
            continue
        if min_shots and r.n_shots < min_shots:
            continue
        if game and r.game_no != game:
            continue
        rows.append(
            {
                "rally_event_id": r.rally_id,
                "rally_no": r.rally_no,
                "game": r.game_no,
                "time": ctx.t(r.start),
                "winner": ctx.names.get(r.winner or "", None),
                "outcome": r.outcome,
                "shots": r.n_shots,
                "score_after": r.score_after,
                "duration_s": round(r.duration_s, 1),
            }
        )
    rows = rows[: min(limit or 40, 100)]
    return {"rallies": rows, "count": len(rows), "evidence_ids": ctx.cite([r["rally_event_id"] for r in rows])}


def get_rally(ctx: ToolContext, rally_event_id: str) -> dict[str, Any]:
    ev = ctx.store.get(rally_event_id)
    if ev is None or ev.type != "rally_end":
        return {"error": "unknown rally id", "evidence_ids": []}
    shots = []
    for s in ev.payload.get("shots", []):
        st = ctx.store.get(s["event_id"]) if s.get("event_id") else None
        shots.append(
            {
                "stroke_event_id": s.get("event_id"),
                "time": ctx.t(s["frame"]),
                "player": ctx.names.get(s.get("player_id") or "", None),
                "stroke": s.get("stroke"),
                "subtype": s.get("subtype"),
                "confidence": st.confidence if st else None,
                "band": st.band.value if st else None,
            }
        )
    points = [p for p in ctx.store.query(types=["point"]) if p.parent_id == ev.event_id]
    pt = points[-1] if points else None
    ids = [ev.event_id] + [s["stroke_event_id"] for s in shots if s["stroke_event_id"]] + ([pt.event_id] if pt else [])
    return {
        "rally_event_id": ev.event_id,
        "rally_no": ev.payload.get("rally_no"),
        "time": ctx.t(ev.frame_start),
        "duration_s": ev.payload.get("duration_s"),
        "winner": ctx.names.get(ev.payload.get("winner") or "", None),
        "outcome": ev.payload.get("outcome"),
        "winner_source": ev.payload.get("winner_source"),
        "confidence": ev.confidence,
        "shots": shots,
        "score_before": pt.payload["state_before"]["score"] if pt else None,
        "score_after": pt.payload["state_after"]["score"] if pt else None,
        "pressure": pt.payload.get("flags_before") if pt else None,
        "evidence_ids": ctx.cite(ids),
    }


def player_stats(ctx: ToolContext, player: str) -> dict[str, Any]:
    pid = ctx.resolve_player(player)
    if pid is None:
        return {"error": f"unknown player {player!r}; players are {ctx.names}", "evidence_ids": []}
    a = ctx.analytics()
    stats = a.players[pid].to_public() if pid in a.players else {}
    won = [r.rally_id for r in a.rallies if r.winner == pid]
    return {
        "player": ctx.names[pid],
        "player_id": pid,
        "stats": stats,
        "rallies_won": len(won),
        "evidence_ids": ctx.cite(won[:60]),
    }


def find_strokes(
    ctx: ToolContext,
    player: str | None = None,
    stroke: str | None = None,
    subtype: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    pid = ctx.resolve_player(player)
    out = []
    for e in ctx.store.query(types=["stroke"], player_id=pid):
        p = e.payload
        if stroke and p.get("stroke") != stroke:
            continue
        if subtype and p.get("subtype") != subtype:
            continue
        out.append(
            {
                "stroke_event_id": e.event_id,
                "time": ctx.t(e.frame_start),
                "player": ctx.names.get(e.actors.player_id or "", None),
                "stroke": p.get("stroke"),
                "subtype": p.get("subtype"),
                "confidence": e.confidence,
                "band": e.band.value,
            }
        )
    out = out[: min(limit or 40, 100)]
    return {"strokes": out, "count": len(out), "evidence_ids": ctx.cite([s["stroke_event_id"] for s in out])}


def top_highlights(ctx: ToolContext, k: int | None = None, player: str | None = None) -> dict[str, Any]:
    pid = ctx.resolve_player(player)
    hl = ctx.analytics().highlights(k=min(k or 8, 20), player=pid)
    rows = [{**h.to_public(), "time": ctx.t(h.start), "player": ctx.names.get(h.player or "", None)} for h in hl]
    return {"highlights": rows, "evidence_ids": ctx.cite([h.rally_id for h in hl])}


def momentum(ctx: ToolContext) -> dict[str, Any]:
    a = ctx.analytics()
    shifts = [{**m, "to": ctx.names.get(m["to"], m["to"])} for m in a.momentum_shifts]
    return {
        "shifts": shifts,
        "recent": a.momentum[-12:],
        "evidence_ids": ctx.cite([m["rally_id"] for m in a.momentum_shifts]),
    }


def rules_and_background(ctx: ToolContext, query: str) -> dict[str, Any]:
    hits = get_kb(ctx.session.sport).search(query, k=4)
    ctx.kb_refs.update(p.ref for p, _ in hits)
    return {
        "passages": [{"ref": p.ref, "source": p.doc, "text": p.text} for p, _ in hits],
        "note": "Background only — never use it for what happened in this match.",
        "evidence_ids": [],
    }


TOOLS: dict[str, tuple[ToolSpec, Callable[..., dict[str, Any]]]] = {
    "match_overview": (
        ToolSpec(
            "match_overview",
            "Players, analysis status, current score/state, finished games and data-quality flags.",
            _obj({}),
        ),
        match_overview,
    ),
    "list_rallies": (
        ToolSpec(
            "list_rallies",
            "List rallies, optionally filtered by winner (name or P1/P2), outcome (out | net | winner | unknown), minimum number of shots or game number.",
            _obj(
                {
                    "winner": _nullable("string"),
                    "outcome": _nullable("string", enum=["out", "net", "winner", "unknown", None]),
                    "min_shots": _nullable("integer"),
                    "game": _nullable("integer"),
                    "limit": _nullable("integer"),
                }
            ),
        ),
        list_rallies,
    ),
    "get_rally": (
        ToolSpec(
            "get_rally",
            "Full detail of one rally: shot sequence with stroke labels and confidence, outcome, score before/after, pressure flags.",
            _obj({"rally_event_id": {"type": "string"}}),
        ),
        get_rally,
    ),
    "player_stats": (
        ToolSpec(
            "player_stats",
            "Statistics for one player (name or P1/P2): points, winners, errors, strokes, smashes, distance, pressure points.",
            _obj({"player": {"type": "string"}}),
        ),
        player_stats,
    ),
    "find_strokes": (
        ToolSpec(
            "find_strokes",
            "Find strokes by player, stroke type (smash, clear, drop, drive, lift, push, net_shot, cross_net, rush, block, short_serve, long_serve) or subtype (jump_smash).",
            _obj(
                {
                    "player": _nullable("string"),
                    "stroke": _nullable("string"),
                    "subtype": _nullable("string"),
                    "limit": _nullable("integer"),
                }
            ),
        ),
        find_strokes,
    ),
    "top_highlights": (
        ToolSpec(
            "top_highlights",
            "Best rallies so far with categories (smash winner, comeback, deuce, …) and the score decomposition explaining the ranking; optional player filter.",
            _obj({"k": _nullable("integer"), "player": _nullable("string")}),
        ),
        top_highlights,
    ),
    "momentum": (ToolSpec("momentum", "Momentum series and momentum shifts.", _obj({})), momentum),
    "rules_and_background": (
        ToolSpec(
            "rules_and_background",
            "Search badminton rules, terminology and player biographies (background knowledge, not match facts).",
            _obj({"query": {"type": "string"}}),
        ),
        rules_and_background,
    ),
}


def run_tool(ctx: ToolContext, name: str, args: dict[str, Any]) -> str:
    entry = TOOLS.get(name)
    if entry is None:
        return json.dumps({"error": f"unknown tool {name}"})
    _, fn = entry
    clean = {k: v for k, v in args.items() if v is not None and not k.startswith("_")}
    try:
        return json.dumps(fn(ctx, **clean), default=str)
    except TypeError as e:
        return json.dumps({"error": f"bad arguments: {e}"})
