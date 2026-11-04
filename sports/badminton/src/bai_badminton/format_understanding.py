"""Replaceable format understanding from sustained target-court observations.

This is an uncalibrated observation policy, not a recognition accuracy claim.
A configured roster is authoritative. Missing people never downgrade doubles.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Literal, Protocol, runtime_checkable

from bai_engine.components import ComponentContract, ComponentRegistry

METHOD = "sustained_target_court_format_v1"
MatchFormat = Literal["singles", "doubles", "unknown"]


@dataclass(frozen=True, slots=True)
class FormatPerson:
    episode_id: str
    court_xy: tuple[float, float]
    detector_matched: bool


@dataclass(frozen=True, slots=True)
class FormatObservation:
    frame_idx: int
    persons: tuple[FormatPerson, ...]
    detector_observed: bool | None
    main_view: bool
    geometry_valid: bool
    full_court_visible: bool
    epoch: str
    cut: bool = False


@dataclass(frozen=True, slots=True)
class FormatPolicy:
    min_observations: int = 8
    min_duration_s: float = 3.0
    max_gap_s: float = 0.75

    def __post_init__(self) -> None:
        if (
            isinstance(self.min_observations, bool)
            or not isinstance(self.min_observations, int)
            or self.min_observations < 2
        ):
            raise ValueError("format minimum observations must be at least two")
        for value in (self.min_duration_s, self.max_gap_s):
            if isinstance(value, bool) or not math.isfinite(value) or value <= 0:
                raise ValueError("format duration and gap must be finite and positive")


@dataclass(frozen=True, slots=True)
class FormatDecision:
    match_format: MatchFormat = "unknown"
    source: str = "unknown"
    reason: str = "insufficient_evidence"
    revision: int = 0
    observed_frames: tuple[int, ...] = ()
    side_counts: tuple[int, int] = (0, 0)
    epoch: str | None = None

    def to_public(self) -> dict:
        return {
            "method": METHOD,
            "match_format": self.match_format,
            "source": self.source,
            "reason": self.reason,
            "revision": self.revision,
            "observed_frames": list(self.observed_frames),
            "side_counts": list(self.side_counts),
            "epoch": self.epoch,
            "support_kind": "uncalibrated_observation_policy",
            "requires_configuration": self.match_format == "unknown",
        }


@runtime_checkable
class FormatUnderstanding(Protocol):
    @property
    def decision(self) -> FormatDecision: ...

    def observe(self, observation: FormatObservation) -> FormatDecision: ...

    def reset(self) -> None: ...

    def close(self) -> None: ...


class SustainedCourtFormat:
    """Consume canonical frames and fresh feet in the selected court's metres.

    Singles requires explicitly asserted full-court observability as well as
    repeated one-per-side evidence. A camera cut clears only a candidate. A new
    target/calibration epoch invalidates inferred format, while keeping user
    configuration. Confirmed doubles is retained through later occlusion.
    """

    def __init__(self, *, fps: float, configured_format: str | None = None, policy: FormatPolicy | None = None) -> None:
        if isinstance(fps, bool) or not math.isfinite(fps) or fps <= 0:
            raise ValueError("format fps must be finite and positive")
        if configured_format not in (None, "singles", "doubles"):
            raise ValueError("configured format must be singles, doubles or absent")
        self.fps = float(fps)
        self.configured_format = configured_format
        self.policy = policy or FormatPolicy()
        self._closed = False
        self.reset()

    def reset(self) -> None:
        if self._closed:
            raise RuntimeError("format component is closed")
        self._last_frame: int | None = None
        self._last_fresh: int | None = None
        self._epoch: str | None = None
        self._candidate: str | None = None
        self._frames: list[int] = []
        self._revision = 0
        self._format = self.configured_format or "unknown"
        self._accepted_frames: tuple[int, ...] = ()
        self._accepted_counts = (0, 0)
        self._decision = FormatDecision(
            match_format=self._format,
            source="configured" if self.configured_format else "unknown",
            reason="configured_format" if self.configured_format else "insufficient_evidence",
        )

    @property
    def decision(self) -> FormatDecision:
        return self._decision

    @property
    def cache_identity(self) -> str:
        identity = {
            "method": METHOD,
            "fps": self.fps,
            "policy": asdict(self.policy),
            "configured_format": self.configured_format,
            "format": self._format,
            "epoch": self._epoch,
            "revision": self._revision,
        }
        return hashlib.sha256(json.dumps(identity, allow_nan=False, sort_keys=True).encode()).hexdigest()

    def _clear_candidate(self) -> None:
        self._candidate, self._frames, self._last_fresh = None, [], None

    def _publish(self, reason: str, counts: tuple[int, int] = (0, 0)) -> FormatDecision:
        source = "configured" if self.configured_format else "inferred" if self._format != "unknown" else "unknown"
        confirmed = self._format != "unknown" and not self.configured_format
        self._decision = FormatDecision(
            match_format=self._format,
            source=source,
            reason=reason,
            revision=self._revision,
            observed_frames=self._accepted_frames if confirmed else tuple(self._frames),
            side_counts=self._accepted_counts if confirmed else counts,
            epoch=self._epoch,
        )
        return self._decision

    @staticmethod
    def _counts(observation: FormatObservation) -> tuple[int, int] | None:
        episodes: set[str] = set()
        counts = [0, 0]
        for person in observation.persons:
            if person.detector_matched is not True:
                continue
            try:
                x, y = person.court_xy
                if not all(math.isfinite(value) and not isinstance(value, bool) for value in (x, y)):
                    return None
            except (ValueError, TypeError):
                return None
            # These are ground-foot bounds, never shuttle or landing geometry.
            if abs(x) > 3.05 or abs(y) > 6.7 or abs(y) < 0.2:
                continue
            if not isinstance(person.episode_id, str) or not person.episode_id or person.episode_id in episodes:
                return None
            episodes.add(person.episode_id)
            counts[0 if y < 0 else 1] += 1
        return counts[0], counts[1]

    def observe(self, observation: FormatObservation) -> FormatDecision:
        if self._closed:
            raise RuntimeError("format component is closed")
        frame = observation.frame_idx
        if isinstance(frame, bool) or not isinstance(frame, int) or frame < 0:
            raise ValueError("format frame must be a nonnegative canonical index")
        if self._last_frame is not None and frame <= self._last_frame:
            raise ValueError("format frames must increase strictly")
        if not isinstance(observation.epoch, str) or not observation.epoch:
            raise ValueError("format observation requires an epoch")
        self._last_frame = frame
        if self._epoch != observation.epoch:
            had_epoch = self._epoch is not None
            self._epoch = observation.epoch
            self._clear_candidate()
            if had_epoch and self.configured_format is None:
                if self._format != "unknown":
                    self._revision += 1
                self._format, self._accepted_frames, self._accepted_counts = "unknown", (), (0, 0)
        if observation.cut:
            self._clear_candidate()
            return self._publish("configured_format" if self.configured_format else "scene_cut")
        if self._last_fresh is not None and frame - self._last_fresh > self.policy.max_gap_s * self.fps:
            self._clear_candidate()
        if not observation.main_view or not observation.geometry_valid or observation.detector_observed is not True:
            return self._publish("configured_format" if self.configured_format else "unobserved_frame")
        counts = self._counts(observation)
        candidate = "doubles" if counts == (2, 2) else "singles" if counts == (1, 1) else None
        if candidate == "singles" and observation.full_court_visible is not True:
            self._clear_candidate()
            return self._publish(
                "configured_format" if self.configured_format else "incomplete_court_visibility", counts
            )
        if candidate is None:
            self._clear_candidate()
            return self._publish(
                "configured_format" if self.configured_format else "insufficient_evidence", counts or (0, 0)
            )
        if candidate != self._candidate:
            self._clear_candidate()
            self._candidate = candidate
        self._last_fresh = frame
        self._frames.append(frame)
        duration = (self._frames[-1] - self._frames[0]) / self.fps
        sustained = len(self._frames) >= self.policy.min_observations and duration >= self.policy.min_duration_s
        # Keep bounded provenance, including the first sustaining anchor.
        if len(self._frames) > max(32, self.policy.min_observations * 2):
            self._frames = [self._frames[0], *self._frames[-(self.policy.min_observations * 2 - 1) :]]
        if self.configured_format is not None:
            reason = (
                "configured_format_conflict"
                if sustained and candidate != self.configured_format
                else "configured_format"
            )
            return self._publish(reason, counts)
        if sustained and candidate != self._format and not (self._format == "doubles" and candidate == "singles"):
            self._format = candidate
            self._revision += 1
            self._accepted_frames = tuple(self._frames)
            self._accepted_counts = counts
        return self._publish("sustained_target_court" if self._format != "unknown" else "insufficient_evidence", counts)

    def close(self) -> None:
        self._closed = True


@dataclass(frozen=True, slots=True)
class FormatContext:
    fps: float
    configured_format: str | None = None


def register_format_components(registry: ComponentRegistry) -> None:
    def create(context: FormatContext, configuration: dict) -> SustainedCourtFormat:
        params = configuration.get("params", configuration)
        return SustainedCourtFormat(
            fps=context.fps,
            configured_format=context.configured_format,
            policy=FormatPolicy(**params),
        )

    registry.register(
        ComponentContract(
            kind="format",
            implementation="sustained-court-v1",
            version="1",
            input_schema="format-observation:v1",
            output_schema="format-decision:v1",
            interface=FormatUnderstanding,
            context_type=FormatContext,
            supported_formats=frozenset({"singles", "doubles", "unknown"}),
            failure_policy="unknown",
            stateful=True,
            declaration={
                "devices": ["cpu"],
                "timeline": "canonical_cfr_frame_index",
                "coordinates": "selected_court_ground_foot_metres",
                "required_evidence": ["fresh_target_court_people", "verified_geometry", "main_view"],
                "optional_evidence": ["explicit_roster", "full_court_observability"],
                "state_restore": "recompute_in_canonical_frame_order",
            },
        ),
        create,
    )
