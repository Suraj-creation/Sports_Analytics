"""Badminton sport plugin — wires perception, the match engine and calibration into the platform."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from typing import Any

import cv2
import msgpack
import numpy as np

from bai_badminton.components import BASELINE_IMPLEMENTATIONS as DOMAIN_BASELINES
from bai_badminton.components import CONTRACT_DETAILS, DomainContext, register_domain_components
from bai_badminton.court import REFERENCE_POINTS, WIDTH_DOUBLES, Homography, fit_homography
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, box_tuple, camera_sample, keypoint_rows
from bai_badminton.events.rally_fsm import RallyState
from bai_badminton.format_understanding import METHOD as FORMAT_METHOD
from bai_badminton.format_understanding import (
    FormatContext,
    FormatDecision,
    FormatObservation,
    FormatPerson,
    register_format_components,
)
from bai_badminton.identity_review import TRACKER_IDENTITY_EVIDENCE_TYPES
from bai_badminton.participant_geometry import GeometryBracketPolicy
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.components import register_perception_components
from bai_badminton.perception.court_lines import METHOD as LINES_METHOD
from bai_badminton.perception.court_lines import CourtFit, camera_pose, choose_main, detect_court, refine_court
from bai_badminton.perception.isolation import is_fixed_camera
from bai_badminton.perception.pipeline import BadmintonPerception, lines_ref_id
from bai_badminton.perception_types import (
    ChunkPerception,
    FramePerception,
    PersonObs,
    RacketObservation,
    ScoreObservationContext,
    ScoreReading,
)
from bai_badminton.rules import SCORE_REVIEW_EVENT_TYPES
from bai_badminton.rules.bwf import MatchConfig
from bai_engine.components import ComponentRegistry
from bai_engine.config import ModelChoice, Profile, get_settings
from bai_engine.decode import DecodedChunk
from bai_engine.obs import get_logger
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import Event, EventStatus, Provenance, Session, TrackObject, TrackSample
from bai_engine.sport import EmitFn
from bai_engine.store import EventStore, TrackStore

log = get_logger(__name__)
AUTO_CALIBRATION_MIN_SCORE = 0.6
REF_FILE = "camera_ref.png"  # the frame the calibration was made on (lossless: its id is a content hash)
CODEC_VERSION = 17  # explicit source-board context and unknown physical identities
MAX_ADJUST = 0.03  # a human calibration the court lines move by more than this (× frame width) is kept as is


def _corner_shift(h_a: np.ndarray, h_b: np.ndarray) -> float:
    """Largest image distance (px) between two court→image homographies over the court's corners and net."""
    hw, hl = WIDTH_DOUBLES / 2, REFERENCE_POINTS["far_left"][1]
    pts = np.array([[-hw, hl], [hw, hl], [hw, -hl], [-hw, -hl], [-hw, 0.0], [hw, 0.0]], np.float64).reshape(-1, 1, 2)
    a, b = cv2.perspectiveTransform(pts, h_a), cv2.perspectiveTransform(pts, h_b)
    d = np.linalg.norm((a - b).reshape(-1, 2), axis=1)
    return float(d.max()) if np.isfinite(d).all() else float("inf")


def _fit_record(fit: CourtFit) -> dict[str, Any]:
    """The quality/camera part of a calibration record (``calibration`` event payload)."""
    return {
        "quality": {
            "precision": round(fit.precision, 4),
            "support": round(fit.support, 3),
            "lines": list(fit.lines),
            "area": round(fit.area, 4),
            "rms_px": round(fit.rms_px, 3),
        },
        "camera": fit.pose.to_json() if fit.pose else None,
        "ambiguous_end": fit.ambiguous_end,
    }


class StaleCacheError(ValueError):
    """A cached perception chunk that no longer matches the calibration (the runner recomputes it)."""


