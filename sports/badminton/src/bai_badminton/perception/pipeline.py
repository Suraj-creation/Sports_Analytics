"""Badminton perception for one decoded chunk: cuts → court & camera → shuttle → players → pose.

Model loading is profile-driven and *degrades gracefully*: a model whose weights are missing or
fail to load is disabled with a recorded reason (surfaced as a ``degraded`` event), and the rest
of the pipeline keeps running — e.g. without the shuttle model the platform still tracks players
and pose; without the detector it still tracks the shuttle.

Court geometry has three modes (``BadmintonPerception.mode``):

* ``lines`` — the court is *measured in every frame* from its painted lines
  (:mod:`bai_badminton.perception.court_lines`), each frame's camera is identified, and only the main
  camera (the calibration's) is analysed; other cameras are calibrated for display only.
* ``camera`` — legacy fallback when the lines cannot be followed: the calibration's reference frame is
  registered by its background (:class:`~bai_badminton.perception.camera.CameraTracker`).
* ``static`` — one homography for every frame (no reference frame to track from).

Rates: detector / pose strides depend on the rally state reported by the match engine
(``in_play`` vs ``idle``) using the profile's ``Rates``; on frames that are not analysed
(other cameras, close-ups, replays) perception is skipped entirely.
"""

from __future__ import annotations

import hashlib
import json
import zlib
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

import numpy as np

from bai_badminton.court import REFERENCE_POINTS, WIDTH_DOUBLES, Homography
from bai_badminton.perception.calibration_state import CalibrationLifecycle
from bai_badminton.perception.camera import CameraTracker, project
from bai_badminton.perception.components import (
    BASELINE_IMPLEMENTATIONS,
    PERCEPTION_PORTS,
    DiagnosticShuttlePort,
    PerceptionContext,
    TrackingContext,
    register_perception_components,
)
from bai_badminton.perception.court_lines import CameraRig, CourtTracker, camera_pose
from bai_badminton.perception.diagnostics import DiagnosticSelection, FrameDiagnostic
from bai_badminton.perception.isolation import flight_mask
from bai_badminton.perception.players import CourtROI, PlayerDetector, PoseEstimator
from bai_badminton.perception.scene import CourtPresence, CutDetector, small_hsv
from bai_badminton.perception.scoreboard import ScoreboardReader
from bai_badminton.perception_types import ChunkPerception, FramePerception, ScoreObservationContext, ScoreReading
from bai_engine.components import ComponentHandle, ComponentRegistry
from bai_engine.config import ModelChoice, Profile
from bai_engine.decode import DecodedChunk
from bai_engine.obs import INFERENCE_FPS, get_logger, timed
from bai_engine.runtime.device import engine_cache_dir, ort_providers, ort_runtime
from bai_engine.runtime.registry import ModelError, ModelRegistry

log = get_logger(__name__)


@dataclass
class Degradation:
    stage: str
    reason: str


@dataclass
class _Scene:
    views: list[str]  # main | alt | none
    heads: list[int | None]
    quality: list[float | None]
    poses: list[np.ndarray | None] | None  # None: the camera is not tracked
    polys: list[np.ndarray | None]
    held: list[bool] = field(default_factory=list)
    broadcast_replay_status: list[str] = field(default_factory=list)


@dataclass
class PerceptionStats:
    frames: int = 0
    shuttle_frames: int = 0
    det_calls: int = 0
    pose_calls: int = 0
    ocr_calls: int = 0
    ocr_readings: int = 0
    seconds: dict[str, float] = field(default_factory=dict)


def lines_ref_id(H: np.ndarray) -> int:
    """Id of a court-line reference calibration (cached perception made against another is stale)."""
    Hn = np.asarray(H, np.float64) / float(H[2][2])
    return zlib.crc32(b"lines:" + np.round(Hn, 6).tobytes())


