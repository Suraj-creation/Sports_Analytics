"""Typed physical-contact evidence, independent of event-ledger finality.

The deterministic assessment is an evidence policy, not a calibrated contact
classifier. A trajectory turn, a racket overlap, a named actor and a finalized
ledger entry are different claims. Only explicit source-bound external review
can produce ``confirmed`` physical impact; this module never creates reviews.
``rejected`` rejects the candidate evidence, not every possible unseen hit.

Inputs use absolute canonical analysis frames and analysis-image pixels. The
assessment is stateless, supports arbitrary participant counts and preserves
unknown legacy provenance. It changes no candidate score, NMS or identity.
"""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from itertools import pairwise
from typing import Any, Literal

ObservationStatus = Literal[
    "fresh_observed",
    "missing",
    "reconstructed",
    "ambiguous",
    "invalid",
    "rejected",
    "stale",
    "carried",
    "occluded",
    "out_of_view",
]
AssociationStatus = Literal["tracked", "static_candidate", "reacquisition", "ambiguous", "rejected", "unknown"]


class Reliability(StrEnum):
    CONFIRMED = "confirmed"
    PROBABLE = "probable"
    AMBIGUOUS = "ambiguous"
    REJECTED = "rejected"
    INSUFFICIENT = "insufficient"


@dataclass(frozen=True)
class ReliabilityAssessment:
    reliability: Reliability
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            not isinstance(self.reliability, Reliability)
            or not isinstance(self.reasons, tuple)
            or not 1 <= len(self.reasons) <= 16
            or any(not isinstance(reason, str) or not 1 <= len(reason) <= 256 for reason in self.reasons)
        ):
            raise ValueError("reliability requires a typed status and bounded immutable reasons")


@dataclass(frozen=True)
class ContactReview:
    """Explicit external assertion; fields identify review, not proof of quality."""

    frame: int
    source_sha256: str
    reviewer: str
    review_id: str
    physical_impact: bool

    def __post_init__(self) -> None:
        if (
            type(self.frame) is not int
            or self.frame < 0
            or re.fullmatch(r"[0-9a-f]{64}", self.source_sha256) is None
            or not self.reviewer.strip()
            or not self.review_id.strip()
            or len(self.reviewer) > 128
            or len(self.review_id) > 256
            or type(self.physical_impact) is not bool
        ):
            raise ValueError("review requires a canonical frame, source digest, reviewer and explicit impact assertion")


@dataclass(frozen=True)
class ContactMotionEvidence:
    """Same-scene observed samples and explicitly declared spatial sensitivity.

    Direction/support values are heuristic sensitivity diagnostics. Missing
    sensitivity stays unknown; raw model support is not an observation-error
    covariance. A zero incoming speed is permitted for a stationary launch.
    """

    before_frames: tuple[int, ...]
    after_frames: tuple[int, ...]
    speed_before: float
    speed_after: float
    spatial_sigma_px: float | None = None
    incoming_direction_support: float | None = None
    outgoing_direction_support: float | None = None
    redirect_support: float | None = None
    speed_gain_support: float | None = None
    incoming_slope_sigma_px_per_frame: float | None = None
    outgoing_slope_sigma_px_per_frame: float | None = None
    incoming_fit_residual_rms_px: float | None = None
    outgoing_fit_residual_rms_px: float | None = None

    def __post_init__(self) -> None:
        for frames in (self.before_frames, self.after_frames):
            if not isinstance(frames, tuple) or len(frames) > 32 or any(type(f) is not int or f < 0 for f in frames):
                raise ValueError("motion sample frames must be bounded immutable canonical indices")
            if any(b <= a for a, b in pairwise(frames)):
                raise ValueError("motion sample frames must be strictly chronological")
        if any(not math.isfinite(v) or v < 0 for v in (self.speed_before, self.speed_after)):
            raise ValueError("motion speeds must be nonnegative and finite")
        if self.spatial_sigma_px is not None and (
            not math.isfinite(self.spatial_sigma_px) or self.spatial_sigma_px <= 0
        ):
            raise ValueError("spatial sensitivity must be positive and finite")
        for value in (
            self.incoming_direction_support,
            self.outgoing_direction_support,
            self.redirect_support,
            self.speed_gain_support,
        ):
            if value is not None and (not math.isfinite(value) or not 0 <= value <= 1):
                raise ValueError("motion support must be finite and within [0, 1]")
        for value in (
            self.incoming_slope_sigma_px_per_frame,
            self.outgoing_slope_sigma_px_per_frame,
            self.incoming_fit_residual_rms_px,
            self.outgoing_fit_residual_rms_px,
        ):
            if value is not None and (not math.isfinite(value) or value < 0):
                raise ValueError("motion fit diagnostics must be nonnegative and finite")


