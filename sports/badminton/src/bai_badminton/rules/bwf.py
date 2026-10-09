"""BWF Laws of Badminton — singles scoring as a deterministic state machine.

The match state is a pure function of ``(MatchConfig, sequence of rally winners)``.  That makes
corrections trivial and auditable: when a rally winner is corrected, the state is re-folded from
the rally sequence and every downstream score/game/match event is regenerated.

Implemented laws (BWF Laws, section 7–9 & 16, singles):

* Rally-point scoring; a match is the best of three games (configurable).
* A game is won by the first side to 21 points; at 20–20 the side gaining a two-point lead wins;
  at 29–29 the side scoring the 30th point wins.
* The side winning a rally serves the next rally. The winner of a game serves first in the next.
* Singles service courts: the server serves from the right court when their score is even and
  from the left court when it is odd.
* Intervals: 60 s when the leading score first reaches 11 in a game; 120 s between games.
* Change of ends: after each game, and in the deciding game when the leading score reaches 11.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PlayerId = Literal["P1", "P2"]
PLAYERS: tuple[PlayerId, PlayerId] = ("P1", "P2")


def other(p: PlayerId) -> PlayerId:
    return "P2" if p == "P1" else "P1"


class End(StrEnum):
    NEAR = "near"  # bottom of the broadcast frame
    FAR = "far"


class ServiceCourt(StrEnum):
    RIGHT = "right"
    LEFT = "left"


class MatchConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    games_to_win: int = 2  # best of 3
    points_to_win: int = 21
    point_cap: int = 30
    interval_at: int = 11
    first_server: PlayerId = "P1"
    initial_ends: dict[str, End] = Field(default_factory=lambda: {"P1": End.NEAR, "P2": End.FAR})

    @property
    def max_games(self) -> int:
        return 2 * self.games_to_win - 1


class Transition(StrEnum):
    POINT = "point"
    INTERVAL = "interval"
    GAME_END = "game_end"
    SIDE_SWITCH = "side_switch"
    MATCH_END = "match_end"


class MatchState(BaseModel):
    """Score and service state *before* the next rally is played."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    game_no: int = 1  # 1-based
    score: dict[str, int] = Field(default_factory=lambda: {"P1": 0, "P2": 0})
    games_won: dict[str, int] = Field(default_factory=lambda: {"P1": 0, "P2": 0})
    completed_games: tuple[tuple[int, int], ...] = ()  # (P1, P2) per finished game
    server: PlayerId = "P1"
    ends: dict[str, End] = Field(default_factory=lambda: {"P1": End.NEAR, "P2": End.FAR})
    rally_no: int = 0  # rallies completed in the match
    interval_taken: bool = False  # mid-game interval already taken in the current game
    deciding_game_switched: bool = False
    winner: PlayerId | None = None

    # ------------------------------------------------------------------ derived
    @property
    def receiver(self) -> PlayerId:
        return other(self.server)

    @property
    def service_court(self) -> ServiceCourt:
        return ServiceCourt.RIGHT if self.score[self.server] % 2 == 0 else ServiceCourt.LEFT

    @property
    def finished(self) -> bool:
        return self.winner is not None

    def is_deciding_game(self, cfg: MatchConfig) -> bool:
        return self.games_won["P1"] == self.games_won["P2"] == cfg.games_to_win - 1

    def game_point_for(self, cfg: MatchConfig) -> PlayerId | None:
        """Player who would win the current game by winning the next rally (if any)."""
        if self.finished:
            return None
        for p in PLAYERS:
            if _game_won_after(self.score[p] + 1, self.score[other(p)], cfg):
                return p
        return None

    def match_point_for(self, cfg: MatchConfig) -> PlayerId | None:
        p = self.game_point_for(cfg)
        if p is not None and self.games_won[p] == cfg.games_to_win - 1:
            return p
        return None

    def is_deuce(self, cfg: MatchConfig) -> bool:
        a, b = self.score["P1"], self.score["P2"]
        return a == b and a >= cfg.points_to_win - 1

    def flags(self, cfg: MatchConfig) -> dict[str, object]:
        return {
            "game_point": self.game_point_for(cfg),
            "match_point": self.match_point_for(cfg),
            "deuce": self.is_deuce(cfg),
            "deciding_game": self.is_deciding_game(cfg),
        }

    def to_public(self, cfg: MatchConfig) -> dict[str, object]:
        """JSON-friendly view for the UI, the event payloads and agents."""
        return {
            "game_no": self.game_no,
            "score": dict(self.score),
            "games_won": dict(self.games_won),
            "completed_games": [list(g) for g in self.completed_games],
            "server": self.server,
            "receiver": self.receiver,
            "service_court": self.service_court.value,
            "ends": {k: v.value for k, v in self.ends.items()},
            "rally_no": self.rally_no,
            "winner": self.winner,
            **self.flags(cfg),
        }


