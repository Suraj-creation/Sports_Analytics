"""Badminton perception for one decoded chunk: cuts → court gate → shuttle → players → pose.

Model loading is profile-driven and *degrades gracefully*: a model whose weights are missing or
fail to load is disabled with a recorded reason (surfaced as a ``degraded`` event), and the rest
of the pipeline keeps running — e.g. without the shuttle model the platform still tracks players
and pose; without the detector it still tracks the shuttle.

Rates: detector / pose strides depend on the rally state reported by the match engine
(``in_play`` vs ``idle``) using the profile's ``Rates``; during replays (court gate failed)
perception is skipped entirely.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from bai_badminton.court import REFERENCE_POINTS, Homography
from bai_badminton.perception.players import CourtROI, PlayerDetector, PlayerPerception, PoseEstimator
from bai_badminton.perception.scene import CourtPresence, CutDetector
from bai_badminton.perception_types import ChunkPerception, FramePerception
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
class PerceptionStats:
    frames: int = 0
    shuttle_frames: int = 0
    det_calls: int = 0
    pose_calls: int = 0
    seconds: dict[str, float] = field(default_factory=dict)


class BadmintonPerception:
    def __init__(self, profile: Profile, registry: ModelRegistry, fps: float, models_dir: Path) -> None:
        self.profile = profile
        self.fps = fps
        self.degraded: list[Degradation] = []
        self.models: dict[str, str] = {}
        self.cuts = CutDetector()
        self.presence: CourtPresence | None = None
        self.stats = PerceptionStats()
        cache = engine_cache_dir(models_dir)
        self.shuttle = self._load_shuttle(profile.shuttle, registry, cache)
        det = self._load_detector(profile.player_detector, registry, cache)
        pose = self._load_pose(profile.pose, registry, cache)
        self.players = PlayerPerception(
            det, pose, fps, det_stride=profile.detector_rates.in_play, pose_stride=profile.pose_rates.in_play
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

    def _degrade(self, stage: str, reason: str) -> None:
        log.warning("perception.degraded", stage=stage, reason=reason)
        self.degraded.append(Degradation(stage, reason))

    # ------------------------------------------------------------------ calibration
    def set_calibration(self, h: Homography) -> None:
        names = ("far_left", "far_right", "near_right", "near_left")
        poly = h.court_to_image(np.array([REFERENCE_POINTS[n] for n in names])).astype(np.float32)
        self.players.set_roi(CourtROI(poly))
        self.presence = CourtPresence(poly)

    def seed_background(self, frames_bgr: list[np.ndarray]) -> None:
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
        shots, replay = [], []
        for f in chunk.frames:
            if self.cuts.update(f):
                self.players.on_cut()
            shots.append(self.cuts.shot_id)
            replay.append(self.presence is not None and not self.presence.is_main_camera(f))

        rates_det = p.detector_rates.in_play if in_play else p.detector_rates.idle
        rates_pose = p.pose_rates.in_play if in_play else p.pose_rates.idle

        shuttle = [None] * n
        if self.shuttle is not None and not all(replay):
            with timed("shuttle"):
                t0 = _now()
                step = int(p.shuttle.params.get("step", self.shuttle.seq_len))
                shuttle = self.shuttle.detect(chunk.frames, shots, step=step)
                self._rate("shuttle", n, t0)

        frames: list[FramePerception] = []
        t0 = _now()
        with timed("players"):
            for i, img in enumerate(chunk.frames):
                fidx = chunk.start + i
                persons = [] if replay[i] else self.players.process(fidx, img, (rates_det, rates_pose))
                s = shuttle[i] if not replay[i] else None
                frames.append(
                    FramePerception(
                        frame_idx=fidx,
                        shuttle_xy=(s.x, s.y) if s is not None else None,
                        shuttle_conf=s.conf if s is not None else 0.0,
                        persons=persons,
                        replay=replay[i],
                        shot_id=shots[i],
                    )
                )
        self._rate("players", n, t0)
        self.stats.frames += n
        self.stats.shuttle_frames += sum(1 for s in shuttle if s is not None)
        return ChunkPerception(start=chunk.start, end=chunk.end, frames=frames, models=dict(self.models))

    def _rate(self, stage: str, n: int, t0: float) -> None:
        dt = _now() - t0
        self.stats.seconds[stage] = self.stats.seconds.get(stage, 0.0) + dt
        if dt > 0:
            INFERENCE_FPS.labels(model=stage).set(n / dt)


def _now() -> float:
    import time

    return time.perf_counter()