@dataclass(frozen=True)
class ContactEvidenceInputs:
    frame: int
    available_through: int
    context_start: int
    context_stop: int  # half-open; only this bounded window may support the assessment
    provider: str
    motion: ContactMotionEvidence | None = None
    # None means legacy provenance is unavailable. Coordinate presence alone
    # cannot distinguish fresh inference, tracker carry or rejected association.
    observation_status: ObservationStatus | None = None
    association_status: AssociationStatus | None = None
    context_valid: bool | None = None
    player_observed: bool | None = None
    pose_observed: bool | None = None
    racket_observed: bool | None = None
    proximity_support: float | None = None
    swing_support: float | None = None
    racket_overlap_support: float | None = None
    attribution_target: str | None = None
    attribution_reason: str | None = None
    review: ContactReview | None = None
    player_observation_frames: tuple[int, ...] = ()
    pose_observation_frames: tuple[int, ...] = ()
    racket_observation_frames: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if (
            any(type(v) is not int for v in (self.frame, self.available_through, self.context_start, self.context_stop))
            or not 0 <= self.context_start <= self.frame < self.context_stop
            or self.available_through < self.frame
            or not self.provider.strip()
            or len(self.provider) > 128
        ):
            raise ValueError("contact evidence requires valid canonical context and provider")
        if self.observation_status not in {
            None,
            "fresh_observed",
            "missing",
            "reconstructed",
            "ambiguous",
            "invalid",
            "rejected",
            "stale",
            "carried",
            "occluded",
            "out_of_view",
        }:
            raise ValueError("unknown contact observation status")
        if self.association_status not in {
            None,
            "tracked",
            "static_candidate",
            "reacquisition",
            "ambiguous",
            "rejected",
            "unknown",
        }:
            raise ValueError("unknown contact association status")
        for value in (self.context_valid, self.player_observed, self.pose_observed, self.racket_observed):
            if value is not None and type(value) is not bool:
                raise ValueError("evidence availability must be an explicit boolean or unknown")
        for value in (self.proximity_support, self.swing_support, self.racket_overlap_support):
            if value is not None and (not math.isfinite(value) or not 0 <= value <= 1):
                raise ValueError("contact support must be finite and within [0, 1]")
        if self.motion is not None:
            before, after = self.motion.before_frames, self.motion.after_frames
            samples = before + after
            if (
                any(f < self.context_start or f >= self.context_stop or f > self.available_through for f in samples)
                or any(f > self.frame for f in before)
                or any(f < self.frame for f in after)
            ):
                raise ValueError("motion samples cannot cross context or availability boundaries")
        if self.review is not None and self.review.frame != self.frame:
            raise ValueError("review frame must identify this contact candidate")
        for samples in (self.player_observation_frames, self.pose_observation_frames, self.racket_observation_frames):
            if (
                not isinstance(samples, tuple)
                or len(samples) > 32
                or any(
                    type(f) is not int or not self.context_start <= f < self.context_stop or f > self.available_through
                    for f in samples
                )
                or any(b <= a for a, b in pairwise(samples))
            ):
                raise ValueError("cue observations must be bounded, chronological and available in this context")


@dataclass(frozen=True)
class ContactEvidence:
    inputs: ContactEvidenceInputs
    trajectory: ReliabilityAssessment
    impact: ReliabilityAssessment
    attribution: ReliabilityAssessment
    schema: str = field(default="badminton-contact-evidence:v1", init=False)
    policy: str = field(default="contact_physical_evidence_v2", init=False)
    score_semantics: str = field(default="uncalibrated_heuristic_support", init=False)

    def __post_init__(self) -> None:
        if self.impact.reliability is Reliability.CONFIRMED and (
            self.inputs.review is None or not self.inputs.review.physical_impact
        ):
            raise ValueError("confirmed physical impact requires explicit external review")

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def _assessment(reliability: Reliability, *reasons: str) -> ReliabilityAssessment:
    return ReliabilityAssessment(reliability, tuple(reasons))


