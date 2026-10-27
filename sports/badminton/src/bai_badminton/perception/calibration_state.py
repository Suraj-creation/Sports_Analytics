"""Conservative court-geometry lifecycle independent of match classification."""

from dataclasses import dataclass
from enum import StrEnum


class CalibrationState(StrEnum):
    VALID = "VALID"
    DEGRADED = "DEGRADED"
    LOST = "LOST"
    REACQUIRING = "REACQUIRING"


@dataclass
class CalibrationLifecycle:
    recovery_frames: int = 3
    state: CalibrationState = CalibrationState.LOST
    _run: int = 0

    def __post_init__(self) -> None:
        if self.recovery_frames < 1:
            raise ValueError("recovery_frames must be positive")

    def update(self, *, verified: bool, held: bool = False, cut: bool = False) -> CalibrationState:
        if cut:
            self.state, self._run = CalibrationState.LOST, 0
        if not verified:
            self._run = 0
            self.state = CalibrationState.DEGRADED if held else CalibrationState.LOST
        elif self.state == CalibrationState.VALID:
            self._run = self.recovery_frames
        else:
            self._run += 1
            self.state = CalibrationState.VALID if self._run >= self.recovery_frames else CalibrationState.REACQUIRING
        return self.state
