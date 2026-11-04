"""Versioned, sport-owned ports and factories for image perception.

The baseline providers adapt the existing loaders. A component implementation
selects behavior; ``ModelChoice.model`` selects its artifact. Alternative
providers receive explicit dependencies and must meet the same observation
contract. Positions are canonical analysis-frame pixels, not 3D measurements.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import numpy as np
from numpy.typing import NDArray

from bai_badminton.perception.diagnostics import DiagnosticSelection, ShuttleDiagnostic
from bai_badminton.perception.players import CourtROI, PlayerPerception
from bai_badminton.perception.tracknet import BackgroundModel, ShuttleDetection
from bai_badminton.perception_types import PersonObs, RacketObservation, ScoreReading
from bai_engine.components import ComponentContract, ComponentRegistry
from bai_engine.config import ModelChoice
from bai_engine.runtime.registry import ModelRegistry


@runtime_checkable
class ShuttlePort(Protocol):
    """BGR frame sequence to image observations; missing detections stay None.

    Backgrounds and flight masks use the baseline 512x288 RGB image convention.
    A different tensor convention needs an adapter or a different port version.
    """

    seq_len: int
    bg: BackgroundModel

    def detect(
        self,
        frames_bgr: list[NDArray[np.uint8]],
        shots: list[int],
        *,
        step: int,
        masks: list[NDArray[np.uint8]] | None,
    ) -> list[ShuttleDetection | None]: ...


@runtime_checkable
class DiagnosticShuttlePort(ShuttlePort, Protocol):
    """Optional summaries; legacy independent shuttle providers remain valid."""

    supports_diagnostics: bool

    def detect_with_diagnostics(
        self,
        frames_bgr: list[NDArray[np.uint8]],
        shots: list[int],
        *,
        step: int,
        masks: list[NDArray[np.uint8]] | None,
        selection: DiagnosticSelection,
        indices: set[int],
    ) -> tuple[list[ShuttleDetection | None], list[ShuttleDiagnostic | None]]: ...


@runtime_checkable
class PlayerDetectorPort(Protocol):
    """BGR image to image-coordinate xyxy boxes and uncalibrated scores."""

    def __call__(self, image: NDArray[np.uint8]) -> tuple[NDArray[Any], NDArray[Any]]: ...


@runtime_checkable
class PosePort(Protocol):
    """BGR image and xyxy boxes to COCO17 image-coordinate x/y/confidence."""

    def __call__(self, image: NDArray[np.uint8], boxes: NDArray[Any]) -> list[NDArray[Any]]: ...


@runtime_checkable
class PlayerReIDPort(Protocol):
    """Appearance features support episode linking, not a named identity."""

    fingerprint: str

    def embed(self, image: NDArray[np.uint8], boxes: NDArray[Any]) -> NDArray[Any]: ...


@runtime_checkable
class RacketPort(Protocol):
    """Image equipment observations indexed by the supplied track episodes."""

    def detect(self, image: NDArray[np.uint8], persons: list[PersonObs]) -> dict[int, RacketObservation]: ...


@runtime_checkable
class OCRPort(Protocol):
    """Canonical-frame source-board readings, independent of point decisions."""

    calls: int

    def maybe_read(self, frame_idx: int, image: NDArray[np.uint8]) -> ScoreReading | None: ...


@runtime_checkable
class TrackingPort(Protocol):
    detector: PlayerDetectorPort | None
    pose: PosePort | None
    reid: PlayerReIDPort | None
    max_players: int
    last_detector_observed: bool
    last_capacity_limited: bool
    last_identity_error: str | None
    identity_policy: dict[str, Any]

    def process(self, frame_idx: int, image: NDArray[np.uint8], strides: tuple[int, int]) -> list[PersonObs]: ...

    def set_roi(self, roi: CourtROI | None) -> None: ...

    def on_cut(self) -> None: ...

    def reset(self) -> None: ...

    def close(self) -> None: ...


@dataclass(frozen=True, slots=True)
class TrackingContext:
    registry: ModelRegistry
    cache: Path
    fps: float
    frame_size: tuple[int, int] | None
    detector: PlayerDetectorPort | None
    pose: PosePort | None
    reid: PlayerReIDPort | None
    max_players: int
    det_stride: int
    pose_stride: int
    identity_retention_s: float
    record_model: Callable[[str, str], None]
    record_runtime: Callable[[str, dict[str, Any]], None]


class _Tracking(PlayerPerception):
    def reset(self) -> None:
        self.on_cut()

    def close(self) -> None:
        self.on_cut()
        self.detector = self.pose = self.reid = self.tracker = self._associator = None


def _tracking_factory(context: TrackingContext, configuration: dict[str, Any]) -> TrackingPort:
    params = configuration.get("params", {})
    if params.keys() - {"identity_retention_s"}:
        raise ValueError("unsupported tracking provider parameters")
    result = _Tracking(
        context.detector,
        context.pose,
        context.fps,
        det_stride=context.det_stride,
        pose_stride=context.pose_stride,
        max_players=context.max_players,
        reid=context.reid,
        identity_retention_s=float(params.get("identity_retention_s", context.identity_retention_s)),
    )
    context.record_model("tracking", "court-player-episodes-v1@1")
    return result


PERCEPTION_PORTS: dict[str, type[Any]] = {
    "shuttle": ShuttlePort,
    "player_detector": PlayerDetectorPort,
    "pose": PosePort,
    "player_reid": PlayerReIDPort,
    "racket": RacketPort,
    "ocr": OCRPort,
    "tracking": TrackingPort,
}

BASELINE_IMPLEMENTATIONS = {
    "shuttle": "tracknet-v3",
    "player_detector": "person-onnx-v1",
    "pose": "rtmpose-v1",
    "player_reid": "osnet-appearance-v1",
    "racket": "racket-geometry-v1",
    "ocr": "rapidocr-v1",
    "tracking": "court-player-episodes-v1",
}


@dataclass(frozen=True, slots=True)
class PerceptionContext:
    """Per-session model dependencies, with no global registry or hidden loader.

    The six loader callbacks preserve existing verified artifact loading. Custom
    providers can use the registry directly and record actual artifact/runtime
    evidence after construction. No factory receives score or reference labels.
    """

    registry: ModelRegistry
    cache: Path
    fps: float
    frame_size: tuple[int, int] | None
    load_shuttle: Callable[[ModelChoice, ModelRegistry, Path], Any]
    load_detector: Callable[[ModelChoice, ModelRegistry, Path], Any]
    load_pose: Callable[[ModelChoice, ModelRegistry, Path], Any]
    load_reid: Callable[[ModelChoice, ModelRegistry], Any]
    load_racket: Callable[[ModelChoice], Any]
    load_ocr: Callable[[ModelChoice, ModelRegistry, float], Any]
    record_model: Callable[[str, str], None]
    record_runtime: Callable[[str, dict[str, Any]], None]


class _ShuttleAdapter:
    """Own TrackNet's background lifetime without replacing its verified model."""

    def __init__(self, model: Any) -> None:
        self._raw_model = model

    @property
    def raw_model(self) -> Any:
        if self._raw_model is None:
            raise RuntimeError("shuttle component is closed")
        return self._raw_model

    @property
    def seq_len(self) -> int:
        return int(self.raw_model.seq_len)

    @property
    def bg(self) -> BackgroundModel:
        return self.raw_model.bg

    @property
    def runtime(self) -> dict[str, Any]:
        return self.raw_model.runtime

    @property
    def model_ref(self) -> str:
        return str(self.raw_model.model_ref)

    def detect(self, frames_bgr, shots, *, step, masks):  # type: ignore[no-untyped-def]
        return self.raw_model.detect(frames_bgr, shots, step=step, masks=masks)

    def detect_with_diagnostics(self, frames_bgr, shots, *, step, masks, selection, indices):  # type: ignore[no-untyped-def]
        return self.raw_model.detect_with_diagnostics(
            frames_bgr, shots, step=step, masks=masks, selection=selection, indices=indices
        )

    @property
    def supports_diagnostics(self) -> bool:
        return callable(getattr(self.raw_model, "detect_with_diagnostics", None))

    def reset(self) -> None:
        old = self.raw_model.bg
        self.raw_model.bg = BackgroundModel(every=old.every, capacity=old.capacity, refresh=old.refresh)

    def close(self) -> None:
        model, self._raw_model = self._raw_model, None
        close = getattr(model, "close", None)
        if callable(close):
            close()