class BadmintonSession:
    def __init__(
        self,
        session: Session,
        store: EventStore,
        profile: Profile,
        registry: ModelRegistry,
        emit: EmitFn,
        *,
        component_registry: ComponentRegistry | None = None,
        pipeline_declaration: dict[str, Any] | None = None,
    ) -> None:
        assert session.media is not None, "session media must be known before analysis starts"
        self.session = session
        self._pipeline_declaration = loads(
            dumps(
                pipeline_declaration if pipeline_declaration is not None else BadmintonPlugin.describe_pipeline(),
                allow_nan=False,
            )
        )
        self.store = store
        self._analytics_token: tuple[Any, ...] | None = None
        self._analytics_fold: Any = None
        m = session.media
        fps = float(m.fps)
        names = {p.player_id: p.name for p in session.players}
        contact_choice = profile.components.get("contact", profile.contact)
        geometry_configuration = (
            contact_choice.params.get("participant_geometry") if contact_choice is not None else None
        )
        geometry_policy = None
        if geometry_configuration is not None:
            try:
                if not isinstance(geometry_configuration, dict):
                    raise ValueError("a configuration object is required")
                geometry_policy = GeometryBracketPolicy(**geometry_configuration)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError("invalid contact participant_geometry configuration") from exc
        # Format controls the rally in/out court geometry. The rules engine still
        # exposes two score-side slots and does not implement doubles partner
        # service rotation; the roster does not imply individual scoring.
        configured_format = session.roster.match_format if session.roster else None
        discipline = configured_format or "singles"  # rules placeholder is gated until format is known
        if component_registry is None:
            component_registry = ComponentRegistry()
            register_perception_components(component_registry)
            register_format_components(component_registry)
            register_domain_components(component_registry)
        self.component_registry = component_registry
        self._format_choice = profile.components.get(
            "format",
            ModelChoice(
                model="none",
                backend="none",
                implementation="sustained-court-v1",
            ),
        ).model_copy(deep=True)
        try:
            self._format_handle = component_registry.create(
                "format",
                self._format_choice.implementation or "sustained-court-v1",
                context=FormatContext(fps=fps, configured_format=configured_format),
                configuration=self._format_choice.model_dump(mode="json"),
                match_format=configured_format or "unknown",
                context_identity={"source": session.source.sha256, "fps": fps},
            )
            self.format_understanding = self._format_handle.instance
            self._domain_component_handles = {}
            self._domain_metadata = {}
            self._domain_effective_choices = {}
            domain_context = DomainContext(fps, m.width, m.height, MatchConfig(discipline=discipline), registry)
            for kind, implementation in DOMAIN_BASELINES.items():
                legacy = getattr(profile, kind, None)
                params = legacy.params if legacy is not None and kind == "contact" else {}
                choice = profile.components.get(
                    kind,
                    ModelChoice(
                        model="none",
                        backend="none",
                        implementation=implementation,
                        params=params,
                    ),
                ).model_copy(deep=True)
                self._domain_effective_choices[kind] = choice
                handle = component_registry.create(
                    kind,
                    choice.implementation or implementation,
                    context=domain_context,
                    configuration=choice.model_dump(mode="json"),
                    match_format=configured_format or "unknown",
                    context_identity={
                        "source": session.source.sha256,
                        "fps": fps,
                        "frame_size": [m.width, m.height],
                        "profile": profile.name,
                    },
                )
                self._domain_component_handles[kind] = handle
                if handle.contract.stateful and not all(
                    callable(getattr(handle.instance, method, None)) for method in ("checkpoint", "restore")
                ):
                    raise ValueError(f"Stateful semantic {kind} provider requires checkpoint and restore")
                model = getattr(handle.instance, "model_ref", None) or getattr(handle.instance, "name", None)
                runtime = getattr(handle.instance, "runtime", {})
                actual = {"model": model, "runtime": runtime}
                fingerprint = sha256(
                    dumps({"construction": handle.fingerprint, **actual}, allow_nan=False, sort_keys=True).encode()
                ).hexdigest()
                self._domain_metadata[kind] = loads(
                    dumps(
                        {
                            "contract": handle.contract.describe(),
                            "configuration": choice.model_dump(mode="json"),
                            "fingerprint": fingerprint,
                            **actual,
                            "baseline_evidence_contract": CONTRACT_DETAILS[kind]
                            if handle.contract.implementation == implementation
                            else None,
                        },
                        allow_nan=False,
                    )
                )
            self.engine = BadmintonMatchEngine(
                session.session_id,
                EngineConfig(
                    fps=fps,
                    frame_width=m.width,
                    frame_height=m.height,
                    profile=profile.name,
                    match=MatchConfig(discipline=discipline),
                    match_format_known=configured_format is not None,
                    participant_geometry_policy=geometry_policy,
                ),
                store,
                emit=emit,
                player_names=names,
                contact_inference=self._domain_component_handles["contact"].instance,
                stroke_classifier=self._domain_component_handles["stroke"].instance,
                activity_tracker=self._domain_component_handles["activity"].instance,
                rally_segmenter=self._domain_component_handles["rally"].instance,
                outcome_inference=self._domain_component_handles["outcome"].instance,
                score_rules=self._domain_component_handles["scoring"].instance,
                analytics=self._domain_component_handles["analytics"].instance,
                identity_provider=self._domain_component_handles["identity"].instance,
                transactional_components={
                    kind: handle.instance
                    for kind, handle in self._domain_component_handles.items()
                    if handle.contract.stateful
                },
            )
            self.perception = BadmintonPerception(
                profile,
                registry,
                fps,
                get_settings().models_dir,
                frame_size=(m.width, m.height),
                match_format=configured_format or "unknown",
                component_registry=component_registry,
                context_identity={"source": session.source.sha256},
            )
            if "stroke" not in profile.components and profile.stroke.model not in ("none", "stroke_rules_v0"):
                self.perception._degrade(
                    "stroke_legacy_request",
                    f"Requested artifact {profile.stroke.model} has no active runtime provider; "
                    "The declared stroke-rules-v0 provider is executing. "
                    "Select components.stroke explicitly to replace it.",
                )
            self._format_epoch = 0
            self._format_last_shot_id: int | None = None
            self._applied_format = configured_format
            self.calibration: Homography | None = None
            self._fixed_camera: bool | None = None  # None: legacy or not yet sampled
            self._emit = emit
            self._frame_at: Callable[[int], np.ndarray] | None = None
            self._ref_dir: Path | None = None
            self._restored_cam_ref: int | None = None  # reference view id the restored calibration was tracked against
            self._restore_calibration()
        except BaseException:
            try:
                self.close()
            except Exception as cleanup_error:
                log.warning("pipeline.construction_cleanup_failed", error=str(cleanup_error))
            raise

    # ------------------------------------------------------------------ frame access (camera tracking)
    def attach_frames(self, frame_at: Callable[[int], np.ndarray], ref_dir: Path) -> None:
        """Give the session access to decoded frames (a human calibration names the frame it was made on)
        and a directory for the reference frame, which makes camera tracking survive a restart."""
        self._frame_at, self._ref_dir = frame_at, ref_dir
        if (
            self.calibration is not None
            and self._restored_cam_ref is not None
            and self.perception.mode != "lines"  # court-line tracking needs no reference image
            and not self.perception.camera.ready
        ):
            ref = self._load_ref()  # a re-analysis / restart: resume tracking against the saved reference
            if ref is not None:
                self.perception.set_calibration(self.calibration, ref)
                if self.perception.camera.ref_id == self._restored_cam_ref:
                    self.engine.set_camera_reference(self._restored_cam_ref)
                else:  # not the frame the calibration was tracked against: do not track
                    log.warning(
                        "camera.reference_mismatch", saved=self.perception.camera.ref_id, wanted=self._restored_cam_ref
                    )
                    self.perception.set_calibration(self.calibration)

    def _save_ref(self, img: np.ndarray) -> None:
        if self._ref_dir is not None:
            self._ref_dir.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(self._ref_dir / REF_FILE), img)

    def _load_ref(self) -> np.ndarray | None:
        f = None if self._ref_dir is None else self._ref_dir / REF_FILE
        return cv2.imread(str(f)) if f is not None and f.exists() else None

    # ------------------------------------------------------------------ calibration
    def _restore_calibration(self) -> None:
        """Re-apply the latest stored calibration (session restart / re-analysis)."""
        cal = self.store.query(types=["calibration"])
        if cal:
            pay = cal[-1].payload
            h = Homography.from_json(pay)
            self._restored_cam_ref = pay.get("cam_ref")
            net = pay.get("net_top")
            net_top = ((net[0][0], net[0][1]), (net[1][0], net[1][1])) if net else None
            # court-line calibrations resume at once; background tracking resumes in attach_frames (needs the
            # reference image)
            self._apply_calibration(
                h,
                emit=False,
                net_top=net_top,
                mode="lines" if pay.get("mode") == "lines" else "static",
                record={"fixed_camera": pay.get("fixed_camera")},
            )

    def _apply_calibration(
        self,
        h: Homography,
        emit: bool = True,
        net_top: tuple[tuple[float, float], tuple[float, float]] | None = None,
        source: str = "auto",
        reference: np.ndarray | None = None,
        ref_frame: int | None = None,
        mode: str | None = None,
        fit: CourtFit | None = None,
        record: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Install a calibration.  ``reference`` is the frame ``h`` was fitted on.  ``mode`` (lines / static)
        forces the geometry mode; by default a calibration whose frame's painted lines confirm it is followed
        by its lines in every frame (refined onto them), otherwise the camera is tracked by its background
        from ``reference``.  Returns the calibration record's extra fields."""
        self._format_epoch = getattr(self, "_format_epoch", 0) + 1
        extra: dict[str, Any] = dict(record or {})
        extra.setdefault("fixed_camera", self._fixed_camera)
        self._fixed_camera = extra["fixed_camera"]
        size = (self.session.media.width, self.session.media.height) if self.session.media else None
        if mode is None and reference is not None:
            fit = refine_court(reference, h.H)
            shift = _corner_shift(fit.H, h.H) if fit is not None else float("inf")
            if fit is not None and fit.ok and fit.pose is not None and shift <= MAX_ADJUST * reference.shape[1]:
                extra["adjusted_px"] = round(shift, 2)  # how far the lines moved the clicked calibration
                h = Homography(fit.H, fit.rms_px, h.n_points)
                mode = "lines"
            else:
                extra["lines_check"] = (
                    "no court lines found" if fit is None or not fit.ok else f"lines disagree by {shift:.0f} px"
                )
        if fit is not None and mode == "lines":
            extra.update(_fit_record(fit))
        self.calibration = h
        used = self.perception.set_calibration(h, reference, "lines" if mode == "lines" else None)
        if used == "lines" and extra.get("fixed_camera"):
            self.perception.court.lock(h.H)
        cam_ref = self.perception.ref_id
        if used == "camera" and reference is not None:
            self._save_ref(reference)
        elif self._ref_dir is not None:  # a reference left by an older calibration must not be reused
            (self._ref_dir / REF_FILE).unlink(missing_ok=True)
        if net_top is None and used == "lines" and size is not None:
            pose = camera_pose(h.H, size)  # the net posts' tops, from the camera the lines define
            net_top = pose.net_top() if pose is not None else None
        extra.update(
            mode=used,
            method=(LINES_METHOD if source == "auto" else f"human+{LINES_METHOD}") if used == "lines" else source,
            validity={"lines": "per_frame", "camera": "tracked_from_reference", "static": "whole_video"}[used],
            calibration_id=f"{cam_ref:08x}" if cam_ref is not None else None,
            frame_size=list(size) if size else None,
            net_top=[list(net_top[0]), list(net_top[1])] if net_top else None,
        )
        self.engine.set_calibration(
            0,
            h,
            *(net_top or (None, None)),
            emit=emit,
            source=source,
            cam_ref=cam_ref,
            ref_frame=ref_frame,
            extra=extra,
        )
        return extra

    def seed(self, keyframes: list[Any]) -> None:
        self.perception.seed_background(keyframes)
        if not keyframes:
            return
        if self._fixed_camera is None:
            self._fixed_camera = is_fixed_camera(keyframes)
            if self.calibration is not None and self.perception.mode == "lines":
                # Existing line calibrations predate camera ownership. Keep the
                # chosen court, classify the camera, and persist the decision.
                records = self.store.query(types=["calibration"])
                pay = records[-1].payload if records else {}
                net = pay.get("net_top")
                self._apply_calibration(
                    self.calibration,
                    mode="lines",
                    source=pay.get("source", "auto"),
                    ref_frame=pay.get("ref_frame"),
                    net_top=((net[0][0], net[0][1]), (net[1][0], net[1][1])) if net else None,
                    record={"fixed_camera": self._fixed_camera, "isolation_version": 1},
                )
        if self.calibration is not None and self.perception.mode != "lines" and self._upgrade_legacy(keyframes):
            return
        if self.calibration is not None:
            return
        if self._auto_calibrate(keyframes):
            return
        # A shared mat can include several courts: its outline is not a valid
        # substitute for one court's painted landmarks.
        self.perception._degrade("court", "Court not verified; select court landmarks before analysis")

    def _upgrade_legacy(self, keyframes: list[np.ndarray]) -> bool:
        """A new analysis restored a calibration made before court-line tracking (one homography for one
        camera pose).  A hand-placed one is refined onto the painted lines of its own frame when they confirm
        it (and kept as it was otherwise); an automatic one (the mat outline) is replaced by court-line
        detection when that finds the court.  Returns whether a calibration is now installed."""
        cal = self.store.query(types=["calibration"])
        if not cal or self.calibration is None:
            return False
        pay = cal[-1].payload
        if pay.get("source") != "human":
            return self._auto_calibrate(keyframes)
        ref_frame = pay.get("ref_frame")
        img = None
        if ref_frame is not None and self._frame_at is not None:
            try:
                img = self._frame_at(int(ref_frame))
            except (OSError, ValueError, RuntimeError, IndexError):
                img = None
        if img is None:
            img = self._load_ref()
        if img is None:
            return True  # nothing to check it against: keep it as it was restored
        net = pay.get("net_top")
        net_top = ((net[0][0], net[0][1]), (net[1][0], net[1][1])) if net else None
        self._apply_calibration(self.calibration, net_top=net_top, source="human", reference=img, ref_frame=ref_frame)
        log.info("calibration.upgraded", mode=self.perception.mode)
        return True

    def _auto_calibrate(self, frames: list[np.ndarray], ref_frames: list[int] | None = None) -> bool:
        """Calibrate from the painted lines of sampled frames: the camera seen most often becomes the main
        camera, its widest view the reference.  Returns whether a court was found."""
        from concurrent.futures import ThreadPoolExecutor

        def one(img: np.ndarray) -> CourtFit | None:
            try:
                return detect_court(img)
            except cv2.error as e:  # a corrupt frame must not stop the analysis
                log.warning("calibration.detect_failed", error=str(e))
                return None

        with ThreadPoolExecutor(max_workers=4) as pool:  # OpenCV releases the GIL
            fits = list(pool.map(one, frames))
        found = [(i, f) for i, f in enumerate(fits) if f is not None and f.ok]
        main = choose_main([f for _, f in found])
        if main is None:
            log.info("calibration.lines_not_found", frames=len(frames))
            return False
        i = next(i for i, f in found if f is main)
        extra = {"coverage": round(len(found) / len(frames), 3), "sampled_frames": len(frames)}
        # Infer a fixed installation from the background, not competing court fits.
        extra["fixed_camera"] = is_fixed_camera(frames)
        extra["isolation_version"] = 1
        self._apply_calibration(
            Homography(main.H, main.rms_px, sum(main.lines)),
            reference=frames[i],
            source="auto",
            mode="lines",
            fit=main,
            ref_frame=None if ref_frames is None else ref_frames[i],
            record=extra,
        )
        log.info(
            "calibration.auto",
            method=LINES_METHOD,
            precision=round(main.precision, 3),
            lines=main.lines,
            found=f"{len(found)}/{len(frames)}",
        )
        return True

    # ------------------------------------------------------------------ perception / temporal
    def perceive(self, chunk: DecodedChunk) -> ChunkPerception:
        return self.perception.process(chunk, in_play=self.in_play)

    def _format_observation(self, fp: FramePerception) -> FormatObservation:
        """Fresh feet in the selected ground plane, before named-player mapping."""
        people: list[FormatPerson] = []
        full_court = False
        valid = self.calibration is not None and fp.calibration_state is CalibrationState.VALID
        valid = valid and fp.scene == "main" and not fp.cam_lost
        if valid:
            matrix = self.calibration.H
            if fp.cam is not None:
                matrix = np.asarray(fp.cam) @ matrix
            try:
                h = Homography(np.asarray(matrix, dtype=float), 0.0, 4)
                if not np.isfinite(matrix).all() or np.linalg.cond(matrix) >= 1e12:
                    raise ValueError("invalid format ground-plane transform")
                corners = h.court_to_image(
                    np.array([REFERENCE_POINTS[name] for name in ("far_left", "far_right", "near_right", "near_left")])
                )
                media = self.session.media
                full_court = bool(
                    media is not None
                    and np.isfinite(corners).all()
                    and (corners[:, 0] >= 0).all()
                    and (corners[:, 0] < media.width).all()
                    and (corners[:, 1] >= 0).all()
                    and (corners[:, 1] < media.height).all()
                )
                for person in fp.persons:
                    box = np.asarray(person.bbox, dtype=float)
                    if person.detector_matched is not True or box.shape != (4,) or not np.isfinite(box).all():
                        continue
                    feet = h.image_to_court(np.array([[(box[0] + box[2]) / 2, box[3]]]))[0]
                    people.append(FormatPerson(str(person.track_id), tuple(float(value) for value in feet), True))
            except (ValueError, np.linalg.LinAlgError):
                valid = False
                people = []
        cut = self._format_last_shot_id is not None and fp.shot_id != self._format_last_shot_id
        self._format_last_shot_id = fp.shot_id
        return FormatObservation(
            frame_idx=fp.frame_idx,
            persons=tuple(people),
            detector_observed=fp.detector_observed,
            main_view=fp.scene == "main",
            geometry_valid=bool(valid),
            full_court_visible=full_court,
            epoch=str(self._format_epoch),
            cut=cut,
        )

    @staticmethod
    def _slice_perception(perception: ChunkPerception, start: int, end: int) -> ChunkPerception:
        return ChunkPerception(
            start,
            end,
            perception.frames[start - perception.start : end - perception.start + 1],
            models=dict(perception.models),
            ocr=[reading for reading in perception.ocr if start <= reading.frame_idx <= end],
            cam_ref=perception.cam_ref,
        )

    def _apply_format_decision(self, decision: FormatDecision, frame: int) -> None:
        selected = None if decision.match_format == "unknown" else decision.match_format
        handles = {**self.perception.component_handles, **self._domain_component_handles}
        for kind, handle in handles.items():
            if decision.match_format not in handle.contract.supported_formats:
                self.perception._degrade(kind, f"Selected provider does not support inferred {decision.match_format}")
                selected = None
        self.engine.set_match_format(selected, frame, Provenance(model=FORMAT_METHOD), decision=decision.to_public())
        self._applied_format = selected
        self.perception.match_format = selected or "unknown"
        # Inferred singles must still observe four people to support an upgrade.
        configured = self.session.roster.match_format if self.session.roster else None
        self.perception.players.max_players = 2 if configured == "singles" else 4
        self.perception.players.on_cut()

    def ingest(self, perception: ChunkPerception) -> None:
        boundaries: list[tuple[int, FormatDecision]] = []
        pending = self._applied_format
        for frame in perception.frames:
            decision = self.format_understanding.observe(self._format_observation(frame))
            selected = None if decision.match_format == "unknown" else decision.match_format
            if selected != pending:
                boundaries.append((frame.frame_idx, decision))
                pending = selected
        start = perception.start
        for boundary, decision in boundaries:
            if start < boundary:
                self.engine.ingest(self._slice_perception(perception, start, boundary - 1))
            self._apply_format_decision(decision, boundary)
            start = boundary
        self.engine.ingest(self._slice_perception(perception, start, perception.end))

    def flush(self) -> None:
        self.engine.flush()

    def close(self) -> None:
        """Close session-owned providers, leaving repository-owned stores open."""
        if getattr(self, "_closed", False):
            return
        self._closed = True
        failure: Exception | None = None
        resources = (
            getattr(self, "engine", None),
            *getattr(self, "_domain_component_handles", {}).values(),
            getattr(self, "_format_handle", None),
            getattr(self, "perception", None),
        )
        for resource in resources:
            close = getattr(resource, "close", None)
            if callable(close):
                try:
                    close()
                except Exception as exc:
                    failure = failure or exc
        if failure is not None:
            raise failure

    def drain_tracks(self) -> list[TrackSample]:
        return self.engine.drain_tracks()

    def tracks_from_perception(self, p: ChunkPerception) -> list[TrackSample]:
        out: list[TrackSample] = []
        for fp in p.frames:
            out.append(
                TrackSample(
                    frame_idx=fp.frame_idx,
                    obj=TrackObject.SHUTTLE,
                    x=fp.shuttle_xy[0] if fp.shuttle_xy else None,
                    y=fp.shuttle_xy[1] if fp.shuttle_xy else None,
                    visible=fp.shuttle_xy is not None,
                    conf=fp.shuttle_conf,
                )
            )
            if p.cam_ref is not None and p.cam_ref == self.perception.ref_id:
                out.append(camera_sample(fp))
            # A seek preview is out of chronological order; preserve visual
            # observations without claiming a match participant association.
            for person in fp.persons:
                out.append(
                    TrackSample(
                        frame_idx=fp.frame_idx,
                        obj=TrackObject.PLAYER,
                        track_id=person.track_id,
                        player_id=None,
                        x=float((person.bbox[0] + person.bbox[2]) / 2),
                        y=float(person.bbox[3]),
                        bbox=box_tuple(person.bbox),
                        keypoints=keypoint_rows(person.kps),
                        conf=person.conf,
                    )
                )
        return out

    @property
    def in_play(self) -> bool:
        return self.engine.fsm.state is not RallyState.IDLE

    # ------------------------------------------------------------------ restart / re-analysis
    def restore(self, last_frame: int) -> int:
        """Re-attach to a finished analysis from the stored log (no perception, no re-emission)."""
        return self.engine.restore_from_log(last_frame)

    def carry_over(self, events: list[Event]) -> int:
        """Re-apply human corrections from an earlier analysis of this video (matched by frames)."""
        return self.engine.carry_over(events, Provenance(model="human", worker="carried-over"))

    # ------------------------------------------------------------------ commands
    def handle(self, command: dict[str, Any]) -> dict[str, Any]:
        cmd = command.get("cmd")
        if cmd == "calibrate":
            pts = {k: (float(v[0]), float(v[1])) for k, v in command["points"].items()}
            h = fit_homography(pts)
            net = command.get("net_top")
            net_top = ((float(net[0][0]), float(net[0][1])), (float(net[1][0]), float(net[1][1]))) if net else None
            frame = command.get("frame")
            reference = None
            if frame is not None and self._frame_at is not None:
                try:
                    reference = self._frame_at(int(frame))
                except (OSError, ValueError, RuntimeError) as e:  # the segment is not decodable (yet)
                    log.warning("calibration.reference_unavailable", frame=frame, error=str(e))
            rec = self._apply_calibration(
                h, net_top=net_top, source="human", reference=reference, ref_frame=None if frame is None else int(frame)
            )
            return {
                "ok": True,
                "reprojection_error_px": h.reprojection_error_px,
                "n_points": h.n_points,
                "camera_tracking": self.perception.mode != "static",
                "mode": self.perception.mode,
                "adjusted_px": rec.get("adjusted_px"),
                "lines_check": rec.get("lines_check"),
            }
        if cmd == "auto_calibrate":
            # re-detect the court from the painted lines of frames sampled across the video (replaces the
            # current calibration; "Analyse again" re-measures what was already analysed)
            if self._frame_at is None or self.session.media is None:
                return {"ok": False, "error": "frames are not available"}
            n = max(1, self.session.media.n_frames)
            frames, idx = [], []
            for i in (int(n * (k + 0.5) / 24) for k in range(24)):
                try:
                    frames.append(self._frame_at(i))
                    idx.append(i)
                except (OSError, ValueError, RuntimeError):  # not transcoded yet
                    continue
            if not frames or not self._auto_calibrate(frames, idx):
                return {"ok": False, "error": "no court lines found in the sampled frames"}
            return {"ok": True, "mode": self.perception.mode}
        if cmd == "correct_winner":
            evs = self.engine.correct_rally_winner(
                command["rally_event_id"], command["winner"], Provenance(model="human", worker="review-ui")
            )
            return {"ok": True, "events": len(evs), "state": self.engine.public_state()}
        if cmd == "set_rally_official":
            evs = self.engine.set_rally_official(
                command["rally_event_id"], bool(command["official"]), Provenance(model="human", worker="review-ui")
            )
            return {"ok": True, "events": len(evs), "state": self.engine.public_state()}
        if cmd == "set_reviewed_match_intervals":
            evs = self.engine.set_reviewed_match_intervals(
                command.get("intervals"), Provenance(model="human", worker="review-ui")
            )
            return {"ok": True, "events": len(evs), "state": self.engine.public_state()}
        if cmd == "set_match_start":
            frame = command.get("frame")
            evs = self.engine.set_match_start(
                None if frame is None else int(frame), Provenance(model="human", worker="review-ui")
            )
            return {"ok": True, "events": len(evs), "state": self.engine.public_state()}
        if cmd == "verify_event":
            ev = self.store.get(command["event_id"])
            if ev is None:
                return {"ok": False, "error": "unknown event"}
            if ev.type in TRACKER_IDENTITY_EVIDENCE_TYPES:
                return {"ok": False, "error": "tracker identity evidence requires its dedicated review flow"}
            if ev.type in SCORE_REVIEW_EVENT_TYPES:
                return {
                    "ok": False,
                    "error": "score evidence requires a winner, official-play or match-phase correction",
                }
            patch = command.get("payload") or {}
            if "participant_hypothesis" in patch and (
                "participant_hypothesis" not in ev.payload
                or patch["participant_hypothesis"] != ev.payload["participant_hypothesis"]
            ):
                return {"ok": False, "error": "participant evidence cannot be changed by generic verification"}
            payload = {**ev.payload, **patch}
            corrected = ev.correct(
                payload=payload,
                status=EventStatus.HUMAN_VERIFIED,
                confidence=1.0,
                provenance=Provenance(model="human", worker="review-ui"),
            )
            appended = self.store.append(corrected)
            self.engine.on_superseded(appended)
            self._emit([appended])
            return {"ok": True, "event_id": appended.event_id}
        raise ValueError(f"unknown command {cmd!r}")

    # ------------------------------------------------------------------ views
    def public_state(self) -> dict[str, Any]:
        return {**self.engine.public_state(), "format": self.format_understanding.decision.to_public()}

    def analytics(self) -> dict[str, Any]:
        """Publish the same canonical event/track fold used by HTTP and reports.

        The runner persists its drained samples before publishing state. The
        engine's coordinate-only live buffers omit the time, track and camera
        evidence required for movement, so they cannot produce that view.
        Ledger identity and atomic track-file revisions invalidate the cache,
        including corrections and reanalysis that restarts sequence numbers.
        """
        from bai_badminton.analytics.rebuild import build

        stat = self.store.path.stat()
        tracks_root = self.store.path.parent / "tracks"
        revisions = []
        for kind in ("player", "camera"):
            directory = tracks_root / kind
            revision = directory.stat() if directory.exists() else None
            revisions.append((kind, revision.st_ino, revision.st_mtime_ns) if revision else (kind, None, None))
        media = self.session.media
        token = (
            self.store.last_seq(),
            stat.st_ino,
            stat.st_mtime_ns,
            tuple(revisions),
            media.fps_num if media else None,
            media.fps_den if media else None,
        )
        if getattr(self, "_analytics_token", None) != token or getattr(self, "_analytics_fold", None) is None:
            tracks = TrackStore(tracks_root) if tracks_root.exists() else None
            self._analytics_fold = build(self.store, tracks, float(media.fps) if media else 30.0)
            self._analytics_token = token
        a = self._analytics_fold.to_public()
        a["highlights"] = [h.to_public() for h in self._analytics_fold.highlights(k=12)]
        return a

    def degraded(self) -> list[dict[str, str]]:
        return [{"stage": d.stage, "reason": d.reason} for d in self.perception.degraded]

    def _format_cache_identity(self) -> dict[str, Any]:
        decision = self.format_understanding.decision
        return {
            "match_format": decision.match_format,
            "source": decision.source,
            "revision": decision.revision,
            "epoch": decision.epoch if decision.epoch is not None else str(self._format_epoch),
        }

    def describe_pipeline(self) -> dict[str, Any]:
        """Detached whole-pipeline composition, selected providers and cache identity."""
        description = loads(dumps(self._pipeline_declaration))
        active = {
            **self.perception.component_metadata,
            **self._domain_metadata,
            "format": {
                "contract": self._format_handle.contract.describe(),
                "fingerprint": self._format_handle.fingerprint,
            },
        }
        components = {}
        for kind, metadata in active.items():
            contract = metadata["contract"]
            components[kind] = {
                "implementation": contract["implementation"],
                "version": contract["version"],
                "fingerprint": metadata["fingerprint"],
                "status": "selected",
            }
        for kind, choice in self.perception.effective_choices.items():
            if kind not in components:
                components[kind] = {
                    "implementation": choice.implementation if choice else None,
                    "status": "unavailable" if choice and choice.model != "none" else "disabled",
                }
        decision = self.format_understanding.decision.to_public()
        description.update(
            components=components,
            format=decision,
            configuration={
                "profile": self.perception.profile.name,
                "source_sha256": self.session.source.sha256,
                "input_transform": {
                    key: self.session.meta[key]
                    for key in ("source_window", "source_time_transform", "analysis_proxy_sha256")
                    if key in self.session.meta
                },
                "scoring_names": {player.player_id: player.name for player in self.session.players},
                "roster": self.session.roster.model_dump(mode="json") if self.session.roster else None,
                "calibration": lines_ref_id(self.calibration.H) if self.calibration else None,
            },
        )
        identity = {**description, "format": self._format_cache_identity()}
        description["fingerprint"] = sha256(dumps(identity, sort_keys=True, allow_nan=False).encode()).hexdigest()
        return description

    def capabilities(self) -> dict[str, dict[str, Any]]:
        """Report actual execution, separately from optional research configuration."""
        from bai_badminton.events.contact import CONTACT_MODEL

        profile = self.perception.profile
        loaded = self.perception.models
        out: dict[str, dict[str, Any]] = {}
        out["named_identity"] = {
            "status": "review_required",
            "required": False,
            "reason": "Scoring names and configured format do not bind visual tracks to named athletes.",
            "review_action": (
                "Configure participants, review identity intervals, "
                "then confirm the hitter for each stroke."
            ),
            "policy": "reviewed_named_attribution_v1",
        }
        if hasattr(self, "format_understanding"):
            decision = self.format_understanding.decision
            out["format"] = {
                "status": decision.source,
                "required": True,
                "reason": decision.reason,
                "decision": decision.to_public(),
                "active_implementation": self._format_handle.contract.implementation,
            }
        for stage, attr, required in (
            ("shuttle", "shuttle", True),
            ("player_detector", "player_detector", True),
            ("pose", "pose", True),
            ("player_identity", "player_reid", False),
            ("ocr", "ocr", False),
            ("racket", "racket", False),
        ):
            choice = getattr(profile, attr, None)
            requested = choice.model if choice is not None else None
            active = loaded.get("player_reid" if stage == "player_identity" else stage)
            disabled = requested in (None, "none") or (choice is not None and choice.backend == "none")
            status = "loaded" if active else "disabled" if disabled else "unavailable"
            reason = next((d.reason for d in self.perception.degraded if d.stage == stage), "")
            if reason and active:
                status = "unavailable"
            if stage == "player_identity" and self.perception.match_format != "doubles" and not active:
                status, reason = "disabled", "Neural identity association is currently available for doubles only."
            out[stage] = {
                "status": status,
                "requested_model": requested,
                "active_model": active,
                "required": required,
                "reason": reason,
            }
            runtime = getattr(self.perception, "runtimes", {}).get(stage)
            if runtime is not None:
                out[stage]["runtime"] = runtime
                if active and runtime.get("backend_fallback"):
                    out[stage]["status"] = "fallback"
                    out[stage]["reason"] = f"Requested {runtime['requested_backend']}; actual runtime: {runtime}"
        scoreboard = getattr(self.perception, "scoreboard", None)
        if scoreboard is not None and getattr(scoreboard, "runtime", None):
            runtime = scoreboard.runtime
            out["ocr"]["runtime"] = runtime
            stages = runtime.get("stages", {})
            detail = "; ".join(
                f"{stage}: {info['model_file']} via {', '.join(info['providers'])}" for stage, info in stages.items()
            )
            out["ocr"]["reason"] = f"RapidOCR {runtime['package_version']}; {detail}"
            if runtime.get("backend_fallback"):
                out["ocr"]["status"] = "fallback"
                out["ocr"]["reason"] += f". Requested {runtime['requested_backend']} was not available for every stage."
        out["stroke"] = {
            "status": "heuristic",
            "requested_model": profile.stroke.model,
            "active_model": self.engine.stroke_clf.name,
            "required": True,
            "reason": (
                "Rule-based estimates with unknown outcomes; "
                "trained BST is available only for explicit singles shadow evaluation."
            ),
        }
        out["stroke_shadow"] = {
            "status": "shadow_only" if self.perception.match_format == "singles" else "unsupported",
            "requested_model": "bst_cg_ap_shuttleset",
            "active_model": None,
            "required": False,
            "reason": (
                "BST-CG-AP can be run explicitly on a completed singles session with verified weights. "
                "It does not publish live shot labels; development evaluation did not improve the repaired default."
                if self.perception.match_format == "singles"
                else "The pretrained BST-CG-AP checkpoint supports exactly two players; doubles are unsupported."
            ),
        }
        out["contact"] = {
            "status": "heuristic",
            "requested_model": profile.contact.model if profile.contact else None,
            "active_model": CONTACT_MODEL,
            "required": True,
            "reason": "Temporal motion, proximity and pose estimate potential hits; racket contact is not confirmed.",
        }
        if loaded.get("racket"):
            out["racket"]["status"] = "geometric"
            out["racket"]["reason"] = (
                "Observed ellipse, shaft and wrist support; no trained racket model or calibrated accuracy."
            )
        elif out["racket"]["requested_model"] not in (None, "none", "racket_geometry_v1"):
            out["racket"]["status"] = "unsupported"
        for stage in ("shuttle_live", "shuttle_second_opinion"):
            choice = getattr(profile, stage, None)
            requested = choice.model if choice is not None else None
            out[stage] = {
                "status": "disabled" if requested in (None, "none") else "unsupported",
                "requested_model": requested,
                "active_model": None,
                "required": False,
                "reason": "Optional research stage has no runtime adapter; it is not executed.",
            }
        if profile.shuttle.params.get("inpaint"):
            out["shuttle_refinement"] = {
                "status": "unsupported",
                "requested_model": "inpaintnet",
                "active_model": None,
                "required": False,
                "reason": "InpaintNet is not integrated; temporal gap filling is explicitly inferred.",
            }
        for kind, handle in getattr(self, "_domain_component_handles", {}).items():
            metadata = self._domain_metadata[kind]
            baseline = handle.contract.implementation == DOMAIN_BASELINES[kind]
            legacy = getattr(profile, kind, None)
            choice = self._domain_effective_choices[kind]
            requested = choice.model if kind in profile.components else legacy.model if legacy is not None else None
            previous = out.get(kind, {})
            active_model = metadata["model"]
            if baseline and kind == "contact":
                active_model = CONTACT_MODEL
            reason = (
                "Versioned rule/observation estimates; uncertainty and required evidence remain explicit."
                if baseline
                else "Explicitly selected provider; accuracy requires separate labelled evaluation."
            )
            if (
                kind == "stroke"
                and kind not in profile.components
                and requested not in (None, "none", "stroke_rules_v0")
            ):
                reason += f" Legacy requested artifact {requested} is not executed; active provider is stroke-rules-v0."
            out[kind] = {
                **previous,
                "status": ("rules" if kind == "scoring" else "derived" if kind == "analytics" else "heuristic")
                if baseline
                else "configured",
                "requested_model": requested,
                "active_model": active_model,
                "active_implementation": handle.contract.implementation,
                "component_fingerprint": metadata["fingerprint"],
                "contract": handle.contract.describe(),
                "required": True,
                "reason": reason,
            }
        if hasattr(self, "_pipeline_declaration"):
            out["pipeline"] = {"status": "configured", **self.describe_pipeline()}
        return out

    @property
    def requires_sequential_perception(self) -> bool:
        """All modes retain tracker, cut, background and camera history.

        Observation caches are diagnostics, not snapshots of that private state.
        A seek preview through this instance, or a mix of cached and fresh chunks,
        would corrupt chronology even when neural identity is disabled.
        """
        return True

    # ------------------------------------------------------------------ cache codec
    def _isolation_id(self) -> dict[str, Any]:
        policy = {
            "court": lines_ref_id(self.calibration.H) if self.calibration is not None else None,
            "mode": self.perception.mode,
            "fixed_camera": self._fixed_camera,
            "match_format": getattr(self.perception, "match_format", "singles"),
        }
        if self.perception.mode == "lines":
            policy["court_line_surface"] = 1
        profile = getattr(self.perception, "profile", None)
        if isinstance(profile, Profile):
            policy["profile"] = profile.model_dump(mode="json")
        policy["loaded_models"] = getattr(self.perception, "models", {})
        policy["components"] = getattr(self.perception, "component_metadata", {})
        policy["domain_components"] = getattr(self, "_domain_metadata", {})
        if hasattr(self, "_pipeline_declaration"):
            policy["pipeline_fingerprint"] = self.describe_pipeline()["fingerprint"]
        if hasattr(self, "format_understanding"):
            policy["format_understanding"] = {
                "method": FORMAT_METHOD,
                "configured_format": self.session.roster.match_format if self.session.roster else None,
                "contract": self._format_handle.contract.describe(),
                "configuration": self._format_choice.model_dump(mode="json"),
                "decision": self._format_cache_identity(),
                "state_restore": "recompute_in_canonical_frame_order",
            }
        policy["runtimes"] = getattr(self.perception, "runtimes", {})
        size = getattr(self.perception, "frame_size", None)
        policy["frame_size"] = list(size) if size else None
        policy["fps"] = getattr(self.perception, "fps", None)
        # Older doubles caches silently capped candidate tracks at four; do not
        # reuse them with the expanded policy. Existing singles caches remain valid.
        if getattr(self.perception, "match_format", "singles") == "doubles":
            policy["player_candidate_limit"] = 6
        identity_policy = getattr(self.perception, "identity_policy", None)
        if identity_policy is not None:
            policy["player_identity"] = identity_policy
        return policy

    def encode_perception(self, p: ChunkPerception) -> bytes:
        frames = []
        for fp in p.frames:
            frames.append(
                {
                    "f": fp.frame_idx,
                    "s": list(fp.shuttle_xy) if fp.shuttle_xy else None,
                    "c": fp.shuttle_conf,
                    "r": fp.replay,
                    "sh": fp.shot_id,
                    "g": [float(v) for v in fp.cam.ravel()] if fp.cam is not None else None,
                    "l": fp.cam_lost,
                    "v": fp.view,
                    "h": fp.head,
                    "q": fp.court_q,
                    "cs": fp.calibration_state.value if fp.calibration_state is not None else None,
                    "do": fp.detector_observed,
                    "ps": fp.pose_stride,
                    "p": [
                        {
                            "t": q.track_id,
                            "b": q.bbox.tolist(),
                            "c": q.conf,
                            "k": q.kps.tolist() if q.kps is not None else None,
                            "a": q.appearance.tolist() if q.appearance is not None else None,
                            "rt": q.raw_track_id,
                            "dm": q.detector_matched,
                            "im": q.identity_method,
                            "rk": asdict(q.racket) if q.racket is not None else None,
                        }
                        for q in fp.persons
                    ],
                }
            )
        out = msgpack.packb(
            {
                "v": CODEC_VERSION,
                "start": p.start,
                "cr": p.cam_ref,
                "ci": self._isolation_id(),
                "end": p.end,
                "models": p.models,
                "frames": frames,
                "ocr": [
                    {
                        "f": r.frame_idx,
                        "r": [list(x) for x in r.rows],
                        "c": r.conf,
                        "ctx": asdict(r.context) if r.context is not None else None,
                    }
                    for r in p.ocr
                ],
            },
            use_bin_type=True,
        )
        assert isinstance(out, bytes)
        return out

    def decode_perception(self, data: bytes, *, diagnostic: bool = False) -> ChunkPerception:
        """Decode validated observations only for an explicit diagnostic replay.

        Decoding cannot restore private perception state, so the runtime must
        recompute in chronological order rather than use this as a cache read.
        """
        if not diagnostic:
            raise StaleCacheError("badminton requires sequential fresh perception; cache is diagnostic only")
        d = msgpack.unpackb(data, raw=False)
        ref_id = self.perception.ref_id
        if d.get("v", 1) != CODEC_VERSION or d.get("cr") != ref_id or d.get("ci") != self._isolation_id():
            # A static calibration has no camera reference, but its geometry and
            # lock policy still control both player admission and shuttle peaks.
            raise StaleCacheError(
                f"perception segment {d['start']} has stale codec/calibration policy "
                f"(version {d.get('v', 1)} vs {CODEC_VERSION}; reference {d.get('cr')} vs {ref_id})"
            )
        # A cache without explicit validity is incomplete, even if its version
        # and geometry fingerprint otherwise match. Never trust it as legacy.
        valid_states = {state.value for state in CalibrationState}
        if any(frame.get("cs") not in valid_states for frame in d["frames"]):
            raise StaleCacheError("perception segment lacks valid calibration state")
        if any(not isinstance(frame.get("do"), bool) for frame in d["frames"]):
            raise StaleCacheError("perception segment lacks detector observation metadata")
        if any(
            "ps" not in frame or (frame["ps"] is not None and (type(frame["ps"]) is not int or frame["ps"] < 0))
            for frame in d["frames"]
        ):
            raise StaleCacheError("perception segment lacks valid pose schedule metadata")
        if any(
            "rt" not in person
            or "dm" not in person
            or "im" not in person
            or (person["rt"] is not None and (type(person["rt"]) is not int or person["rt"] < 0))
            or (person["dm"] is not None and type(person["dm"]) is not bool)
            or (
                person["im"] is not None
                and (not isinstance(person["im"], str) or not person["im"] or len(person["im"]) > 96)
            )
            for frame in d["frames"]
            for person in frame["p"]
        ):
            raise StaleCacheError("perception segment lacks valid player identity provenance")
        frames = [
            FramePerception(
                frame_idx=f["f"],
                shuttle_xy=tuple(f["s"]) if f["s"] else None,
                shuttle_conf=f["c"],
                replay=f["r"],
                shot_id=f["sh"],
                cam=np.asarray(f["g"], dtype=np.float64).reshape(3, 3) if f.get("g") else None,
                cam_lost=bool(f.get("l", False)),
                view=f.get("v"),
                head=f.get("h"),
                court_q=f.get("q"),
                calibration_state=CalibrationState(f["cs"]) if f.get("cs") is not None else None,
                detector_observed=f["do"],
                pose_stride=f["ps"],
                persons=[
                    PersonObs(
                        track_id=q["t"],
                        bbox=np.asarray(q["b"]),
                        conf=q["c"],
                        kps=np.asarray(q["k"]) if q["k"] is not None else None,
                        appearance=np.asarray(q["a"], np.float32) if q["a"] is not None else None,
                        raw_track_id=q["rt"],
                        detector_matched=q["dm"],
                        identity_method=q["im"],
                        racket=RacketObservation(**q["rk"]) if q.get("rk") is not None else None,
                    )
                    for q in f["p"]
                ],
            )
            for f in d["frames"]
        ]
        ocr = [
            ScoreReading(
                frame_idx=o["f"],
                rows=((o["r"][0][0], o["r"][0][1]), (o["r"][1][0], o["r"][1][1])),
                conf=o["c"],
                context=ScoreObservationContext(**o["ctx"]) if o.get("ctx") is not None else None,
            )
            for o in d.get("ocr", [])
        ]
        return ChunkPerception(
            start=d["start"], end=d["end"], frames=frames, models=d.get("models", {}), ocr=ocr, cam_ref=d.get("cr")
        )


class BadmintonPlugin:
    name = "badminton"
    pipeline_id = "badminton-broadcast"
    pipeline_version = "2"
    stages = (
        ("perception", (), ("shuttle", "player_detector", "pose", "player_reid", "tracking", "racket", "ocr")),
        ("format", ("perception",), ("format",)),
        ("identity", ("perception", "format"), ("identity",)),
        ("activity", ("perception", "identity"), ("activity",)),
        ("contact", ("perception", "format", "identity"), ("contact",)),
        ("rally", ("contact", "activity"), ("rally",)),
        ("stroke", ("contact", "rally", "identity"), ("stroke",)),
        ("outcome", ("rally", "format", "perception"), ("outcome",)),
        ("scoring", ("format", "rally", "outcome", "perception"), ("scoring",)),
        ("analytics", ("scoring", "stroke", "identity"), ("analytics",)),
    )

    @classmethod
    def describe_pipeline(cls) -> dict[str, Any]:
        return {
            "plugin": cls.name,
            "pipeline_id": cls.pipeline_id,
            "pipeline_version": cls.pipeline_version,
            "input_schema": "canonical-cfr-bgr-chunk:v1",
            "output_schema": "events-and-observation-tracks:v1",
            "supported_formats": ["singles", "doubles", "unknown"],
            "configuration": "Profile.components",
            "stages": [
                {"id": name, "depends_on": list(dependencies), "components": list(components)}
                for name, dependencies, components in cls.stages
            ],
            "lifecycle": {
                "per_session_factory": True,
                "ordered_ingest": True,
                "state_restore": "recompute_perception;restore_event_fold",
                "close": "owned_components_after_resident_commands",
            },
            "failure_behavior": "explicit_unavailable_or_unknown;no_fabricated_points",
        }

    def create_session(
        self, session: Session, store: EventStore, profile: Profile, registry: ModelRegistry, emit: EmitFn
    ) -> BadmintonSession:
        return BadmintonSession(session, store, profile, registry, emit, pipeline_declaration=self.describe_pipeline())
