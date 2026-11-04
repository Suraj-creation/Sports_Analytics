"""Sport-owned decision ports and baseline providers; no second match engine.

Factories select behavior independently of artifact names. Temporal observations
use canonical CFR indices; floor coordinates never denote airborne 3D geometry.
"""

from __future__ import annotations

import copy
from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Any, Protocol, runtime_checkable
from uuid import uuid4

import numpy as np

from bai_badminton.analytics.match import MatchAnalytics, RallyRecord
from bai_badminton.events.activity import ActivityEstimate, ActivityInterval, ActivityObservation, ActivityTracker
from bai_badminton.events.contact import ContactCandidate, ContactMotionReliability, detect_contacts
from bai_badminton.events.rally_evidence import EvidenceRallyFSM, RallyObservation
from bai_badminton.events.rally_fsm import RallyFSM, RallyParams, RallySegment, RallyState, RallyUpdate
from bai_badminton.events.rally_motion import (
    ImageExitReturnSupport,
    image_exit_return_curve_support,
    image_exit_return_tracklet_support,
)
from bai_badminton.events.rally_outcome import CourtImageGeometry, analyze_rally_end, outcome_confidence
from bai_badminton.events.stroke import RuleStrokeClassifier, StrokeContext, StrokePrediction
from bai_badminton.identity import IdentityResolver
from bai_badminton.observations import WindowObs
from bai_badminton.participation import ParticipantFrame, ParticipantTracker
from bai_badminton.perception_types import PersonObs
from bai_badminton.rules import MatchConfig, MatchState, RallyResult, apply_rally, initial_state
from bai_badminton.teams import DoublesTeamEstimate, DoublesTeamTracker
from bai_engine.components import ComponentContract, ComponentRegistry
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import Event


@dataclass(frozen=True, slots=True)
class DomainContext:
    fps: float
    frame_width: int
    frame_height: int
    match_config: MatchConfig
    registry: ModelRegistry | None = None


@runtime_checkable
class NamedIdentity(Protocol):
    net_image_y: float | None

    def assign(
        self, persons: list[PersonObs], ends: dict[str, str], frame: int | None = None
    ) -> dict[str, PersonObs]: ...


@runtime_checkable
class ParticipantIdentity(Protocol):
    def update(
        self, frame_idx: int, persons: list[PersonObs], *, coverage_valid: bool, absence_valid: bool
    ) -> ParticipantFrame: ...


@runtime_checkable
class TeamIdentity(Protocol):
    def update(
        self, frame: ParticipantFrame, *, court_valid: bool, active_play_evidence: bool
    ) -> DoublesTeamEstimate: ...


@runtime_checkable
class IdentityInference(Protocol):
    def named_resolver(self) -> NamedIdentity: ...

    def participant_tracker(self, instance_id: str) -> ParticipantIdentity: ...

    def team_tracker(self) -> TeamIdentity: ...


@runtime_checkable
class ContactInference(Protocol):
    def detect(self, window: WindowObs, **kwargs: Any) -> list[ContactCandidate]: ...


@runtime_checkable
class StrokeClassification(Protocol):
    name: str

    def predict(self, context: StrokeContext) -> StrokePrediction: ...


@runtime_checkable
class ActivityInference(Protocol):
    def reset(self) -> None: ...

    def close(self) -> None: ...

    def checkpoint(self) -> object: ...

    def restore(self, checkpoint: object) -> None: ...

    def update(self, observation: ActivityObservation) -> tuple[ActivityEstimate, ActivityInterval | None]: ...

    def flush(self) -> ActivityInterval | None: ...


@runtime_checkable
class RallySegmentation(Protocol):
    def reset(self) -> None: ...

    def close(self) -> None: ...

    def checkpoint(self) -> object: ...

    def restore(self, checkpoint: object) -> None: ...

    state: RallyState
    params: RallyParams
    start: int | None
    tentative_end: int | None
    closed: RallySegment | None

    def on_contact(self, frame: int) -> RallyUpdate: ...

    def step(self, frame: int, visible: bool, speed: float, replay: bool = False) -> RallyUpdate: ...

    def on_discontinuity(self, frame: int) -> RallyUpdate: ...

    def flush(self, frame: int) -> RallyUpdate: ...


@runtime_checkable
class EvidenceRallySegmentation(RallySegmentation, Protocol):
    """Optional v2 observation input; legacy independent providers stay valid."""

    def step_evidence(self, observation: RallyObservation) -> RallyUpdate: ...