def _game_won_after(a: int, b: int, cfg: MatchConfig) -> bool:
    """True if a side with ``a`` points (vs ``b``) has won the game."""
    if a >= cfg.point_cap:
        return True
    return a >= cfg.points_to_win and a - b >= 2


def initial_state(cfg: MatchConfig) -> MatchState:
    return MatchState(server=cfg.first_server, ends=dict(cfg.initial_ends))


class RallyResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    before: MatchState
    after: MatchState
    winner: PlayerId
    transitions: tuple[Transition, ...]
    game_point_saved: bool = False  # the loser of this rally had game point and lost it? (see below)


class MatchFinishedError(RuntimeError):
    pass


def apply_rally(state: MatchState, winner: PlayerId, cfg: MatchConfig) -> RallyResult:
    """Apply one rally won by ``winner``; returns the new state and the transitions triggered."""
    if state.finished:
        raise MatchFinishedError(f"match already won by {state.winner}")
    transitions: list[Transition] = [Transition.POINT]
    score = dict(state.score)
    score[winner] += 1
    loser = other(winner)
    had_gp = state.game_point_for(cfg)

    games_won = dict(state.games_won)
    completed = state.completed_games
    ends = dict(state.ends)
    game_no = state.game_no
    interval_taken = state.interval_taken
    deciding_switched = state.deciding_game_switched
    match_winner: PlayerId | None = None
    server: PlayerId = winner

    if _game_won_after(score[winner], score[loser], cfg):
        transitions.append(Transition.GAME_END)
        games_won[winner] += 1
        completed = (*completed, (score["P1"], score["P2"]))
        if games_won[winner] == cfg.games_to_win:
            transitions.append(Transition.MATCH_END)
            match_winner = winner
        else:
            # change ends after each game; the game winner serves first in the next game
            ends = {p: (End.FAR if e == End.NEAR else End.NEAR) for p, e in ends.items()}
            transitions.append(Transition.SIDE_SWITCH)
            transitions.append(Transition.INTERVAL)
            game_no += 1
            score = {"P1": 0, "P2": 0}
            interval_taken = False
            deciding_switched = False
    else:
        lead = max(score.values())
        if not interval_taken and lead == cfg.interval_at:
            transitions.append(Transition.INTERVAL)
            interval_taken = True
            deciding = games_won["P1"] == games_won["P2"] == cfg.games_to_win - 1
            if deciding and not deciding_switched:
                ends = {p: (End.FAR if e == End.NEAR else End.NEAR) for p, e in ends.items()}
                transitions.append(Transition.SIDE_SWITCH)
                deciding_switched = True

    after = MatchState(
        game_no=game_no,
        score=score,
        games_won=games_won,
        completed_games=completed,
        server=server,
        ends=ends,
        rally_no=state.rally_no + 1,
        interval_taken=interval_taken,
        deciding_game_switched=deciding_switched,
        winner=match_winner,
    )
    return RallyResult(
        before=state,
        after=after,
        winner=winner,
        transitions=tuple(transitions),
        game_point_saved=had_gp == loser,
    )


def fold(winners: list[PlayerId], cfg: MatchConfig) -> list[RallyResult]:
    """Replay a full rally sequence. Rallies after the match end raise ``MatchFinishedError``."""
    state = initial_state(cfg)
    out: list[RallyResult] = []
    for w in winners:
        r = apply_rally(state, w, cfg)
        out.append(r)
        state = r.after
    return out


def infer_server_and_config(first_server: PlayerId | None, cfg: MatchConfig) -> MatchConfig:
    """Return a config with the detected first server (from serve detection) when known."""
    if first_server is None or first_server == cfg.first_server:
        return cfg
    return cfg.model_copy(update={"first_server": first_server})
