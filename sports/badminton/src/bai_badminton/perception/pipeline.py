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

import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from bai_badminton.court import REFERENCE_POINTS, WIDTH_DOUBLES, Homography
from bai_badminton.perception.calibration_state import CalibrationLifecycle
from bai_badminton.perception.camera import CameraTracker, project
from bai_badminton.perception.court_lines import CameraRig, CourtTracker, camera_pose
from bai_badminton.perception.isolation import flight_mask
from bai_badminton.perception.players import CourtROI, PlayerDetector, PlayerPerception, PoseEstimator
from bai_badminton.perception.scene import CourtPresence, CutDetector, small_hsv
from bai_badminton.perception.scoreboard import ScoreboardReader
from bai_badminton.perception_types import ChunkPerception, FramePerception, ScoreReading
from bai_engine.config import ModelChoice, Profile
from bai_engine.decode import DecodedChunk
from bai_engine.obs import INFERENCE_FPS, get_logger, timed
from bai_engine.runtime.device import engine_cache_dir, ort_providers
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
    ) -> None:
        if match_format not in ("singles", "doubles"):
            raise ValueError("unknown match format")
        self.match_format = match_format
        self.profile = profile
        self.fps = fps
        self.frame_size = frame_size
        self.degraded: list[Degradation] = []
        self.models: dict[str, str] = {}
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
        self.shuttle = self._load_shuttle(profile.shuttle, registry, cache)
        det = self._load_detector(profile.player_detector, registry, cache)
        pose = self._load_pose(profile.pose, registry, cache)
        self.scoreboard = self._load_ocr(profile.ocr, registry, fps)
        self.players = PlayerPerception(
            det, pose, fps, det_stride=profile.detector_rates.in_play, pose_stride=profile.pose_rates.in_play,
            max_players=4 if match_format == "doubles" else 2,
        )

    # ------------------------------------------------------------------ loading
    def _providers(self, choice: ModelChoice, cache: Path) -> list[Any]:
        return ort_providers(choice.backend, engine_cache=cache / choice.model, fp16=choice.precision == "fp16")

    def _load_shuttle(self, c: ModelChoice, reg: ModelRegistry, cache: Path):  # type: ignore[no-untyped-def]
        if c.model == "none":
            return None
        try:
            from bai_badminton.perception.tracknet import TrackNetV3

            m = TrackNetV3(
                reg.path(c.model),
                backend=c.backend,
                threshold=float(c.params.get("threshold", 0.5)),
                onnx_dir=cache / c.model,
                providers=self._providers(c, cache),
                batch=c.batch,
            )
            self.models["shuttle"] = reg.get(c.model).ref
            return m
        except (ModelError, OSError, ValueError, ImportError, RuntimeError) as e:
            self._degrade("shuttle", f"{c.model}: {e}")
            return None

    def _load_detector(self, c: ModelChoice, reg: ModelRegistry, cache: Path) -> PlayerDetector | None:
        if c.model == "none":
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
            self.models["player_detector"] = spec.ref
            return d
        except (ModelError, OSError, ValueError, ImportError, RuntimeError) as e:
            self._degrade("player_detector", f"{c.model}: {e}")
            return None

    def _load_pose(self, c: ModelChoice, reg: ModelRegistry, cache: Path) -> PoseEstimator | None:
        if c.model == "none":
            return None
        try:
            spec = reg.get(c.model)
            size = c.input_size or (spec.input.get("width", 192), spec.input.get("height", 256))
            p = PoseEstimator(reg.path(c.model), (int(size[0]), int(size[1])), self._providers(c, cache))
            self.models["pose"] = spec.ref
            return p
        except (ModelError, OSError, ValueError, ImportError, RuntimeError) as e:
            self._degrade("pose", f"{c.model}: {e}")
            return None

    def _load_ocr(self, c: ModelChoice | None, reg: ModelRegistry, fps: float) -> ScoreboardReader | None:
        if c is None or c.model == "none":
            return None
        try:
            r = ScoreboardReader.load(every=max(1, int(round(self.profile.ocr_every_s * fps))))
            self.models["ocr"] = reg.get(c.model).ref
            return r
        except (ModelError, OSError, ValueError, ImportError, RuntimeError) as e:
            self._degrade("ocr", f"{c.model}: {e}")
            return None

    def _degrade(self, stage: str, reason: str) -> None:
        log.warning("perception.degraded", stage=stage, reason=reason)
        self.degraded.append(Degradation(stage, reason))

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
        if self.shuttle is not None and not all(replay):
            with timed("shuttle"):
                t0 = _now()
                step = int(p.shuttle.params.get("step", self.shuttle.seq_len))
                from bai_badminton.perception.tracknet import HEIGHT, WIDTH

                masks = None
                if self._ref_poly is not None:
                    masks = [
                        flight_mask(poly, (img.shape[1], img.shape[0]), (WIDTH, HEIGHT))
                        if poly is not None and not replay[i]
                        else np.zeros((HEIGHT, WIDTH), np.uint8)
                        for i, (img, poly) in enumerate(zip(chunk.frames, polys, strict=True))
                    ]
                shuttle = self.shuttle.detect(chunk.frames, shots, step=step, masks=masks)
                self._rate("shuttle", n, t0)

        frames: list[FramePerception] = []
        t0 = _now()
        with timed("players"):
            for i, img in enumerate(chunk.frames):
                fidx = chunk.start + i
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
                reason = "Too many court tracks in some frames; player evidence was withheld."
                if (not replay[i] and getattr(self.players, "last_capacity_limited", False)
                    and not any(d.stage == "player_tracking" and d.reason == reason for d in self.degraded)):
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
                        detector_observed=bool(
                            not replay[i] and getattr(self.players, "last_detector_observed", False)
                        ),
                    )
                )
        self._rate("players", n, t0)
        ocr = self._read_scoreboard(chunk, replay, in_play)
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

    def _read_scoreboard(self, chunk: DecodedChunk, replay: list[bool], in_play: bool) -> list[ScoreReading]:
        """Read the score bug between rallies only (it cannot change during one), on main-camera
        frames (replay graphics often hide or freeze it)."""
        if self.scoreboard is None or in_play:
            return []
        out = []
        t0 = _now()
        with timed("ocr"):
            for i, img in enumerate(chunk.frames):
                if replay[i]:
                    continue
                calls = self.scoreboard.calls
                r = self.scoreboard.maybe_read(chunk.start + i, img)
                self.stats.ocr_calls += self.scoreboard.calls - calls
                if r is not None:
                    out.append(r)
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