@runtime_checkable
class AssociatedExitRallySegmentation(EvidenceRallySegmentation, Protocol):
    """Optional sport-owned policy for a bounded exit association proof."""

    def exit_return_support(
        self,
        window: WindowObs,
        index: int,
        *,
        frame_height: float,
        raw_xy: Callable[[int, tuple[float, float]], tuple[float, float] | None],
    ) -> ImageExitReturnSupport: ...


@dataclass(frozen=True, slots=True)
class OutcomeInput:
    window: WindowObs
    observed: np.ndarray
    terminal_frame: int
    geometry: CourtImageGeometry
    fps: float


@dataclass(frozen=True, slots=True)
class OutcomePrediction:
    outcome: str
    fault: str
    check: str
    confidence: float


@runtime_checkable
class OutcomeInference(Protocol):
    def predict(self, request: OutcomeInput) -> OutcomePrediction: ...


@runtime_checkable
class ScoreRules(Protocol):
    def initial(self, config: MatchConfig) -> MatchState: ...

    def apply(self, before: MatchState, winner: str, config: MatchConfig) -> RallyResult: ...


@runtime_checkable
class Analytics(Protocol):
    def reset(self) -> None: ...

    def close(self) -> None: ...

    def on_stroke(self, event: Event, *, spatial_valid: bool = False) -> None: ...

    def on_stroke_retracted(self, event: Event) -> None: ...

    def on_presence(self, player_id: str, points: Any) -> None: ...

    def on_rally(self, rally: RallyRecord) -> None: ...

    def score_rally(self, rally: RallyRecord) -> Any: ...

    def highlights(self, k: int = 10, **kwargs: Any) -> list[Any]: ...

    def to_public(self) -> dict[str, Any]: ...

    def checkpoint(self) -> object: ...

    def restore(self, checkpoint: object) -> None: ...


DOMAIN_PORTS = {
    "identity": IdentityInference,
    "contact": ContactInference,
    "stroke": StrokeClassification,
    "activity": ActivityInference,
    "rally": RallySegmentation,
    "outcome": OutcomeInference,
    "scoring": ScoreRules,
    "analytics": Analytics,
}
BASELINE_IMPLEMENTATIONS = {
    "identity": "participant-identity-v1",
    "contact": "contact-fusion-v1",
    "stroke": "stroke-rules-v0",
    "activity": "temporal-activity-v3",
    "rally": "rally-fsm-v1",
    "outcome": "observed-terminal-v1",
    "scoring": "bwf-rally-point-v1",
    "analytics": "match-analytics-v1",
}

# These contracts augment the generic construction metadata with domain evidence
# conventions. Unknown-format support means abstention where required, not a
# claim that format-specific rules are executable without a format decision.
CONTRACT_DETAILS = {
    kind: {
        "timeline": "canonical_cfr_frame_index",
        "coordinates": "analysis_image_pixels_and_ground_foot_metres_with_provenance",
        "devices": ["cpu"],
        "required_evidence": {
            "identity": ["provisional_track_episodes"],
            "contact": ["observed_shuttle_motion_or_equipment_support"],
            "stroke": ["contact_context_and_declared_classifier_evidence"],
            "activity": ["view_eligible_observations"],
            "rally": ["ordered_visibility_motion_and_contacts"],
            "outcome": ["guarded_terminal_observations_and_valid_court"],
            "scoring": ["accepted_winner_and_known_format"],
            "analytics": ["accepted_events_and_spatial_provenance"],
        }[kind],
        "state_restore": "explicit_checkpoint_restore"
        if kind == "analytics"
        else "checkpoint_in_session;recompute_after_restart"
        if kind in {"activity", "rally"}
        else "stateless",
    }
    for kind in DOMAIN_PORTS
}


class _Identity:
    """Create fresh existing identity state at each declared temporal epoch."""

    def __init__(self, context: DomainContext) -> None:
        self.context = context

    def named_resolver(self) -> NamedIdentity:
        return IdentityResolver(
            frame_height=float(self.context.frame_height), rebind_gap_frames=round(2 * self.context.fps)
        )

    def participant_tracker(self, instance_id: str) -> ParticipantIdentity:
        return ParticipantTracker(float(self.context.frame_height), fps=self.context.fps, instance_id=instance_id)

    def team_tracker(self) -> TeamIdentity:
        return DoublesTeamTracker(self.context.fps)


class _Contact:
    def __init__(self, params: dict[str, Any]) -> None:
        # Participant geometry belongs to the contact composition after peak
        # selection; keep its full configuration in the component fingerprint.
        params = {key: value for key, value in params.items() if key != "participant_geometry"}
        allowed = {"p_min", "nms_s", "min_same_player_gap_s"}
        if params.keys() - allowed:
            raise ValueError("unsupported contact provider parameters")
        self.params = dict(params)

    def detect(self, window: WindowObs, **kwargs: Any) -> list[ContactCandidate]:
        return detect_contacts(window, **{**self.params, **kwargs})


