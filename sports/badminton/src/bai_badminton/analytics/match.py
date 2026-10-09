"""Match analytics derived deterministically from the canonical event stream.

``MatchAnalytics`` is a fold over live events (strokes, rallies, points): it can be rebuilt from
the store at any time (after corrections) and updated incrementally while the engine runs.  It
owns per-player statistics, momentum and highlight discovery; every number it reports carries the
event ids it was computed from so agents can cite evidence.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any

from bai_badminton.analytics.heatmaps import HeatmapSet
from bai_badminton.ontology import get_ontology
from bai_engine.schema import Event


@dataclass
class RallyRecord:
    rally_id: str  # rally_end event id
    rally_no: int
    start: int
    end: int
    winner: str | None
    loser: str | None
    outcome: str
    shots: list[dict[str, Any]]
    score_after: dict[str, int]
    game_no: int
    flags_before: dict[str, Any]
    duration_s: float

    @property
    def n_shots(self) -> int:
        return len(self.shots)


@dataclass
class PlayerStats:
    points_won: int = 0
    points_lost: int = 0
    winners: int = 0  # rallies won because the shuttle landed in on the opponent
    errors_out: int = 0
    errors_net: int = 0
    strokes: Counter[str] = field(default_factory=Counter)
    smashes: int = 0
    jump_smashes: int = 0
    smash_points: int = 0
    serves: int = 0
    serve_points_won: int = 0
    distance_m: float = 0.0
    points_won_under_pressure: int = 0  # at game point (either side) or deuce

    def to_public(self) -> dict[str, Any]:
        played = self.points_won + self.points_lost
        return {
            "points_won": self.points_won,
            "points_lost": self.points_lost,
            "win_rate": round(self.points_won / played, 3) if played else None,
            "winners": self.winners,
            "errors_out": self.errors_out,
            "errors_net": self.errors_net,
            "strokes": dict(self.strokes),
            "smashes": self.smashes,
            "jump_smashes": self.jump_smashes,
            "smash_points": self.smash_points,
            "serves": self.serves,
            "serve_points_won": self.serve_points_won,
            "distance_m": round(self.distance_m, 1),
            "points_won_under_pressure": self.points_won_under_pressure,
        }


@dataclass
class Highlight:
    rally_id: str
    rally_no: int
    start: int
    end: int
    score: float  # 0–10
    categories: list[str]
    reasons: dict[str, float]  # decomposition of the score ("why ranked")
    player: str | None

    def to_public(self) -> dict[str, Any]:
        return {
            "rally_id": self.rally_id,
            "rally_no": self.rally_no,
            "frame_start": self.start,
            "frame_end": self.end,
            "score": round(self.score, 2),
            "categories": self.categories,
            "reasons": {k: round(v, 2) for k, v in self.reasons.items()},
            "player": self.player,
        }


class MatchAnalytics:
    def __init__(self, fps: float) -> None:
        self.fps = fps
        self.rallies: list[RallyRecord] = []
        self.players: dict[str, PlayerStats] = defaultdict(PlayerStats)
        self.heatmaps = HeatmapSet()
        self.momentum: list[dict[str, Any]] = []  # per point: {rally_no, value, leader}
        self._ewma = 0.0
        self._run: tuple[str | None, int] = (None, 0)
        self.momentum_shifts: list[dict[str, Any]] = []
        self.score_timeline: list[dict[str, Any]] = []

    # ------------------------------------------------------------------ ingestion
    def on_stroke(self, ev: Event) -> None:
        pid = ev.actors.player_id
        if pid is None:
            return
        st = ev.payload.get("stroke", "unknown")
        self.players[pid].strokes[st] += 1
        if st == "smash":
            self.players[pid].smashes += 1
            if ev.payload.get("subtype") == "jump_smash":
                self.players[pid].jump_smashes += 1
        if ev.payload.get("is_serve"):
            self.players[pid].serves += 1
        origin = ev.payload.get("hitter_court_xy")
        if origin:
            self.heatmaps.add(pid, "origin", *origin)
        landing = ev.payload.get("landing_court_xy")
        if landing:
            self.heatmaps.add(pid, "landing", *landing)
            opp = ev.payload.get("receiver_id")
            if opp:
                self.heatmaps.add(pid, "targeting", *landing)

    def on_stroke_retracted(self, ev: Event) -> None:
        pid = ev.actors.player_id
        if pid is None:
            return
        st = ev.payload.get("stroke", "unknown")
        ps = self.players[pid]
        if ps.strokes[st] > 0:
            ps.strokes[st] -= 1
        if st == "smash" and ps.smashes > 0:
            ps.smashes -= 1
            if ev.payload.get("subtype") == "jump_smash" and ps.jump_smashes > 0:
                ps.jump_smashes -= 1
        if ev.payload.get("is_serve") and ps.serves > 0:
            ps.serves -= 1

    def on_presence(self, player: str, court_xy: list[tuple[float, float]]) -> None:
        import numpy as np

        arr = np.asarray(court_xy, dtype=float).reshape(-1, 2)
        self.heatmaps.add_many(player, "presence", arr[:: max(1, int(self.fps // 5))])
        self.players[player].distance_m += self.heatmaps.add_path(player, arr)

    def on_rally(self, rally: RallyRecord) -> None:
        self.rallies.append(rally)
        if rally.winner is None or rally.loser is None:
            return
        w, lo = self.players[rally.winner], self.players[rally.loser]
        w.points_won += 1
        lo.points_lost += 1
        if rally.outcome == "winner":
            w.winners += 1
        elif rally.outcome == "out":
            lo.errors_out += 1
        elif rally.outcome == "net":
            lo.errors_net += 1
        last = rally.shots[-1] if rally.shots else None
        if last and last.get("player_id") == rally.winner and last.get("stroke") == "smash":
            w.smash_points += 1
        if rally.shots and rally.shots[0].get("player_id") == rally.winner and rally.shots[0].get("is_serve"):
            w.serve_points_won += 1
        if rally.flags_before.get("game_point") or rally.flags_before.get("deuce"):
            w.points_won_under_pressure += 1
        self._update_momentum(rally)
        self.score_timeline.append(
            {
                "rally_no": rally.rally_no,
                "game_no": rally.game_no,
                "score": dict(rally.score_after),
                "winner": rally.winner,
                "frame": rally.end,
                "rally_id": rally.rally_id,
            }
        )

    def _update_momentum(self, rally: RallyRecord) -> None:
        sign = 1.0 if rally.winner == "P1" else -1.0
        alpha = 0.3
        prev = self._ewma
        self._ewma = alpha * sign + (1 - alpha) * self._ewma
        leader, run = self._run
        self._run = (rally.winner, run + 1) if leader == rally.winner else (rally.winner, 1)
        self.momentum.append(
            {
                "rally_no": rally.rally_no,
                "value": round(self._ewma, 3),
                "leader": "P1" if self._ewma > 0 else "P2",
                "run": {"player": self._run[0], "length": self._run[1]},
                "rally_id": rally.rally_id,
            }
        )
        if prev * self._ewma < 0 and abs(prev) > 0.25:
            self.momentum_shifts.append(
                {
                    "rally_no": rally.rally_no,
                    "to": rally.winner,
                    "rally_id": rally.rally_id,
                    "from_value": round(prev, 3),
                }
            )

    # ------------------------------------------------------------------ highlights
    def score_rally(self, r: RallyRecord) -> Highlight:
        ont = get_ontology()
        reasons: dict[str, float] = {}
        cats: list[str] = []
        longest = max((x.n_shots for x in self.rallies), default=r.n_shots)
        reasons["length"] = min(3.0, r.n_shots / 6.0)
        if r.n_shots >= max(12, longest) and r.n_shots == longest:
            cats.append("longest_rally")
        stroke_set = {s.get("stroke") for s in r.shots}
        reasons["variety"] = min(1.5, 0.3 * len(stroke_set))
        last = r.shots[-1] if r.shots else {}
        if last.get("stroke") == "smash" and last.get("player_id") == r.winner:
            reasons["smash_winner"] = 1.5
            cats.append("smash_winner")
        if any(s.get("subtype") == "jump_smash" for s in r.shots):
            reasons["jump_smash"] = 1.2
            cats.append("jump_smash")
        defensive = sum(
            1
            for s in r.shots
            if s.get("player_id") == r.winner and ont.stroke(s.get("stroke", "unknown")).family in ("lift", "defence")
        )
        if r.winner and defensive >= 4:
            reasons["defence"] = min(1.5, 0.3 * defensive)
            cats.append("best_defence")
        net = sum(1 for s in r.shots if ont.stroke(s.get("stroke", "unknown")).family == "net")
        if net >= 4:
            reasons["net_play"] = min(1.2, 0.25 * net)
            cats.append("net_battle")
        fb = r.flags_before
        if fb.get("match_point"):
            reasons["pressure"] = 2.0
            cats.append("match_point")
        elif fb.get("game_point"):
            reasons["pressure"] = 1.4
            cats.append("game_point")
        if fb.get("deuce"):
            reasons["deuce"] = 1.0
            cats.append("deuce")
            if fb.get("game_point"):
                cats.append("clutch")
        if any(m["rally_id"] == r.rally_id for m in self.momentum_shifts):
            reasons["momentum"] = 1.0
            cats.append("momentum_shift")
        if self._is_comeback_point(r):
            reasons["comeback"] = 1.5
            cats.append("comeback")
        score = min(10.0, sum(reasons.values()))
        return Highlight(r.rally_id, r.rally_no, r.start, r.end, score, cats, reasons, r.winner)

    def _is_comeback_point(self, r: RallyRecord) -> bool:
        """The winner levels or takes the lead in a game after trailing by ≥ 5."""
        if r.winner is None:
            return False
        game = [x for x in self.score_timeline if x["game_no"] == r.game_no and x["rally_no"] <= r.rally_no]
        if not game:
            return False
        opp = "P2" if r.winner == "P1" else "P1"
        max_deficit = max((x["score"][opp] - x["score"][r.winner] for x in game), default=0)
        now = r.score_after
        return max_deficit >= 5 and now[r.winner] >= now[opp] and now[r.winner] - 1 <= now[opp]

    def highlights(self, k: int = 10, player: str | None = None, diversity: float = 0.35) -> list[Highlight]:
        """Top-k rallies by score with Maximal-Marginal-Relevance diversity over categories."""
        pool = [self.score_rally(r) for r in self.rallies if player is None or r.winner == player]
        pool = [h for h in pool if h.score > 0]
        chosen: list[Highlight] = []
        while pool and len(chosen) < k:

            def mmr(h: Highlight) -> float:
                if not chosen:
                    return h.score
                overlap = max(_jaccard(set(h.categories), set(c.categories)) for c in chosen)
                return (1 - diversity) * h.score - diversity * 10 * overlap

            best = max(pool, key=mmr)
            chosen.append(best)
            pool.remove(best)
        return chosen

    # ------------------------------------------------------------------ public
    def to_public(self) -> dict[str, Any]:
        return {
            "rallies": len(self.rallies),
            "players": {p: s.to_public() for p, s in sorted(self.players.items())},
            "momentum": self.momentum[-60:],
            "momentum_shifts": self.momentum_shifts,
            "score_timeline": self.score_timeline,
            "avg_rally_shots": round(sum(r.n_shots for r in self.rallies) / len(self.rallies), 2)
            if self.rallies
            else None,
            "longest_rally_shots": max((r.n_shots for r in self.rallies), default=0),
        }


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def ewma_to_bar(v: float) -> float:
    """Map momentum EWMA (−1..1) to a 0..100 bar for P1 (UI helper)."""
    return round(50 + 50 * math.tanh(1.5 * v), 1)
