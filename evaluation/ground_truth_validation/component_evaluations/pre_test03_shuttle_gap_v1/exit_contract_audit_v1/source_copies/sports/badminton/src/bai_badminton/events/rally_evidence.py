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

from bai_badminton.events.contact_evidence import ContactEvidence, Reliability
from bai_badminton.events.exchange_evidence import simultaneous_opponents
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


@dataclass(frozen=True, slots=True)
class RallyContactAdmission:
    """Temporal-policy decision; accepted does not establish physical impact."""

    frame: int
    accepted: bool
    reason: str
    prior_state: str
    impact: str
    trajectory: str


@dataclass
class EvidenceRallyFSM(RallyFSM):
    use_reconstruction: bool = True
    motion_guard: bool = False
    use_exit_recovery: bool = False
    use_short_exchange_evidence: bool = False
    use_terminal_contact_evidence: bool = False
    _motion: deque[bool | None] = field(default_factory=deque)
    _stationary_conflict: bool = False
    last_evidence: RallyObservation | None = None
    last_contact_admission: RallyContactAdmission | None = None
    last_exchange_admission: dict | None = None
    _contact_witnesses: list[ContactEvidence] = field(default_factory=list)
    _first_observed_motion_span: tuple[int, int] | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if any(
            type(flag) is not bool
            for flag in (
                self.use_reconstruction,
                self.motion_guard,
                self.use_exit_recovery,
                self.use_short_exchange_evidence,
                self.use_terminal_contact_evidence,
            )
        ):
            raise ValueError("evidence switches must be booleans")
        self._motion = deque(maxlen=self.params.stationary_window)

    def on_contact(self, frame: int) -> RallyUpdate:
        result = super().on_contact(frame)
        self._motion.clear()
        self._stationary_conflict = False
        return result

    def on_contact_evidence(self, frame: int, evidence: ContactEvidence | None) -> RallyUpdate:
        """Admit provisional starts separately from terminal contradiction.

        Preserve every candidate upstream. Unknown/weak contacts may propose an
        idle exchange, still subject to observed-motion/maturity checks, but
        cannot erase observed rest, move its last-contact anchor or reopen it.
        This policy uses existing typed reliability, never a new score cutoff.
        Legacy callers explicitly retain ``on_contact`` compatibility.
        """
        if evidence is not None and evidence.inputs.frame != frame:
            raise ValueError("contact evidence frame differs from canonical contact frame")
        impact = evidence.impact.reliability if evidence is not None else None
        trajectory = evidence.trajectory.reliability if evidence is not None else None
        invalid = evidence is not None and (
            evidence.inputs.context_valid is False
            or evidence.inputs.observation_status in {"invalid", "rejected"}
            or impact is Reliability.REJECTED
            or trajectory is Reliability.REJECTED
        )
        if invalid:
            accepted, reason = False, "contact_context_or_physical_evidence_rejected"
        elif not self.use_terminal_contact_evidence:
            accepted, reason = True, "legacy_candidate_contact_policy"
        elif self.state is RallyState.IDLE:
            accepted, reason = True, "provisional_contact_start"
        elif self.state is RallyState.IN_PLAY:
            accepted, reason = True, "in_play_contact_candidate"
        elif (self.state is RallyState.ENDING and self.end_reason != "stationary") or (
            self.state is RallyState.CLOSED and self.closed is not None and self.closed.reason != "stationary"
        ):
            # Missing evidence does not establish observed rest. Preserve weak
            # launch/trajectory callbacks across ordinary perception gaps.
            accepted, reason = True, "gap_contact_candidate_without_rest_contradiction"
        elif evidence is None:
            accepted, reason = False, "contact_evidence_unavailable_for_continuation"
        elif impact is Reliability.CONFIRMED:
            accepted, reason = True, "externally_reviewed_contact"
        elif (
            trajectory is Reliability.PROBABLE
            and evidence.inputs.context_valid is True
            and evidence.inputs.observation_status == "fresh_observed"
        ):
            accepted, reason = True, "observed_trajectory_support_without_impact_confirmation"
        else:
            accepted, reason = False, "terminal_contact_trajectory_unsubstantiated"
        self.last_contact_admission = RallyContactAdmission(
            frame,
            accepted,
            reason,
            self.state.value,
            impact.value if impact is not None else "unknown",
            trajectory.value if trajectory is not None else "unknown",
        )
        result = self.on_contact(frame) if accepted else RallyUpdate()
        if (
            evidence is not None
            and self.start is not None
            and self.start <= frame < self.start + self.params.min_frames
            and evidence.inputs.context_valid is True
            and evidence.inputs.observation_status == "fresh_observed"
            and evidence.inputs.attribution_target is not None
            and evidence.impact.reliability is not Reliability.REJECTED
            and evidence.trajectory.reliability is not Reliability.REJECTED
            and not any(w.inputs.frame == frame for w in self._contact_witnesses)
        ):
            self._contact_witnesses.append(evidence)
        return result

    def _open(self, start: int, update: RallyUpdate) -> None:
        super()._open(start, update)
        self._contact_witnesses.clear()
        self._first_observed_motion_span = None

    def _short_exchange_witnesses(self, segment) -> tuple[int, int] | None:
        if not self.use_short_exchange_evidence:
            return None
        span = self._first_observed_motion_span
        if span is None or not segment.start <= span[0] <= span[1] <= segment.end:
            return None
        witnesses = []
        for witness in self._contact_witnesses:
            motion = witness.inputs.motion
            if not segment.start <= witness.inputs.frame <= segment.end or motion is None:
                continue
            if (
                motion.spatial_sigma_px is None
                or len(motion.before_frames) < 2
                or len(motion.after_frames) < 2
                or not ((motion.incoming_direction_support or 0) > 0 or (motion.outgoing_direction_support or 0) > 0)
            ):
                continue
            for previous in witnesses:
                old_motion = previous.inputs.motion
                assert old_motion is not None
                if (
                    simultaneous_opponents(
                        previous.inputs.participant_context,
                        previous.inputs.attribution_target,
                        witness.inputs.participant_context,
                        witness.inputs.attribution_target,
                    )
                    is not None
                    and not set(old_motion.before_frames + old_motion.after_frames).intersection(
                        motion.before_frames + motion.after_frames
                    )
                    and any(
                        assessment.reliability in {Reliability.PROBABLE, Reliability.CONFIRMED}
                        for value in (previous, witness)
                        for assessment in (value.trajectory, value.impact)
                    )
                ):
                    return previous.inputs.frame, witness.inputs.frame
            witnesses.append(witness)
        return None

    def _finalize(self, update: RallyUpdate) -> None:
        segment = self.closed
        pair = self._short_exchange_witnesses(segment) if segment is not None else None
        super()._finalize(update)
        if segment is not None:
            if update.cancelled_start == segment.start and pair is not None:
                update.cancelled_start = None
                update.finalized = segment
            self.last_exchange_admission = {
                "start": segment.start,
                "end": segment.end,
                "accepted": update.finalized is not None,
                "reason": "independent_contact_and_observed_motion_witnesses"
                if pair is not None and segment.length < self.params.min_frames
                else "duration_policy",
                "witness_frames": list(pair) if pair is not None else [],
                "participant_proof": next(
                    (
                        simultaneous_opponents(
                            a.inputs.participant_context,
                            a.inputs.attribution_target,
                            b.inputs.participant_context,
                            b.inputs.attribution_target,
                        )
                        for a in self._contact_witnesses
                        for b in self._contact_witnesses
                        if pair is not None and (a.inputs.frame, b.inputs.frame) == pair
                    ),
                    None,
                ),
                "identity_semantics": "source-observed opposite episodes; no named/team identity asserted",
            }
        self._contact_witnesses.clear()
        self._first_observed_motion_span = None

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
        if (
            self._first_observed_motion_span is None
            and self.start is not None
            and self._run_start is not None
            and self._run_visible >= self.params.start_visible
            and observation.frame - max(self.start, self._run_start) + 1 >= self.params.start_visible
        ):
            self._first_observed_motion_span = (max(self.start, self._run_start), observation.frame)
        if continuing:
            self._invisible = 0
        return result

    def _stationary(self) -> bool:
        return not self._stationary_conflict and super()._stationary()