class BadmintonPerception:
    def __init__(
        self,
        profile: Profile,
        registry: ModelRegistry,
        fps: float,
        models_dir: Path,
        frame_size: tuple[int, int] | None = None,
        *,
        match_format: str = "singles",
        component_registry: ComponentRegistry | None = None,
        context_identity: dict[str, Any] | None = None,
    ) -> None:
        if match_format not in ("singles", "doubles", "unknown"):
            raise ValueError("unknown match format")
        self.match_format = match_format
        self.profile = profile.model_copy(deep=True)
        profile = self.profile
        self.fps = fps
        self.frame_size = frame_size
        self.degraded: list[Degradation] = []
        self.models: dict[str, str] = {}
        self.runtimes: dict[str, dict[str, Any]] = {}
        self.cuts = CutDetector()
        self.presence: CourtPresence | None = None
        self.camera = CameraTracker()  # legacy: keeps a calibration on a panning camera by its background
        self.calibration_lifecycle = CalibrationLifecycle()
        self._calibration_last_frame: int | None = None
        self.court = CourtTracker()  # measures the court in every frame from its painted lines
        self.rig: CameraRig | None = None  # the production's cameras (head 0 = the calibration's)
        self.mode = "static"
        self._H_ref: np.ndarray | None = None  # court → reference-view px of the installed calibration
        self._lines_id: int | None = None
        self._ref_poly: np.ndarray | None = None  # court polygon in the reference view (px)
        self._court_samples: list[tuple[np.ndarray, tuple[int, int]]] = []  # small HSV keyframes
        self.stats = PerceptionStats()
        cache = engine_cache_dir(models_dir)
        cache.mkdir(parents=True, exist_ok=True)
        if component_registry is None:
            component_registry = ComponentRegistry()
            register_perception_components(component_registry)
        self.component_registry = component_registry
        self.component_handles: dict[str, ComponentHandle] = {}
        self._component_metadata: dict[str, dict[str, Any]] = {}
        self.effective_choices: dict[str, ModelChoice | None] = {
            kind: profile.components.get(kind, getattr(profile, kind, None)) for kind in PERCEPTION_PORTS
        }
        shuttle_choice = self.effective_choices["shuttle"]
        self.diagnostic_selection = DiagnosticSelection.parse(
            shuttle_choice.params.get("diagnostics") if shuttle_choice is not None else None
        )
        self.flight_region = (
            shuttle_choice.params.get("flight_region", "bounded_upward_sweep_v1")
            if shuttle_choice
            else "bounded_upward_sweep_v1"
        )
        if self.flight_region not in {"bounded_upward_sweep_v1", "vertical_columns_to_image_top_v1"}:
            raise ValueError("unsupported shuttle flight-region policy")
        ocr_choice = self.effective_choices["ocr"]
        self.ocr_scene_policy = ocr_choice.params.get("scene_policy", "main_camera") if ocr_choice else "main_camera"
        if self.ocr_scene_policy not in ("main_camera", "all_image_broadcast_overlay"):
            raise ValueError("unsupported OCR scene_policy")
        tracking_choice = self.effective_choices["tracking"] or ModelChoice(model="none", backend="none")
        self.effective_choices["tracking"] = tracking_choice.model_copy(
            update={
                "implementation": tracking_choice.implementation or BASELINE_IMPLEMENTATIONS["tracking"],
            }
        )
        context = PerceptionContext(
            registry=registry,
            cache=cache,
            fps=fps,
            frame_size=frame_size,
            load_shuttle=self._load_shuttle,
            load_detector=self._load_detector,
            load_pose=self._load_pose,
            load_reid=self._load_reid,
            load_racket=self._load_racket,
            load_ocr=self._load_ocr,
            record_model=self.models.__setitem__,
            record_runtime=self._record_runtime,
        )
        identity = {
            "session": context_identity if context_identity is not None else {},
            "fps": fps,
            "frame_size": list(frame_size) if frame_size is not None else None,
            "ocr_every_s": profile.ocr_every_s,
        }
        self.shuttle = self._create_component("shuttle", context, identity)
        det = self._create_component("player_detector", context, identity)
        pose = self._create_component("pose", context, identity)
        # Preserve the legacy singles policy. An explicit component selection can
        # enable appearance on singles too; uncertain acquisition keeps capacity4.
        reid = (
            self._create_component("player_reid", context, identity)
            if match_format != "singles" or "player_reid" in profile.components
            else None
        )
        self.scoreboard = self._create_component("ocr", context, identity)
        self.racket = self._create_component("racket", context, identity)
        reid_choice = self.effective_choices["player_reid"]
        tracking_context = TrackingContext(
            registry=registry,
            cache=cache,
            fps=fps,
            frame_size=frame_size,
            detector=det,
            pose=pose,
            reid=reid,
            max_players=2 if match_format == "singles" else 4,
            det_stride=profile.detector_rates.in_play,
            pose_stride=profile.pose_rates.in_play,
            identity_retention_s=float(reid_choice.params.get("retention_seconds", 1.0)) if reid_choice else 1.0,
            record_model=self.models.__setitem__,
            record_runtime=self._record_runtime,
        )
        self.players = self._create_component(
            "tracking",
            tracking_context,
            {
                **identity,
                "dependencies": {
                    kind: self._component_metadata[kind]["fingerprint"]
                    for kind in ("player_detector", "pose", "player_reid")
                    if kind in self._component_metadata
                },
            },
        )
        if self.players is None:
            self.close()
            reason = next((item.reason for item in reversed(self.degraded) if item.stage == "tracking"), "unavailable")
            raise RuntimeError(f"tracking component unavailable: {reason}")

    def _create_component(
        self, kind: str, context: PerceptionContext | TrackingContext, identity: dict[str, Any]
    ) -> Any | None:
        choice = self.effective_choices[kind]
        if choice is None:
            return None
        # Explicit providers may be weightless; legacy artifact disable flags
        # continue to disable the baseline rather than constructing a model.
        if choice.implementation is None and (choice.model == "none" or choice.backend == "none"):
            return None
        degraded_before = len(self.degraded)
        try:
            handle = self.component_registry.create(
                kind,
                choice.implementation or BASELINE_IMPLEMENTATIONS[kind],
                context=context,
                configuration=choice.model_dump(mode="json"),
                match_format=self.match_format,
                context_identity=identity,
            )
        except (ModelError, OSError, ValueError, ImportError, RuntimeError, TypeError) as exc:
            # A failed explicit provider never falls back to another method.
            if not any(item.stage == kind for item in self.degraded[degraded_before:]):
                self._degrade(kind, str(exc))
            return None
        self.component_handles[kind] = handle
        actual = {
            "model": self.models.get(kind),
            "runtime": self.runtimes.get(kind, {}),
        }
        # The generic construction fingerprint includes configuration/context.
        # Artifact identity can become known only inside a verified factory, so
        # bind its actual post-load evidence into the exported cache identity.
        fingerprint = hashlib.sha256(
            json.dumps(
                {"construction": handle.fingerprint, **actual},
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        self._component_metadata[kind] = json.loads(
            json.dumps(
                {
                    "contract": handle.contract.describe(),
                    "configuration": choice.model_dump(mode="json"),
                    "fingerprint": fingerprint,
                    **actual,
                },
                allow_nan=False,
            )
        )
        return handle.instance

    @property
    def component_metadata(self) -> dict[str, dict[str, Any]]:
        """Detached provider/artifact evidence for session metadata and cache keys."""
        return json.loads(json.dumps(self._component_metadata, allow_nan=False))

    def reset_components(self) -> None:
        """Clear provider-owned temporal evidence at an explicit session boundary."""
        for handle in self.component_handles.values():
            handle.reset()

    def close(self) -> None:
        for handle in reversed(list(self.component_handles.values())):
            handle.close()

    @property
    def identity_policy(self) -> dict[str, Any]:
        choice = getattr(self, "effective_choices", {}).get("player_reid", getattr(self.profile, "player_reid", None))
        return {
            **getattr(self.players, "identity_policy", {"state": "disabled"}),
            "requested_model": choice.model if choice is not None else None,
        }

    # ------------------------------------------------------------------ loading
    def _load_racket(self, choice: ModelChoice | None):  # type: ignore[no-untyped-def]
        if choice is None or choice.model == "none" or choice.backend == "none":
            return None
        if choice.model != "racket_geometry_v1" or choice.backend != "opencv-cpu":
            self._degrade("racket", f"{choice.model}: no verified local adapter; select racket_geometry_v1 explicitly")
            return None
        from bai_badminton.perception.racket import RacketDetector

        self.models["racket"] = "racket_geometry_v1@1"
        self.runtimes["racket"] = {
            "requested_backend": choice.backend,
            "actual_backend": "opencv-cpu",
            "backend_fallback": False,
            "method": "opencv_ellipse_shaft_v1",
        }
        return RacketDetector()

    def _providers(self, choice: ModelChoice, cache: Path, *, model_digest: str | None = None) -> list[Any]:
        return ort_providers(
            choice.backend,
            engine_cache=cache / choice.model,
            fp16=choice.precision == "fp16",
            model_digest=model_digest,
        )

    def _load_shuttle(self, c: ModelChoice, reg: ModelRegistry, cache: Path):  # type: ignore[no-untyped-def]
        if c.model == "none" or c.backend == "none":
            return None
        try:
            from bai_badminton.perception.tracknet import TrackNetV3

            with reg.open_verified(c.model) as artifact:
                m = TrackNetV3(
                    artifact.path,
                    checkpoint_stream=artifact.stream,
                    expected_sha256=artifact.sha256,
                    backend=c.backend,
                    threshold=float(c.params.get("threshold", 0.5)),
                    onnx_dir=cache / c.model,
                    provider_factory=lambda graph_sha: self._providers(c, cache, model_digest=graph_sha),
                    batch=c.batch,
                    precision=c.precision,
                )
            self._record_runtime("shuttle", m.runtime)
            self.models["shuttle"] = reg.get(c.model).ref
            return m
        except (ModelError, OSError, ValueError, ImportError, RuntimeError) as e:
            self._degrade("shuttle", f"{c.model}: {e}")
            return None

    def _load_detector(self, c: ModelChoice, reg: ModelRegistry, cache: Path) -> PlayerDetector | None:
        if c.model == "none" or c.backend == "none":
            return None
        try:
            spec = reg.get(c.model)
            size = c.input_size or (spec.input.get("width", 384), spec.input.get("height", 384))
            kind = "rfdetr" if c.model.startswith("rfdetr") else "yolox"
            d = PlayerDetector(
                reg.path(c.model),
                (int(size[0]), int(size[1])),
                self._providers(c, cache),
                score_thr=float(c.params.get("score_threshold", 0.35)),
                kind=kind,
            )
            self._record_runtime("player_detector", ort_runtime(c.backend, d.tool.session))
            self.models["player_detector"] = spec.ref
            return d
        except (ModelError, OSError, ValueError, ImportError, RuntimeError) as e:
            self._degrade("player_detector", f"{c.model}: {e}")
            return None

    def _load_pose(self, c: ModelChoice, reg: ModelRegistry, cache: Path) -> PoseEstimator | None:
        if c.model == "none" or c.backend == "none":
            return None
        try:
            spec = reg.get(c.model)
            size = c.input_size or (spec.input.get("width", 192), spec.input.get("height", 256))
            p = PoseEstimator(reg.path(c.model), (int(size[0]), int(size[1])), self._providers(c, cache))
            self._record_runtime("pose", ort_runtime(c.backend, p.tool.session))
            self.models["pose"] = spec.ref
            return p
        except (ModelError, OSError, ValueError, ImportError, RuntimeError) as e:
            self._degrade("pose", f"{c.model}: {e}")
            return None

    def _load_reid(self, choice: ModelChoice | None, registry: ModelRegistry) -> Any | None:
        if choice is None or choice.model == "none" or choice.backend == "none":
            return None
        try:
            from bai_badminton.perception.offline_reid import OSNetAppearanceEmbedder

            if (
                choice.model != "osnet_ain_x0_25"
                or choice.precision != "fp32"
                or choice.backend not in ("torch-cpu", "torch-cuda")
            ):
                raise ValueError(
                    "OSNet identity inference requires the pinned model, FP32 and an explicit Torch device"
                )
            checkpoint = registry.path(choice.model, fetch=False)
            model = OSNetAppearanceEmbedder(
                checkpoint, device="cuda:0" if choice.backend == "torch-cuda" else "cpu", max_crops=8
            )
            self.models["player_reid"] = registry.get(choice.model).ref
            return model
        except (ModelError, OSError, ValueError, ImportError, RuntimeError) as exc:
            self._degrade("player_identity", f"{choice.model}: {exc}")
            return None

    def _load_ocr(self, c: ModelChoice | None, reg: ModelRegistry, fps: float) -> ScoreboardReader | None:
        if c is None or c.model == "none" or c.backend == "none":
            return None
        try:
            spec = reg.get(c.model)
            if spec.format != "package" or spec.source.get("package") != "rapidocr":
                raise ModelError(f"{c.model} is not a RapidOCR package alias")
            r = ScoreboardReader.load(every=max(1, int(round(self.profile.ocr_every_s * fps))), backend=c.backend)
            self.models["ocr"] = r.model_ref
            if r.runtime.get("backend_fallback"):
                providers = {stage: info["providers"] for stage, info in r.runtime["stages"].items()}
                self._degrade("ocr_backend", f"Requested {c.backend}; actual OCR providers: {providers}")
            return r
        except (ModelError, OSError, ValueError, ImportError, RuntimeError) as e:
            self._degrade("ocr", f"{c.model}: {e}")
            return None

    def _degrade(self, stage: str, reason: str) -> None:
        log.warning("perception.degraded", stage=stage, reason=reason)
        self.degraded.append(Degradation(stage, reason))

    def _record_runtime(self, stage: str, runtime: dict[str, Any]) -> None:
        if not hasattr(self, "runtimes"):
            self.runtimes = {}
        self.runtimes[stage] = runtime
        if runtime.get("backend_fallback"):
            self._degrade(f"{stage}_backend", f"Requested {runtime['requested_backend']}; actual runtime: {runtime}")

    # ------------------------------------------------------------------ calibration
    @property
    def ref_id(self) -> int | None:
        """Id of the view poses (``FramePerception.cam``) are relative to; ``None`` when untracked."""
        if self.mode == "lines":
            return self._lines_id
        return self.camera.ref_id if self.mode == "camera" else None

    def set_calibration(self, h: Homography, reference: np.ndarray | None = None, mode: str | None = None) -> str:
        """Install the court calibration; returns the geometry mode actually used.

        ``mode="lines"``: ``h`` is a court-line calibration of the main camera — every frame is measured from
        its lines and frames from other cameras are not analysed (needs a plausible camera pose for ``h``).
        Otherwise ``reference`` (the frame ``h`` was fitted on) enables background tracking of a panning
        camera, and without it the calibration is taken to hold for the whole shot (fixed camera)."""
        names = ("far_left", "far_right", "near_right", "near_left")
        poly = h.court_to_image(np.array([REFERENCE_POINTS[n] for n in names])).astype(np.float32)
        self.players.on_cut()
        self.players.set_roi(CourtROI(poly, homography=h))
        self.presence = CourtPresence(poly)
        self._ref_poly = poly
        self._H_ref = np.asarray(h.H, np.float64)
        self._learn_court_colour()
        self.camera.clear()
        self.court.reset()
        self.calibration_lifecycle = CalibrationLifecycle()
        self._calibration_last_frame = None
        self.rig, self._lines_id, self.mode = None, None, "static"
        size = self.frame_size or (None if reference is None else (reference.shape[1], reference.shape[0]))
        if mode == "lines" and size is not None:
            pose = camera_pose(h.H, size)
            if pose is not None:
                self.rig = CameraRig.from_main(h.H, pose)
                self._lines_id = lines_ref_id(h.H)
                self.mode = "lines"
                return self.mode
            log.warning("court.lines_unavailable", reason="no plausible camera explains the calibration")
        if reference is not None:
            # poses are verified against the court plane: the court plus its run-off (lines, decals, mat)
            hw, hl = WIDTH_DOUBLES / 2 + 0.9, REFERENCE_POINTS["far_left"][1] + 0.9
            floor = h.court_to_image(np.array([[-hw, hl], [hw, hl], [hw, -hl], [-hw, -hl]]))
            if self.camera.set_reference(reference, floor=floor) is None:
                log.warning("camera.untrackable", reason="reference frame has too little texture")
            else:
                self.mode = "camera"
        return self.mode

    def _learn_court_colour(self) -> None:
        if self.presence is None or not self._court_samples:
            return
        band = self.presence.learn(self._court_samples)
        log.info("court.colour", band=band.name if band else None, kept=self.presence.band.name)

    def seed_background(self, frames_bgr: list[np.ndarray]) -> None:
        if frames_bgr:
            self._court_samples = [small_hsv(f) for f in frames_bgr]
            self._learn_court_colour()
        if self.shuttle is None or not frames_bgr:
            return
        import cv2

        from bai_badminton.perception.tracknet import HEIGHT, WIDTH

        small = [
            cv2.cvtColor(cv2.resize(f, (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
            for f in frames_bgr
        ]
        self.shuttle.bg.seed(0, small)

    # ------------------------------------------------------------------ per chunk
    def process(self, chunk: DecodedChunk, in_play: bool) -> ChunkPerception:
        p = self.profile
        n = len(chunk.frames)
        shots, cut_flags = [], []
        for f in chunk.frames:
            cut_flags.append(self.cuts.update(f))
            shots.append(self.cuts.shot_id)

        # Where the camera is: the pose of every frame relative to the calibration's reference view.  A frame
        # that is not analysed (no court in view, another camera) is treated like a replay.
        scene = self._scene(chunk, cut_flags)
        if self._calibration_last_frame is None or self._calibration_last_frame != chunk.start - 1:
            self.calibration_lifecycle = CalibrationLifecycle()
        states = []
        for i, view in enumerate(scene.views):
            held = scene.held[i] if scene.held else False
            main_geometry = view == "main" and scene.polys[i] is not None
            # Background tracking without an installed floor mask cannot verify the court plane.
            camera_floor = self.camera._st is not None and self.camera._st.floor is not None
            can_verify = self.mode == "lines" or (self.mode == "camera" and camera_floor)
            verified = (
                main_geometry and can_verify and not held and scene.poses is not None and scene.poses[i] is not None
            )
            states.append(
                self.calibration_lifecycle.update(
                    verified=verified, held=main_geometry and (held or not can_verify), cut=cut_flags[i]
                )
            )
        if n:
            self._calibration_last_frame = chunk.start + n - 1
        replay = [v != "main" for v in scene.views]
        poses, polys = scene.poses, scene.polys

        rates_det = p.detector_rates.in_play if in_play else p.detector_rates.idle
        rates_pose = p.pose_rates.in_play if in_play else p.pose_rates.idle

        shuttle = [None] * n
        diagnostic_selection = getattr(self, "diagnostic_selection", DiagnosticSelection())
        diagnostic_indices = {i for i in range(n) if diagnostic_selection.includes(chunk.start + i)}
        shuttle_diagnostics = [None] * n
        diagnostics_supported = isinstance(self.shuttle, DiagnosticShuttlePort) and self.shuttle.supports_diagnostics
        if self.shuttle is not None and not all(replay):
            with timed("shuttle"):
                t0 = _now()
                choice = getattr(self, "effective_choices", {}).get("shuttle", p.shuttle)
                step = (
                    int(choice.params.get("step", self.shuttle.seq_len)) if choice is not None else self.shuttle.seq_len
                )
                from bai_badminton.perception.tracknet import HEIGHT, WIDTH

                masks = None
                if self._ref_poly is not None:
                    masks = [
                        flight_mask(
                            poly,
                            (img.shape[1], img.shape[0]),
                            (WIDTH, HEIGHT),
                            region=getattr(self, "flight_region", "bounded_upward_sweep_v1"),
                        )
                        if poly is not None and not replay[i]
                        else np.zeros((HEIGHT, WIDTH), np.uint8)
                        for i, (img, poly) in enumerate(zip(chunk.frames, polys, strict=True))
                    ]
                if diagnostic_indices and diagnostics_supported:
                    shuttle, shuttle_diagnostics = self.shuttle.detect_with_diagnostics(
                        chunk.frames,
                        shots,
                        step=step,
                        masks=masks,
                        selection=diagnostic_selection,
                        indices=diagnostic_indices,
                    )
                else:
                    shuttle = self.shuttle.detect(chunk.frames, shots, step=step, masks=masks)
                self._rate("shuttle", n, t0)

        frames: list[FramePerception] = []
        t0 = _now()
        with timed("players"):
            for i, img in enumerate(chunk.frames):
                fidx = chunk.start + i
                configure_diagnostics = getattr(self.players, "set_diagnostics", None)
                if callable(configure_diagnostics):
                    configure_diagnostics(i in diagnostic_indices and not replay[i], diagnostic_selection.top_k)
                if cut_flags[i]:
                    self.players.on_cut()
                poly = polys[i]
                if poly is not None:  # the player ROI follows the court as the camera moves
                    H_now = self._H_ref
                    if poses is not None and poses[i] is not None and H_now is not None:
                        H_now = poses[i] @ H_now
                    h_now = Homography(H_now, 0.0, 4) if H_now is not None else None
                    self.players.set_roi(CourtROI(poly.astype(np.float32), homography=h_now))
                persons = [] if replay[i] else self.players.process(fidx, img, (rates_det, rates_pose))
                racket_detector = getattr(self, "racket", None)
                # Equipment remains observable when the independent shuttle stage misses.
                if racket_detector is not None and persons and not replay[i]:
                    observed_rackets = racket_detector.detect(img, persons)
                    for person in persons:
                        person.racket = observed_rackets.get(person.track_id)
                identity_error = getattr(self.players, "last_identity_error", None)
                if identity_error is not None and not any(
                    d.stage == "player_identity" and d.reason == identity_error for d in self.degraded
                ):
                    self._degrade("player_identity", identity_error)
                reason = "Too many court tracks in some frames; player evidence was withheld."
                if (
                    not replay[i]
                    and getattr(self.players, "last_capacity_limited", False)
                    and not any(d.stage == "player_tracking" and d.reason == reason for d in self.degraded)
                ):
                    self._degrade("player_tracking", reason)
                s = shuttle[i] if not replay[i] else None
                # lines mode: every calibrated frame carries its pose (other cameras too: the court is drawn
                # there); camera mode: only analysed frames (another camera's pose is not measured)
                G = poses[i] if poses is not None and (self.mode == "lines" or not replay[i]) else None
                frames.append(
                    FramePerception(
                        frame_idx=fidx,
                        shuttle_xy=(s.x, s.y) if s is not None else None,
                        shuttle_conf=s.conf if s is not None else 0.0,
                        persons=persons,
                        replay=replay[i],
                        shot_id=shots[i],
                        cam=G,
                        cam_lost=poses is not None and G is None,
                        view=scene.views[i],
                        head=scene.heads[i],
                        court_q=scene.quality[i],
                        calibration_state=states[i],
                        pose_stride=int(rates_pose)
                        if not replay[i] and getattr(self.players, "pose", None) is not None
                        else 0,
                        detector_observed=bool(
                            not replay[i] and getattr(self.players, "last_detector_observed", False)
                        ),
                        diagnostic=FrameDiagnostic(
                            frame_idx=fidx,
                            canonical_time_sec=fidx / self.fps,
                            shot_id=shots[i],
                            view=scene.views[i],
                            calibration_state=states[i].value,
                            shuttle=shuttle_diagnostics[i],
                            acquisition_reason="view_excluded"
                            if replay[i]
                            else "provider_unavailable"
                            if self.shuttle is None
                            else "model_ran"
                            if diagnostics_supported
                            else "provider_diagnostics_unsupported",
                            provider=self.models.get("shuttle", "unavailable"),
                            players=getattr(self.players, "last_diagnostic", None)
                            if callable(configure_diagnostics)
                            else None,
                        )
                        if i in diagnostic_indices
                        else None,
                    )
                )
        self._rate("players", n, t0)
        ocr = self._read_scoreboard(chunk, replay, in_play, scene.views, scene.broadcast_replay_status)
        self.stats.frames += n
        self.stats.shuttle_frames += sum(1 for s in shuttle if s is not None)
        return ChunkPerception(
            start=chunk.start,
            end=chunk.end,
            frames=frames,
            models=dict(self.models),
            ocr=ocr,
            cam_ref=self.ref_id if poses is not None else None,
        )

    def _scene(self, chunk: DecodedChunk, cut_flags: list[bool]) -> _Scene:
        """Per-frame view, camera head, pose (reference px → frame px) and court polygon of a chunk."""
        n = len(chunk.frames)
        sc = _Scene(["main"] * n, [None] * n, [None] * n, None, [None] * n, [False] * n)
        if self.presence is None:  # court ownership is unknown: require calibration
            sc.views = ["none"] * n
            return sc
        if self.mode == "lines" and self.rig is not None and self._H_ref is not None:
            t0 = _now()
            fits = self.court.track(chunk.frames, cut_flags, chunk.start)
            self._rate("court", n, t0)
            H_inv = np.linalg.inv(self._H_ref)
            sc.poses = [None] * n
            for i, fit in enumerate(fits):
                if fit is None:
                    sc.views[i] = "none"
                    continue
                sc.held[i] = fit.method == "hold"
                head = self.rig.classify(fit)
                G = fit.H @ H_inv
                G = G / G[2, 2]
                poly = project(G, self._ref_poly) if self._ref_poly is not None else None
                sc.poses[i], sc.heads[i], sc.quality[i] = G, head, round(fit.precision, 3)
                sc.views[i] = "main" if head == 0 else "alt"
                sc.polys[i] = poly if poly is not None and np.isfinite(poly).all() else None
            return sc
        poses = self.camera.track(chunk.frames, cut_flags, chunk.start) if self.mode == "camera" else None
        sc.poses = poses
        if poses is not None:
            sc.held = list(self.camera.last_held)
        for i, f in enumerate(chunk.frames):
            if poses is None:
                sc.polys[i] = self._ref_poly
                sc.views[i] = "main" if self.presence.is_main_camera(f) else "none"
                continue
            pose = poses[i]
            poly = project(pose, self._ref_poly) if pose is not None and self._ref_poly is not None else None
            if poly is not None and not np.isfinite(poly).all():
                poly = None
            sc.polys[i] = poly
            sc.views[i] = "main" if poly is not None and self.presence.is_main_camera(f, poly) else "none"
        return sc

    def _read_scoreboard(
        self,
        chunk: DecodedChunk,
        replay: list[bool],
        in_play: bool,
        views: list[str] | None = None,
        broadcast_replay_status: list[str] | None = None,
    ) -> list[ScoreReading]:
        """Read the score bug between rallies only (it cannot change during one), on main-camera
        frames (replay graphics often hide or freeze it)."""
        if self.scoreboard is None:
            return []
        policy = getattr(self, "ocr_scene_policy", "main_camera")
        views = views if views is not None else ["unknown" if excluded else "main" for excluded in replay]
        statuses = broadcast_replay_status or ["unknown"] * len(chunk.frames)
        if len(views) != len(chunk.frames) or len(statuses) != len(chunk.frames):
            raise ValueError("scoreboard scene context must cover the canonical chunk")
        out = []
        t0 = _now()
        with timed("ocr"):
            for i, img in enumerate(chunk.frames):
                if policy == "main_camera" and replay[i]:
                    continue
                calls = self.scoreboard.calls
                r = self.scoreboard.maybe_read(chunk.start + i, img)
                self.stats.ocr_calls += self.scoreboard.calls - calls
                if r is not None:
                    status = statuses[i]
                    if r.context is not None:
                        if r.context.actual_replay_status == "replay":
                            status = "replay"
                        elif status == "unknown":
                            status = r.context.actual_replay_status
                    out.append(
                        replace(
                            r,
                            context=ScoreObservationContext(
                                view=views[i],
                                analysis_excluded=bool(replay[i]),
                                actual_replay_status=status,
                                acquisition_policy=policy,
                            ),
                        )
                    )
        self._rate("ocr", len(chunk.frames), t0)
        self.stats.ocr_readings += len(out)
        return out

    def _rate(self, stage: str, n: int, t0: float) -> None:
        dt = _now() - t0
        self.stats.seconds[stage] = self.stats.seconds.get(stage, 0.0) + dt
        if dt > 0:
            INFERENCE_FPS.labels(model=stage).set(n / dt)


def _now() -> float:
    import time

    return time.perf_counter()