@dataclass(frozen=True, slots=True)
class _TemporalCheckpoint:
    owner: str
    state: dict[str, Any]


class _MotionReliableContact(_Contact):
    def __init__(self, params: dict[str, Any]) -> None:
        params = dict(params)
        if "spatial_sigma_px" not in params:
            raise ValueError("motion-reliability contact requires an explicit image sensitivity scale")
        self.policy = ContactMotionReliability(params.pop("spatial_sigma_px"))
        super().__init__(params)

    def detect(self, window: WindowObs, **kwargs: Any) -> list[ContactCandidate]:
        return detect_contacts(window, **{**self.params, **kwargs}, motion_reliability=self.policy)


class _BaselineTemporalState:
    """Only these baseline adapters own pure Python temporal state.

    A custom provider implements its own opaque checkpoint/restore contract;
    neither the engine nor registry deepcopies that provider or its models.
    """

    def checkpoint(self) -> _TemporalCheckpoint:
        return _TemporalCheckpoint(
            self._checkpoint_owner,
            copy.deepcopy({key: value for key, value in self.__dict__.items() if key != "_checkpoint_owner"}),
        )

    def restore(self, checkpoint: object) -> None:
        if not isinstance(checkpoint, _TemporalCheckpoint) or checkpoint.owner != self._checkpoint_owner:
            raise ValueError("incompatible temporal checkpoint")
        owner = self._checkpoint_owner
        self.__dict__.clear()
        self.__dict__.update(copy.deepcopy(checkpoint.state))
        self._checkpoint_owner = owner


class _Activity(_BaselineTemporalState, ActivityTracker):
    def __init__(self, fps: float, **params: Any) -> None:
        self._checkpoint_owner = str(uuid4())
        self._configuration = (fps, dict(params))
        super().__init__(fps, **params)

    def reset(self) -> None:
        fps, params = self._configuration
        ActivityTracker.__init__(self, fps, **params)

    def close(self) -> None:
        self._window.clear()


class _Rally(_BaselineTemporalState, RallyFSM):
    def __init__(self, params: RallyParams) -> None:
        self._checkpoint_owner = str(uuid4())
        RallyFSM.__init__(self, params=params)

    def reset(self) -> None:
        RallyFSM.__init__(self, params=self.params)

    def close(self) -> None:
        self._recent.clear()


class _EvidenceRally(_BaselineTemporalState, EvidenceRallyFSM):
    def __init__(
        self,
        params: RallyParams,
        *,
        use_reconstruction: bool = True,
        motion_guard: bool = False,
        use_exit_recovery: bool = False,
    ) -> None:
        self._checkpoint_owner = str(uuid4())
        super().__init__(
            params,
            use_reconstruction=use_reconstruction,
            motion_guard=motion_guard,
            use_exit_recovery=use_exit_recovery,
        )

    def reset(self) -> None:
        EvidenceRallyFSM.__init__(
            self,
            self.params,
            use_reconstruction=self.use_reconstruction,
            motion_guard=self.motion_guard,
            use_exit_recovery=self.use_exit_recovery,
        )

    def close(self) -> None:
        self._recent.clear()
        self._motion.clear()


class _TrackletEvidenceRally(_EvidenceRally):
    """Keep v2 starts; associate one singleton only for a qualified event.

    Qualification uses the existing minimum duration BEFORE the loss. Waiting
    through unknown observations cannot confirm a provisional event.
    """

    last_exit_support: ImageExitReturnSupport | None = None
    last_exit_support_frame: int | None = None

    def __init__(self, params: RallyParams, *, use_curve_exit: bool = False, **options: Any) -> None:
        if type(use_curve_exit) is not bool:
            raise ValueError("curve exit support requires a strict boolean")
        self.use_curve_exit = use_curve_exit
        super().__init__(params, **options)

    def reset(self) -> None:
        super().reset()
        self.last_exit_support = None
        self.last_exit_support_frame = None

    def close(self) -> None:
        super().close()
        self.last_exit_support = None
        self.last_exit_support_frame = None

    def exit_return_support(
        self,
        window: WindowObs,
        index: int,
        *,
        frame_height: float,
        raw_xy: Callable[[int, tuple[float, float]], tuple[float, float] | None],
    ) -> ImageExitReturnSupport:
        proof = image_exit_return_tracklet_support(
            window,
            index,
            frame_height=frame_height,
            raw_xy=raw_xy,
            minimum_speed=self.params.start_speed,
        )
        if self.use_curve_exit and proof.basis != "observed_top_exit_return":
            curve = image_exit_return_curve_support(
                window,
                index,
                frame_height=frame_height,
                raw_xy=raw_xy,
                minimum_speed=self.params.start_speed,
            )
            if curve.supported:
                proof = curve
        if proof.supported and proof.basis != "observed_top_exit_return":
            start = self.closed.start if self.closed is not None else self.start
            if start is None or proof.gap_start is None or proof.gap_start - start < self.params.min_frames:
                proof = replace(proof, supported=False, reason="event_not_qualified_before_loss")
        self.last_exit_support = proof
        self.last_exit_support_frame = window.frame0 + index
        return proof