class _OCRAdapter:
    """Reset reader search, cadence and ROI while retaining the loaded recognizer."""

    def __init__(self, reader: Any) -> None:
        self._raw_model = reader

    @property
    def raw_model(self) -> Any:
        if self._raw_model is None:
            raise RuntimeError("ocr component is closed")
        return self._raw_model

    @property
    def calls(self) -> int:
        return int(self.raw_model.calls)

    @property
    def runtime(self) -> dict[str, Any]:
        return self.raw_model.runtime

    @property
    def model_ref(self) -> str:
        return str(self.raw_model.model_ref)

    def maybe_read(self, frame_idx, image):  # type: ignore[no-untyped-def]
        return self.raw_model.maybe_read(frame_idx, image)

    def reset(self) -> None:
        reader = self.raw_model
        reader.roi, reader._corner, reader._misses = None, 0, 0
        reader._last, reader.calls = -(10**9), 0

    def close(self) -> None:
        reader, self._raw_model = self._raw_model, None
        close = getattr(reader, "close", None)
        if callable(close):
            close()


def _baseline_factory(kind: str) -> Callable[[PerceptionContext, dict[str, Any]], Any]:
    def create(context: PerceptionContext, configuration: dict[str, Any]) -> Any:
        choice = ModelChoice.model_validate(configuration)
        if kind == "shuttle":
            model = context.load_shuttle(choice, context.registry, context.cache)
        elif kind == "player_detector":
            model = context.load_detector(choice, context.registry, context.cache)
        elif kind == "pose":
            model = context.load_pose(choice, context.registry, context.cache)
        elif kind == "player_reid":
            model = context.load_reid(choice, context.registry)
        elif kind == "racket":
            model = context.load_racket(choice)
        else:
            model = context.load_ocr(choice, context.registry, context.fps)
        if model is None:
            raise RuntimeError(f"baseline {kind} provider is unavailable")
        runtime = getattr(model, "runtime", None)
        if isinstance(runtime, dict):
            context.record_runtime(kind, runtime)
        if kind == "shuttle":
            return _ShuttleAdapter(model)
        if kind == "ocr":
            return _OCRAdapter(model)
        return model

    return create


