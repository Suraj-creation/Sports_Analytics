"""Badminton rules (BWF Laws)."""

from bai_badminton.rules.bwf import (
    PLAYERS,
    End,
    MatchConfig,
    MatchFinishedError,
    MatchState,
    PlayerId,
    RallyResult,
    ServiceCourt,
    Transition,
    apply_rally,
    fold,
    initial_state,
    other,
)

# These records jointly define score history. Generic payload verification must
# not change them without the engine's winner/official/phase correction fold.
SCORE_REVIEW_EVENT_TYPES = frozenset({"rally_end", "match_phase", *(transition.value for transition in Transition)})

__all__ = [
    "PLAYERS",
    "SCORE_REVIEW_EVENT_TYPES",
    "End",
    "MatchConfig",
    "MatchFinishedError",
    "MatchState",
    "PlayerId",
    "RallyResult",
    "ServiceCourt",
    "Transition",
    "apply_rally",
    "fold",
    "initial_state",
    "other",
]
