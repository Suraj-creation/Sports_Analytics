"""Read-only tools the agents use to ground every claim in the event store.

Every tool returns JSON that lists the ``event_id`` s it was computed from; the answer validator
only accepts citations to ids that some tool actually returned in the conversation.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from contextlib import AbstractContextManager, nullcontext
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
    outputs: list[str] = field(default_factory=list)  # every tool result of the conversation (grounding)
    _analytics: Any = None
    _analytics_token: tuple[Any, ...] | None = None
    read_scope: Callable[[], AbstractContextManager[None]] | None = None

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
        stat = self.store.path.stat()
        track_revision = (
            tuple(
                (kind, (self.tracks.root / kind).stat().st_mtime_ns if (self.tracks.root / kind).exists() else None)
                for kind in ("player", "camera")
            )
            if self.tracks is not None
            else ()
        )
        media = self.session.media
        token = (
            self.store.last_seq(),
            stat.st_ino,
            stat.st_mtime_ns,
            track_revision,
            media.fps_num if media else None,
            media.fps_den if media else None,
        )
        if self._analytics is None or token != self._analytics_token:
            from bai_badminton.analytics.rebuild import build

            fps = float(self.session.media.fps) if self.session.media else 30.0
            self._analytics = build(self.store, self.tracks, fps)
            self._analytics_token = token
        return self._analytics

    def t(self, frame: int) -> str:
        return self.session.media.timeline().format_frame(frame) if self.session.media else str(frame)

    def cite(self, ids: list[str]) -> list[str]:
        self.seen_ids.update(i for i in ids if i)
        return ids


def _official(ctx: ToolContext) -> tuple[list[Any], list[Any]]:
    from bai_badminton.analytics.rebuild import rally_records

    recs = rally_records(ctx.store)
    return [r for r in recs if r.official], [r for r in recs if not r.official]


def match_overview(ctx: ToolContext) -> dict[str, Any]:
    official, unofficial = _official(ctx)
    snap = ctx.store.state_at(10**12)
    games = [e for e in ctx.store.query(types=["game_end"])]
    degraded = [e.payload for e in ctx.store.query(types=["degraded"])]
    phases = ctx.store.query(types=["match_phase"])
    points = ctx.store.query(types=["point"])
    phase = next((e for e in reversed(phases) if not e.payload.get("marker") and not e.payload.get("base_state")), None)
    marker = next((e for e in reversed(phases) if e.payload.get("marker") == "match_start"), None)
    seeded = next((e for e in phases if e.payload.get("base_state")), None)
    state = snap.state if snap else None
    media = ctx.session.media
    last = media.n_frames - 1 if media else None
    return {
        "players": ctx.names,
        "status": ctx.session.status.value,
        "official_rallies": len(official),
        "unofficial_rallies": len(unofficial),
        "unofficial_note": "exchanges not established as official play; excluded from score and official statistics",
        "rallies_without_winner": sum(1 for r in official if r.winner is None),
        "current_state": state,
        "match_phase": {
            "phase": phase.payload.get("phase") if phase else "unknown",
            "reason": phase.payload.get("reason") if phase else "no rally decided yet",
            "match_start_marked_at": ctx.t(marker.payload["frame"])
            if marker and marker.payload.get("frame") is not None
            else None,
        },
        "observation": {
            "video_length": ctx.t(last) if last is not None else None,
            "analysed_until": ctx.t(ctx.session.frontier_frame),
            "active_play_s": round(sum(r.duration_s for r in official), 1),
            "score_basis": "scoreboard: the video starts mid-game, the score before it is read from the board"
            if seeded
            else "counted from the first observed official rally (0-0 assumed)",
            "match_finished": bool(state and state.get("winner")),
        },
        "games": [
            {
                "game_no": g.payload.get("game_no"),
                "winner": ctx.names.get(g.payload.get("winner"), None),
                "score": g.payload.get("score"),
                "event_id": g.event_id,
            }
            for g in games
        ],
        "score_event_id": points[-1].event_id if points else None,
        "data_quality": {
            "degraded": ctx.session.meta.get("degraded", degraded),
            "capabilities": ctx.session.meta.get("capabilities", {}),
            "calibration_recorded": bool(ctx.store.query(types=["calibration"])),
            "note": "CV events are estimates unless human reviewed. Calibration validity is frame-specific; "
            "a recorded calibration alone does not establish valid geometry throughout the clip.",
        },
        "evidence_ids": ctx.cite(
            [g.event_id for g in games]
            + ([points[-1].event_id] if points else [])
            + ([phase.event_id] if phase else [])
            + ([seeded.event_id] if seeded else [])
        ),
    }


def list_rallies(
    ctx: ToolContext,
    winner: str | None = None,
    outcome: str | None = None,
    min_shots: int | None = None,
    game: int | None = None,
    limit: int | None = None,
    include_unofficial: bool | None = None,
) -> dict[str, Any]:
    from bai_badminton.analytics.rebuild import rally_records

    pid = ctx.resolve_player(winner)
    rows: list[dict[str, Any]] = []
    for r in rally_records(ctx.store):
        if not r.official and not include_unofficial:
            continue
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
                "rally_no": r.rally_no if r.official else None,
                "official": r.official,
                "game": r.game_no,
                "time": ctx.t(r.start),
                "winner": ctx.names.get(r.winner or "", None),
                "outcome": r.outcome,
                "shots": r.n_shots,
                "score_after": r.score_after if r.official and r.score_available else None,
                "score_available": r.official and r.score_available,
                "duration_s": round(r.duration_s, 1),
            }
        )
    rows = rows[: min(limit or 40, 100)]
    return {"rallies": rows, "count": len(rows), "evidence_ids": ctx.cite([r["rally_event_id"] for r in rows])}


def get_rally(ctx: ToolContext, rally_event_id: str | None = None, rally_no: int | None = None) -> dict[str, Any]:
    from bai_badminton.analytics.rebuild import lineage_ids, rally_records

    records = {record.rally_id: record for record in rally_records(ctx.store)}
    ev = None
    # Use the same append-only rally versions whose shots were resolved above.
    # A second live-view query can observe a newer correction absent in records.
    for record in records.values():
        candidate = ctx.store.get(record.rally_id)
        if candidate is None:
            continue
        if (rally_event_id and rally_event_id in lineage_ids(ctx.store, candidate)) or (
            not rally_event_id and rally_no is not None and candidate.payload.get("rally_no") == rally_no
        ):
            ev = candidate
            break
    if ev is None or ev.type != "rally_end":
        official, _ = _official(ctx)
        return {
            "error": "no such rally in this match's data",
            "official_rallies": f"numbered 1..{len(official)}" if official else "none analysed",
            "hint": "rally ids come from list_rallies; never construct one",
            "evidence_ids": [],
        }
    shots = []
    for s in records[ev.event_id].shots:
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
                "status": st.status.value if st else None,
                "evidence_kind": st.payload.get("evidence_kind", "estimated") if st else "unavailable",
                "model": st.provenance.model if st else None,
            }
        )
    rally_ids = set(lineage_ids(ctx.store, ev))
    points = [p for p in ctx.store.query(types=["point"]) if p.parent_id in rally_ids]
    pt = points[-1] if points else None
    ids = [ev.event_id] + [s["stroke_event_id"] for s in shots if s["stroke_event_id"]] + ([pt.event_id] if pt else [])
    return {
        "rally_event_id": ev.event_id,
        "rally_no": ev.payload.get("rally_no"),
        "official": ev.payload.get("official", True),
        "phase_reason": ev.payload.get("phase_reason"),
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
    counted = {s.get("event_id") for r in a.rallies for s in r.shots}
    smashes = [
        e.event_id
        for e in ctx.store.query(types=["stroke"], player_id=pid)
        if e.payload.get("stroke") == "smash" and e.event_id in counted
    ]
    return {
        "player": ctx.names[pid],
        "player_id": pid,
        "stats": stats,
        "rallies_won": len(won),
        "rally_ids_won": won[:60],
        "smash_event_ids": smashes[:40],
        "scope": "official rallies observed in this video only (warm-up excluded); distance is an estimate in court metres "
        "only where distance_quality supports it; null means unavailable",
        "evidence_ids": ctx.cite(won[:60] + smashes[:40]),
    }


def find_strokes(
    ctx: ToolContext,
    player: str | None = None,
    stroke: str | None = None,
    subtype: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    pid = ctx.resolve_player(player)
    official, _ = _official(ctx)
    owned = {s.get("event_id") for r in official for s in r.shots}
    out = []
    for e in ctx.store.query(types=["stroke"], player_id=pid):
        if e.event_id not in owned:
            continue
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
                "status": e.status.value,
                "evidence_kind": p.get("evidence_kind", "estimated"),
                "model": e.provenance.model,
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
            "Players, analysis status, current score/state, finished games, match phase (warm-up vs official play), what part of the match the video covers, and data-quality flags. Call this first.",
            _obj({}),
        ),
        match_overview,
    ),
    "list_rallies": (
        ToolSpec(
            "list_rallies",
            "List official rallies, optionally filtered by winner (name or P1/P2), outcome (out | net | winner | unknown), minimum number of shots or game number. include_unofficial=true also lists warm-up / replayed exchanges (not scored).",
            _obj(
                {
                    "winner": _nullable("string"),
                    "outcome": _nullable("string", enum=["out", "net", "winner", "unknown", None]),
                    "min_shots": _nullable("integer"),
                    "game": _nullable("integer"),
                    "limit": _nullable("integer"),
                    "include_unofficial": _nullable("boolean"),
                }
            ),
        ),
        list_rallies,
    ),
    "get_rally": (
        ToolSpec(
            "get_rally",
            "Full detail of one rally by rally_event_id (from list_rallies) or by official rally number: shot sequence with stroke labels and confidence, outcome, score before/after, pressure flags.",
            _obj({"rally_event_id": _nullable("string"), "rally_no": _nullable("integer")}),
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
    with ctx.read_scope() if ctx.read_scope else nullcontext():
        try:
            out = json.dumps(fn(ctx, **clean), default=str)
        except TypeError as e:
            out = json.dumps({"error": f"bad arguments: {e}"})
    ctx.outputs.append(out)
    return out