def register_perception_components(registry: ComponentRegistry) -> None:
    """Register compatible model and tracking baseline ports in a caller-supplied registry.

    Registration is explicit; duplicate providers are rejected by the registry.
    Baseline providers support two/four/uncertain acquisition. This capability
    does not infer a format or claim that a downstream singles model is valid
    for doubles. Backend/artifact verification remains in each existing loader.
    """
    for kind, interface in PERCEPTION_PORTS.items():
        registry.register(
            ComponentContract(
                kind=kind,
                implementation=BASELINE_IMPLEMENTATIONS[kind],
                version="3" if kind == "ocr" else "1",
                input_schema=f"badminton-{kind}-input:v1",
                output_schema=f"badminton-{kind}-output:v1",
                interface=interface,
                context_type=TrackingContext if kind == "tracking" else PerceptionContext,
                supported_formats=frozenset({"singles", "doubles", "unknown"}),
                failure_policy="unavailable",
                stateful=kind in {"shuttle", "ocr", "tracking"},
                declaration={
                    "devices": (["cpu"] if kind in {"racket", "tracking"} else ["cpu", "cuda"]),
                    "backends": {
                        "shuttle": ["torch-cpu", "torch-cuda", "onnx-cpu", "onnx-cuda", "tensorrt"],
                        "player_detector": ["onnx-cpu", "onnx-cuda", "tensorrt"],
                        "pose": ["onnx-cpu", "onnx-cuda", "tensorrt"],
                        "player_reid": ["torch-cpu", "torch-cuda"],
                        "racket": ["opencv-cpu"],
                        "ocr": ["onnx-cpu", "onnx-cuda"],
                        "tracking": ["none"],
                    }[kind],
                    "timeline": "canonical_cfr_frame_index",
                    "coordinates": "analysis_proxy_image_pixels;BGR_input;shuttle_masks_512x288",
                    "required_evidence": ["view_eligible_image"],
                    "optional_evidence": ["verified_target_court", "current_person_and_pose_for_racket"],
                    "state_restore": "recompute_in_frame_order"
                    if kind in {"shuttle", "ocr", "tracking"}
                    else "stateless",
                },
            ),
            _tracking_factory if kind == "tracking" else _baseline_factory(kind),
        )