class _Outcome:
    def predict(self, request: OutcomeInput) -> OutcomePrediction:
        window = request.window
        result = analyze_rally_end(
            window.frames,
            window.shuttle.x,
            window.shuttle.y,
            request.observed,
            request.terminal_frame,
            request.geometry,
            request.fps,
        )
        if not result.check.startswith("c0_static_"):
            return OutcomePrediction("unknown", "unknown", "terminal_not_observed", 0.2)
        return OutcomePrediction(result.outcome.value, result.fault, result.check, outcome_confidence(result))


class _Score:
    def initial(self, config: MatchConfig) -> MatchState:
        return initial_state(config)

    def apply(self, before: MatchState, winner: str, config: MatchConfig) -> RallyResult:
        return apply_rally(before, winner, config)  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class _AnalyticsCheckpoint:
    owner: str
    operations: tuple[tuple[str, tuple[Any, ...], dict[str, Any]], ...]


class TransactionalAnalytics(MatchAnalytics):
    """Checkpoint pure event/record inputs, never deepcopy an arbitrary provider.

    The aggregate remains the existing implementation. A rollback replays its
    typed input records; checkpoints survive a reset during an attempted refold.
    The containing engine treats a custom provider's checkpoint as opaque and
    invokes that provider's explicit restore method.
    """

    def __init__(self, fps: float) -> None:
        self._owner = str(uuid4())
        self._operations: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []
        super().__init__(fps)

    def on_stroke(self, event: Event, *, spatial_valid: bool = False) -> None:
        self._operations.append(("on_stroke", (event,), {"spatial_valid": spatial_valid}))
        super().on_stroke(event, spatial_valid=spatial_valid)

    def on_stroke_retracted(self, event: Event) -> None:
        self._operations.append(("on_stroke_retracted", (event,), {}))
        super().on_stroke_retracted(event)

    def on_presence(self, player_id: str, points: Any) -> None:
        saved = tuple(tuple(float(value) for value in point) for point in points)
        self._operations.append(("on_presence", (player_id, saved), {}))
        super().on_presence(player_id, saved)

    def on_rally(self, rally: RallyRecord) -> None:
        self._operations.append(("on_rally", (copy.deepcopy(rally),), {}))
        super().on_rally(rally)

    def checkpoint(self) -> _AnalyticsCheckpoint:
        return _AnalyticsCheckpoint(self._owner, tuple(copy.deepcopy(self._operations)))

    def restore(self, checkpoint: object) -> None:
        if not isinstance(checkpoint, _AnalyticsCheckpoint) or checkpoint.owner != self._owner:
            raise ValueError("incompatible analytics checkpoint")
        operations = copy.deepcopy(checkpoint.operations)
        MatchAnalytics.__init__(self, self.fps)
        for method, args, kwargs in operations:
            getattr(MatchAnalytics, method)(self, *args, **kwargs)
        self._operations = list(operations)

    def reset(self) -> None:
        self._operations = []
        MatchAnalytics.__init__(self, self.fps)

    def close(self) -> None:
        self._operations.clear()