def assess_contact_evidence(inputs: ContactEvidenceInputs) -> ContactEvidence:
    """Keep independent trajectory, physical-impact and attribution conclusions.

    A probable automatic impact needs a coherent turn or launch, a fresh person
    and a fresh swing or geometric racket overlap. Static launch context is
    allowed. Missing cues are not negative physical-contact labels. Unknown or
    reacquired association cannot be repaired by a large relative-speed score.
    """
    motion = inputs.motion
    if inputs.context_valid is False:
        trajectory = impact = _assessment(Reliability.REJECTED, "invalid_temporal_context")
    elif inputs.observation_status in {"invalid", "rejected"} or inputs.association_status == "rejected":
        trajectory = impact = _assessment(Reliability.REJECTED, "candidate_observation_rejected")
    elif inputs.observation_status is None:
        trajectory = impact = _assessment(Reliability.INSUFFICIENT, "observation_provenance_unknown")
    elif inputs.observation_status != "fresh_observed":
        status = Reliability.AMBIGUOUS if inputs.observation_status == "ambiguous" else Reliability.INSUFFICIENT
        trajectory = impact = _assessment(status, "fresh_physical_observation_unavailable")
    else:
        fresh_swing = inputs.pose_observed is True and (inputs.swing_support or 0) > 0
        fresh_overlap = inputs.racket_observed is True and (inputs.racket_overlap_support or 0) >= 0.5
        independent_cue = fresh_swing or fresh_overlap
        turn = bool(
            motion is not None
            and motion.spatial_sigma_px is not None
            and len(motion.before_frames) >= 2
            and len(motion.after_frames) >= 2
            and (motion.incoming_direction_support or 0) > 0
            and (motion.outgoing_direction_support or 0) > 0
            and (motion.redirect_support or 0) > 0
        )
        launch = bool(
            motion is not None
            and motion.spatial_sigma_px is not None
            and len(motion.before_frames) >= 2
            and len(motion.after_frames) >= 2
            and (motion.outgoing_direction_support or 0) > 0
            and (motion.speed_gain_support or 0) > 0
            and motion.speed_after > motion.speed_before
        )
        association_known = inputs.association_status == "tracked" or (
            inputs.association_status == "static_candidate" and launch and independent_cue
        )
        if not association_known:
            reason = (
                "static_candidate_without_independent_contact_cue"
                if inputs.association_status == "static_candidate" and not independent_cue
                else "association_unresolved"
            )
            trajectory = impact = _assessment(Reliability.AMBIGUOUS, reason)
        else:
            trajectory = (
                _assessment(Reliability.PROBABLE, "supported_turn" if turn else "supported_launch")
                if turn or launch
                else _assessment(
                    Reliability.INSUFFICIENT,
                    "motion_sensitivity_unavailable"
                    if motion is None or motion.spatial_sigma_px is None
                    else "coherent_motion_change_unavailable",
                )
            )
            if inputs.context_valid is not True:
                impact = _assessment(Reliability.INSUFFICIENT, "temporal_context_provenance_unknown")
            elif inputs.player_observed is not True:
                impact = _assessment(Reliability.INSUFFICIENT, "fresh_player_observation_unavailable")
            elif (inputs.proximity_support or 0) < 0.05:
                impact = _assessment(Reliability.AMBIGUOUS, "insufficient_player_proximity")
            elif not independent_cue:
                impact = _assessment(Reliability.AMBIGUOUS, "no_fresh_swing_or_racket_overlap")
            elif trajectory.reliability is not Reliability.PROBABLE:
                impact = _assessment(Reliability.AMBIGUOUS, "coherent_motion_change_unavailable")
            else:
                impact = _assessment(Reliability.PROBABLE, "coherent_motion_and_fresh_contact_cue")
    if inputs.review is not None:
        impact = _assessment(
            Reliability.CONFIRMED if inputs.review.physical_impact else Reliability.REJECTED,
            "source_bound_external_review",
        )
    if inputs.player_observed is not True:
        attribution = _assessment(Reliability.INSUFFICIENT, "fresh_player_observation_unavailable")
    elif inputs.attribution_target is None:
        attribution = _assessment(Reliability.AMBIGUOUS, inputs.attribution_reason or "hitter_unresolved")
    elif inputs.attribution_reason != "nearest_proximity":
        attribution = _assessment(Reliability.AMBIGUOUS, inputs.attribution_reason or "attribution_method_unknown")
    else:
        attribution = _assessment(Reliability.PROBABLE, "geometric_attribution_not_verified_identity")
    return ContactEvidence(inputs, trajectory, impact, attribution)
