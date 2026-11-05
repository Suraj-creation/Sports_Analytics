"""Explicit observation quality for optional badminton rally continuation.

Reconstruction and body motion are supporting evidence, never observed contacts,
new starts, physical landings or winner decisions. The legacy provider remains
available; this provider is opt-in and requires independent validation.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import StrEnum
from math import isfinite, nan
from numbers import Real

from bai_badminton.events.rally_fsm import RallyFSM, RallyState, RallyUpdate


class ObservationKind(StrEnum):
    OBSERVED = "observed"
    RECONSTRUCTED = "reconstructed"
    MISSING = "missing"
    INVALID = "invalid"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True, slots=True)
class RallyObservation:
    frame: int
    kind: ObservationKind
    speed: float | None = None  # adjacent independently observed pixels/frame only
    shuttle_support: float | None = None  # uncalibrated model support, not probability
    player_motion: bool | None = None  # frame-aligned independently observed support
    context_valid: bool = True
    replay: bool = False
    continuation_supported: bool = False  # independently moving observed brackets; not generic interpolation
    exit_return_supported: bool = False  # observed top exit/re-entry, without fabricated positions

    def __post_init__(self) -> None:
        if type(self.frame) is not int or self.frame < 0 or not isinstance(self.kind, ObservationKind):
            raise ValueError("invalid canonical rally observation")
        if self.speed is not None and (
            isinstance(self.speed, bool)
            or not isinstance(self.speed, Real)
            or not isfinite(self.speed)
            or self.speed < 0
        ):
            raise ValueError("observed speed must be finite, nonnegative or unavailable")
        if self.kind is not ObservationKind.OBSERVED and self.speed is not None:
            raise ValueError("estimated/missing samples cannot claim observed speed")
        if self.shuttle_support is not None and (
            isinstance(self.shuttle_support, bool)
            or not isinstance(self.shuttle_support, Real)
            or not isfinite(self.shuttle_support)
        ):
            raise ValueError("model support must be finite or unavailable")
        if type(self.context_valid) is not bool or type(self.replay) is not bool:
            raise ValueError("context and replay flags must be booleans")
        if type(self.continuation_supported) is not bool or (
            self.continuation_supported and self.kind is not ObservationKind.RECONSTRUCTED
        ):
            raise ValueError("only a reconstructed sample can carry explicit continuation support")
        if self.player_motion is not None and type(self.player_motion) is not bool:
            raise ValueError("motion support must be true, false or unavailable")
        if type(self.exit_return_supported) is not bool or (
            self.exit_return_supported
            and self.kind not in {ObservationKind.MISSING, ObservationKind.RECONSTRUCTED, ObservationKind.AMBIGUOUS}
        ):
            raise ValueError("image-exit support belongs only to unobserved or estimated samples")


@dataclass
class EvidenceRallyFSM(RallyFSM):
    use_reconstruction: bool = True
    motion_guard: bool = False
    use_exit_recovery: bool = False
    _motion: deque[bool | None] = field(default_factory=deque)
    _stationary_conflict: bool = False
    last_evidence: RallyObservation | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if any(type(flag) is not bool for flag in (self.use_reconstruction, self.motion_guard, self.use_exit_recovery)):
            raise ValueError("evidence switches must be booleans")
        self._motion = deque(maxlen=self.params.stationary_window)

    def on_contact(self, frame: int) -> RallyUpdate:
        result = super().on_contact(frame)
        self._motion.clear()
        self._stationary_conflict = False
        return result

    def on_discontinuity(self, frame: int) -> RallyUpdate:
        result = super().on_discontinuity(frame)
        self._motion.clear()
        self._stationary_conflict = False
        return result

    def step(self, frame: int, visible: bool, speed: float, replay: bool = False) -> RallyUpdate:
        """Legacy adapter; unknown quality cannot acquire richer support."""
        return self.step_evidence(
            RallyObservation(
                frame,
                ObservationKind.OBSERVED if visible else ObservationKind.MISSING,
                speed if visible and isfinite(speed) else None,
                replay=replay,
            )
        )

    def step_evidence(self, observation: RallyObservation) -> RallyUpdate:
        self.last_evidence = observation
        if observation.replay or not observation.context_valid or observation.kind is ObservationKind.INVALID:
            return self.on_discontinuity(observation.frame)
        self._motion.append(observation.player_motion)
        reconstructed = (
            self.use_reconstruction
            and observation.kind is ObservationKind.RECONSTRUCTED
            and observation.continuation_supported
        )
        motion_conflict = self.motion_guard and any(value is True for value in self._motion)
        exit_supported = self.use_exit_recovery and observation.exit_return_supported
        self._stationary_conflict = reconstructed or exit_supported or motion_conflict
        if (
            self.state is RallyState.CLOSED
            and exit_supported
            and self.closed is not None
            and self.closed.reason == "gap"
        ):
            # A retained (unpublished) gap candidate can be disambiguated by
            # actual observed exit/re-entry brackets. No start is invented.
            self._reopen(RallyUpdate())
        if self.state is RallyState.ENDING and (
            reconstructed or exit_supported or (motion_conflict and self.end_reason == "stationary")
        ):
            self.state, self.tentative_end = RallyState.IN_PLAY, None
        continuing = (reconstructed or exit_supported) and self.state is RallyState.IN_PLAY
        if continuing:
            # Estimated continuity prevents accumulating absence as termination
            # evidence. It stays invisible, cannot build a start/resume motion
            # run, and is never passed to the observed-contact detector.
            self._invisible = 0
        result = super().step(
            observation.frame,
            observation.kind is ObservationKind.OBSERVED,
            observation.speed if observation.speed is not None else nan,
        )
        if continuing:
            self._invisible = 0
        return result

    def _stationary(self) -> bool:
        return not self._stationary_conflict and super()._stationary()