def register_domain_components(registry: ComponentRegistry) -> None:
    def factory(kind: str):
        def create(context: DomainContext, configuration: dict[str, Any]) -> Any:
            params = configuration.get("params", configuration)
            if kind == "identity":
                if params:
                    raise ValueError("baseline identity provider has no tunable parameters")
                return _Identity(context)
            if kind == "contact":
                return _Contact(params)
            if kind == "stroke":
                if params:
                    raise ValueError("the baseline stroke provider has no tunable parameters")
                return RuleStrokeClassifier()
            if kind == "activity":
                return _Activity(context.fps, **params)
            if kind == "rally":
                return _Rally(RallyParams(fps=context.fps, **params))
            if kind == "analytics":
                if params:
                    raise ValueError("the baseline analytics provider has no tunable parameters")
                return TransactionalAnalytics(context.fps)
            if params:
                raise ValueError(f"the baseline {kind} provider has no tunable parameters")
            return _Outcome() if kind == "outcome" else _Score()

        return create

    for kind, interface in DOMAIN_PORTS.items():
        registry.register(
            ComponentContract(
                kind=kind,
                implementation=BASELINE_IMPLEMENTATIONS[kind],
                version="2" if kind == "rally" else "1",
                input_schema=f"badminton-{kind}-input:v1",
                output_schema=f"badminton-{kind}-output:v1",
                interface=interface,
                context_type=DomainContext,
                supported_formats=frozenset({"singles", "doubles", "unknown"}),
                failure_policy="abstain",
                stateful=kind in {"activity", "rally", "analytics"},
                declaration={**CONTRACT_DETAILS[kind], "optional_evidence": []},
            ),
            factory(kind),
        )

    def evidence_rally(context: DomainContext, configuration: dict[str, Any]) -> EvidenceRallySegmentation:
        params = dict(configuration.get("params", configuration))
        reconstruction = params.pop("use_reconstruction", True)
        motion_guard = params.pop("motion_guard", False)
        exit_recovery = params.pop("use_exit_recovery", False)
        return _EvidenceRally(
            RallyParams(fps=context.fps, **params),
            use_reconstruction=reconstruction,
            motion_guard=motion_guard,
            use_exit_recovery=exit_recovery,
        )

    def tracklet_rally(context: DomainContext, configuration: dict[str, Any]) -> AssociatedExitRallySegmentation:
        params = dict(configuration.get("params", configuration))
        curve = params.pop("use_curve_exit", False)
        options = {
            key: params.pop(key, default)
            for key, default in (("use_reconstruction", False), ("motion_guard", False), ("use_exit_recovery", True))
        }
        return _TrackletEvidenceRally(RallyParams(fps=context.fps, **params), use_curve_exit=curve, **options)

    registry.register(
        ComponentContract(
            kind="contact",
            implementation="contact-motion-reliability-v1",
            version="1",
            input_schema="badminton-contact-input:v1",
            output_schema="badminton-contact-output:v2",
            interface=ContactInference,
            context_type=DomainContext,
            supported_formats=frozenset({"singles", "doubles", "unknown"}),
            failure_policy="abstain",
            stateful=False,
            declaration={
                **CONTRACT_DETAILS["contact"],
                "optional_evidence": ["declared_image_localization_sensitivity"],
                "score_semantics": "uncalibrated_heuristic_support; experimental; no_contact_accuracy_claim",
            },
        ),
        lambda context, configuration: _MotionReliableContact(configuration.get("params", configuration)),
    )
    registry.register(
        ComponentContract(
            kind="rally",
            implementation="rally-evidence-tracklets-v1",
            version="1",
            input_schema="badminton-rally-evidence:v2",
            output_schema="badminton-rally-output:v1",
            interface=AssociatedExitRallySegmentation,
            context_type=DomainContext,
            supported_formats=frozenset({"singles", "doubles", "unknown"}),
            failure_policy="abstain",
            stateful=True,
            declaration={
                **CONTRACT_DETAILS["rally"],
                "required_evidence": ["typed_frame_aligned_observation_quality"],
                "optional_evidence": [
                    "qualified_event_singleton_exit_association:v1",
                    "optional_observed_bracket_image_curve:v1",
                ],
                "limitations": [
                    "VOD_available_window_only",
                    "no_new_coordinates_contacts_or_idle_starts",
                    "development_validation_only",
                ],
            },
        ),
        tracklet_rally,
    )

    registry.register(
        ComponentContract(
            kind="rally",
            implementation="rally-evidence-v2",
            version="2",
            input_schema="badminton-rally-evidence:v2",
            output_schema="badminton-rally-output:v1",
            interface=EvidenceRallySegmentation,
            context_type=DomainContext,
            supported_formats=frozenset({"singles", "doubles", "unknown"}),
            failure_policy="abstain",
            stateful=True,
            declaration={
                **CONTRACT_DETAILS["rally"],
                "required_evidence": ["typed_frame_aligned_observation_quality"],
                "optional_evidence": [
                    "bounded_estimated_trajectory",
                    "independently_observed_body_motion",
                    "observed_image_top_exit_reentry",
                ],
                "image_exit_max_gap_s": 2.0,
                "image_top_fraction": 0.1,
                "promotion": "exploratory_opt_in;not_validated_on_held_out_matches",
            },
        ),
        evidence_rally,
    )
