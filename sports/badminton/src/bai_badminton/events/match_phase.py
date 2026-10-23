"""Match phase: which segmented rallies are *official* play.

A video rarely starts at the first official serve. Walk-ons, warm-up hitting, practice exchanges
and broadcast replays all produce badminton-like shuttle motion that the rally FSM segments as
rallies; only official rallies may reach the BWF state machine (validation report DEF-01: five
warm-up "rallies" were scored before the match began).

Each finished rally is decided from evidence, in order of authority:

1. **human** — a match-start marker or a per-rally official / not-official mark from the review UI;
2. **scoreboard** — a stable broadcast score reading that did not change across the rally means it
   was not scored (warm-up, let, or a replay of a rally already counted); a change means it was;
3. **serve formation** (BWF Laws 9.1) — an official rally starts with server and receiver standing
   still in *diagonally opposite* service courts: each in their own right court when the server's
   score is even, both in their left courts when odd.  Warm-up exchanges start anywhere;
4. **tempo** — before the match, warm-up exchanges restart within seconds; the first official serve
   follows a pause.

Once the match is in progress, rallies are official unless there is negative evidence (scoreboard
unchanged, or a rally that starts right after a camera cut without a serve formation — a replay or
the tail of a rally already ended by the cut).  Missing evidence never starts the match on its own:
without calibrated player positions and stationarity evidence the phase stays undecided and
those rallies are not scored. Explicit human decisions and stable scoreboard changes can
establish official play independently of court calibration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

from bai_badminton.court import HALF_LEN, SHORT_SERVICE, WIDTH_SINGLES


class Phase(StrEnum):
    UNKNOWN = "unknown"  # nothing decided yet
    WARMUP = "warmup"  # badminton-like activity, not official play
    MATCH_PLAY = "match_play"
    COMPLETED = "completed"  # match won; later hitting is not scored


@dataclass(frozen=True)
class PhaseParams:
    court_tol_m: float = 0.4  # feet-position tolerance around the service-court lines
    still_window_s: float = 1.0  # players must be set before the serve ...
    still_max_m: float = 0.75  # ... moving less than this over the window
    min_entry_gap_s: float = 4.0  # the first official serve follows at least this pause
    post_cut_s: float = 3.0  # "right after a camera cut / replay"


@dataclass(frozen=True)
class RallyEvidence:
    calibrated: bool = True
    formation: bool | None = None  # diagonal service courts at the serve (None = players not seen)
    still: bool | None = None  # both players stationary before the serve
    gap_s: float | None = None  # since the previous rally ended (None = first rally)
    after_cut: bool = False  # starts within post_cut_s of a camera cut / replay
    scoreboard: str | None = None  # "changed" | "unchanged" | None (no stable readings)

    def to_public(self) -> dict[str, Any]:
        d = asdict(self)
        if d["gap_s"] is not None:
            d["gap_s"] = round(d["gap_s"], 2)
        return d


@dataclass(frozen=True)
class PhaseDecision:
    official: bool
    phase: Phase  # phase after this rally
    reason: str
    basis: str  # human | scoreboard | formation | phase | rules | assumed | insufficient


def service_courts(xy: tuple[float, float], tol: float) -> set[str]:
    """Service courts ("right" / "left", from the player's own view) that a feet position is in."""
    x, y = xy
    if not (SHORT_SERVICE - tol <= abs(y) <= HALF_LEN + tol and abs(x) <= WIDTH_SINGLES / 2 + tol):
        return set()
    lateral = x if y < 0 else -x  # the near player faces +y, the far player faces -y
    out = set()
    if lateral > -tol:
        out.add("right")
    if lateral < tol:
        out.add("left")
    return out


def serve_formation(a: tuple[float, float] | None, b: tuple[float, float] | None, tol: float = 0.4) -> bool | None:
    """Are the two players in diagonally opposite service courts? ``None`` if either is unseen."""
    if a is None or b is None:
        return None
    if (a[1] < 0) == (b[1] < 0):
        return False  # same half: not a serve set-up
    return bool(service_courts(a, tol) & service_courts(b, tol))


@dataclass
class MatchPhaseTracker:
    params: PhaseParams = PhaseParams()
    phase: Phase = Phase.UNKNOWN
    match_start_frame: int | None = None  # human marker: rallies starting at/after it are official

    def decide(
        self, start: int, ev: RallyEvidence, *, match_finished: bool = False, override: bool | None = None
    ) -> PhaseDecision:
        if override is not None:
            return self._to(override, "marked by a reviewer", "human")
        if self.match_start_frame is not None:
            ok = start >= self.match_start_frame
            return self._to(ok, "after the match-start marker" if ok else "before the match-start marker", "human")
        if match_finished:
            self.phase = Phase.COMPLETED
            return PhaseDecision(False, self.phase, "after the end of the match", "rules")
        if ev.scoreboard == "unchanged":
            return PhaseDecision(False, self.phase, "the scoreboard did not change", "scoreboard")
        if ev.scoreboard == "changed":
            return self._to(True, "the scoreboard changed", "scoreboard")
        if self.phase is Phase.MATCH_PLAY:
            if ev.after_cut and ev.formation is False:
                return PhaseDecision(False, self.phase, "starts right after a camera cut without a serve", "formation")
            return PhaseDecision(True, self.phase, "match in progress", "phase")
        if not ev.calibrated:
            return PhaseDecision(False, self.phase, "no court calibration: phase cannot be judged", "insufficient")
        if ev.formation is None:
            return PhaseDecision(False, self.phase, "players not visible at the serve", "insufficient")
        if ev.still is None:
            return PhaseDecision(False, self.phase, "players not observed stationary before the serve", "insufficient")
        failed = []
        if not ev.formation:
            failed.append("players not in diagonal service courts")
        if ev.still is False:
            failed.append("players moving before the serve")
        if ev.gap_s is not None and ev.gap_s < self.params.min_entry_gap_s:
            failed.append(f"restarted {ev.gap_s:.1f}s after the previous exchange")
        if failed:
            self.phase = Phase.WARMUP
            return PhaseDecision(False, self.phase, "; ".join(failed), "formation")
        return self._to(True, "serve formation: players set in diagonal service courts", "formation")

    def _to(self, official: bool, reason: str, basis: str) -> PhaseDecision:
        if official:
            self.phase = Phase.MATCH_PLAY
        elif self.phase is Phase.UNKNOWN:
            self.phase = Phase.WARMUP
        return PhaseDecision(official, self.phase, reason, basis)
