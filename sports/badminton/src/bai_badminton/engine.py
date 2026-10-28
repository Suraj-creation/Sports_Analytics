"""Badminton match engine — the sequential temporal layer of the platform.

Consumes perception chunks **in frame order** and appends canonical events to the session's
event store.  Everything here is deterministic given the perception input, so the whole
semantic pipeline can be replayed from recorded perception (golden tests, re-analysis after a
model upgrade, CPU development without weights).

Latency model (VOD): a frame is *finalised* once ``lookahead`` frames after it have been seen
(gap filling, contact scoring and rally-end confirmation need that context).  Points are
emitted after the rally end plus the OCR waiting window.  With the analysis frontier running
ahead of playback by the lead buffer, all of this is invisible to the viewer.

Event flow::

    contact (provisional) ─► stroke (at next contact / rally end) ─► contact confirmed
    rally_start (provisional) ─► rally_end ─► point (+ game_end / interval / side_switch /
    match_end) ─► highlight (if notable)
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from dataclasses import asdict, dataclass, field, replace
from hashlib import sha256
from typing import Any

import numpy as np

from bai_badminton.analytics.match import MatchAnalytics, RallyRecord
from bai_badminton.court import Homography
from bai_badminton.events.activity import ActivityInterval, ActivityObservation, ActivityState, ActivityTracker
from bai_badminton.events.contact import CONTACT_MODEL, ContactCandidate, detect_contacts
from bai_badminton.events.match_phase import (
    MatchPhaseTracker,
    Phase,
    PhaseDecision,
    PhaseParams,
    RallyEvidence,
    serve_formation,
)
from bai_badminton.events.rally_fsm import RallyFSM, RallyParams, RallySegment
from bai_badminton.events.rally_outcome import CourtImageGeometry, Outcome, analyze_rally_end, outcome_confidence
from bai_badminton.events.scene import SceneSegment, SceneSegmenter
from bai_badminton.events.stroke import (
    RuleStrokeClassifier,
    StrokeClassifier,
    StrokeContext,
    assess_smash,
    jump_features,
)
from bai_badminton.identity import IdentityResolver
from bai_badminton.observations import PlayerSeries, WindowObs
from bai_badminton.ontology import get_ontology
from bai_badminton.participation import ParticipantTracker
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.camera import project
from bai_badminton.perception.keypoints import KP
from bai_badminton.perception.shuttle_post import Track, process
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs, ScoreReading
from bai_badminton.rules import (
    PLAYERS,
    MatchConfig,
    MatchState,
    RallyResult,
    Transition,
    apply_rally,
    initial_state,
    other,
)
from bai_badminton.score_ocr import ScoreReconciler
from bai_badminton.teams import DoublesTeamTracker
from bai_engine.schema import (
    Actors,
    ConfidenceBand,
    Event,
    EventStatus,
    Evidence,
    EvidenceKind,
    Provenance,
    StateSnapshot,
    TrackObject,
    TrackSample,
)
from bai_engine.store import EventStore
from bai_engine.timeline import Timeline

EmitFn = Callable[[list[Event]], None]


@dataclass(frozen=True)
class EngineConfig:
    fps: float
    frame_width: int
    frame_height: int
    lookahead: int = 40  # frames of future context before a frame is final
    context_back: int = 45  # past frames re-processed with each window (spike/gap context)
    history: int = 1800  # frames retained in memory (rally outcome & jump windows)
    ocr_wait_s: float = 4.0
    highlight_min_score: float = 4.0
    checkpoint_every_s: float = 10.0
    match: MatchConfig = field(default_factory=MatchConfig)
    phase: PhaseParams = field(default_factory=PhaseParams)
    profile: str = "unknown"


_OPPONENT = {"P1": "P2", "P2": "P1"}


def box_tuple(b: Any) -> tuple[float, float, float, float]:
    return float(b[0]), float(b[1]), float(b[2]), float(b[3])


def keypoint_rows(k: Any) -> tuple[tuple[float, float, float], ...] | None:
    """(x, y, score) rows as plain floats (track rows), or None."""
    return None if k is None else tuple((float(r[0]), float(r[1]), float(r[2])) for r in k)


def _usable_camera_pose(fp: FramePerception, *, allow_alternate: bool = False) -> Any:
    """Reject missing, stale, non-finite or singular camera transforms."""
    if fp.cam_lost or fp.cam is None or fp.scene == "none":
        return None
    if fp.calibration_state not in (None, CalibrationState.VALID) and not (allow_alternate and fp.scene == "alt"):
        return None
    try:
        cam = np.asarray(fp.cam, dtype=np.float64)
        if cam.shape != (3, 3) or not np.isfinite(cam).all() or np.linalg.cond(cam) >= 1e12:
            return None
    except (TypeError, ValueError, np.linalg.LinAlgError):
        return None
    return cam


def camera_sample(fp: FramePerception) -> TrackSample:
    """The per-frame CAMERA track row: pose (reference px → frame px; ``None``: no court in view), the physical
    camera that shot the frame (``track_id``: 0 = the main camera, -1 = none) and the court-line fit's
    precision (``conf``)."""
    cam = _usable_camera_pose(fp, allow_alternate=True)
    return TrackSample(
        frame_idx=fp.frame_idx,
        obj=TrackObject.CAMERA,
        visible=cam is not None,
        cam=tuple(float(v) for v in cam.ravel()) if cam is not None else None,
        track_id=(
            fp.head
            if fp.scene == "main" and fp.head is not None
            else (
                0
                if fp.scene == "main" and cam is not None
                else (fp.head if fp.scene == "alt" and fp.head not in (None, 0) else -1)
            )
        ),
        conf=float(fp.court_q) if fp.court_q is not None else 0.0,
    )


def _stabilise(p: PersonObs, Ginv: Any) -> PersonObs:
    """``p`` seen through the reference view: box corners and skeleton mapped by G⁻¹ (a copy)."""
    x1, y1, x2, y2 = (float(v) for v in p.bbox)
    q = project(Ginv, [[x1, y1], [x2, y1], [x2, y2], [x1, y2]])
    kps = None
    if p.kps is not None:
        kps = np.array(p.kps, dtype=np.float64, copy=True)
        kps[:, :2] = project(Ginv, kps[:, :2])
    return PersonObs(
        track_id=p.track_id,
        bbox=np.array([q[:, 0].min(), q[:, 1].min(), q[:, 0].max(), q[:, 1].max()]),
        conf=p.conf,
        kps=kps,
        appearance=p.appearance,
    )


@dataclass
class _Calib:
    homography: Homography
    geometry: CourtImageGeometry


@dataclass
class _Contact:
    cand: ContactCandidate
    event: Event
    stroke_event: Event | None = None


@dataclass
class _PendingRally:
    seg: RallySegment
    contacts: list[_Contact]
    start_event: Event | None


@dataclass
class _RallyEvents:
    """Events produced for one completed rally (needed to re-emit on corrections)."""

    rally_end: Event
    point: Event | None
    transitions: list[Event]
    record: RallyRecord
    geometry_winner: str | None
    outcome: str
    evidence: RallyEvidence = field(default_factory=RallyEvidence)
    observed_winner: str | None = None  # winner seen by OCR/geometry, whether or not the rally counted
    override: bool | None = None  # human official / not-official mark
    presence: dict[str, list[tuple[float, float]]] = field(default_factory=dict)


class BadmintonMatchEngine:
    def __init__(
        self,
        session_id: str,
        cfg: EngineConfig,
        store: EventStore,
        emit: EmitFn | None = None,
        stroke_classifier: StrokeClassifier | None = None,
        player_names: dict[str, str | None] | None = None,
    ) -> None:
        self.session_id = session_id
        self.cfg = cfg
        self.store = store
        self._emit_cb = emit
        self.timeline = Timeline.from_rate(cfg.fps, 10**9)
        self.ont = get_ontology()
        self.stroke_clf: StrokeClassifier = stroke_classifier or RuleStrokeClassifier()
        self.identity = IdentityResolver(frame_height=float(cfg.frame_height))
        self.participants: ParticipantTracker | None = None
        self._participant_shot_id: int | None = None
        self._participant_last_coverage: int | None = None
        self._participant_reference_changed = False
        self._multi_person_identity_ambiguous = False
        self.activity = ActivityTracker(cfg.fps)
        self.doubles_teams = DoublesTeamTracker(cfg.fps)
        self._current_team_key: tuple[Any, ...] | None = None
        self._activity_positions: deque[tuple[int, dict[int, tuple[float, float]]]] = deque(
            maxlen=max(3, round(cfg.fps * 0.5))
        )
        self.fsm = RallyFSM(RallyParams(fps=cfg.fps))
        self.analytics = MatchAnalytics(cfg.fps)
        self.ocr = ScoreReconciler(player_names=player_names or {})
        self.state: MatchState = initial_state(cfg.match)
        self._base_state: MatchState = self.state  # score the first official rally is played from
        self.match_cfg = cfg.match
        self.phase = MatchPhaseTracker(cfg.phase)
        self._last_rally_end: int | None = None
        self._seed_checked = False  # mid-match start: base score read from the scoreboard (once)
        self.calibration: dict[int, _Calib] = {}
        self._main_calib: _Calib | None = None
        # Camera tracking: while ``_cam_ref`` matches the perception's reference view every frame carries
        # the camera pose ``G`` (reference px → frame px).  All geometry below (shuttle, player boxes and
        # skeletons) is kept *stabilised* — mapped through G⁻¹ into the reference view, where the one
        # calibration (court homography, net line, in/out geometry) is valid — and mapped back (``_raw_xy``)
        # wherever a pixel position leaves the engine for the screen.
        self._cam_ref: int | None = None
        self._cam: list[Any] = []  # per frame: G (3×3) or None; aligned with the buffers
        self._track_out: list[TrackSample] = []
        self.scenes = SceneSegmenter(min_frames=max(6, int(round(0.5 * cfg.fps))))

        # dense buffers (absolute frame = _buf0 + index)
        self._buf0 = 0
        self._sx: list[float] = []
        self._sy: list[float] = []
        self._svis: list[bool] = []
        self._sconf: list[float] = []
        self._replay: list[bool] = []
        self._shot: list[int] = []
        self._geometry_valid: list[bool] = []
        self._players: dict[str, dict[str, list[Any]]] = {
            pid: {"bbox": [], "kps": [], "court": []} for pid in ("P1", "P2")
        }
        self._proc: Track | None = None  # processed shuttle over the current window
        self._proc0 = 0
        self._last_frame = -1
        self._final = -1  # last finalised frame
        self._open_contacts: list[_Contact] = []
        self._rally_start_event: Event | None = None
        self._pending: list[_PendingRally] = []
        self._rallies: list[_RallyEvents] = []
        self._last_checkpoint_frame = 0
        self._ocr_seen = False
        self._provenance = {"perception": "unknown"}

    # ================================================================== inputs
    def set_camera_reference(self, cam_ref: int | None) -> None:
        """Tracking (re)started against reference view ``cam_ref`` (a restart / re-analysis restoring the
        calibration; ``None``: not tracked)."""
        if self.participants is not None and cam_ref != self._cam_ref:
            self._participant_reference_changed = True
        self._cam_ref = cam_ref

    def set_calibration(
        self,
        shot_id: int,
        homography: Homography,
        net_top_left: tuple[float, float] | None = None,
        net_top_right: tuple[float, float] | None = None,
        *,
        emit: bool = True,
        source: str = "auto",
        cam_ref: int | None = None,
        ref_frame: int | None = None,
        extra: dict[str, Any] | None = None,
    ) -> Event | None:
        """Install the court calibration for a camera shot (``emit=False`` when restoring).

        ``source`` is ``"human"`` for a calibration placed in the UI — those survive a re-analysis.
        ``cam_ref`` identifies the reference view the camera tracker measures poses against (``None``:
        the camera is not tracked and the calibration is taken to hold for the whole shot).  ``extra`` is
        the rest of the calibration record (mode, method, validity, quality, camera, …).
        """
        if self.participants is not None:
            self._participant_reference_changed = True
        geom = CourtImageGeometry.from_homography(
            homography, net_top_left, net_top_right, singles=self.match_cfg.discipline == "singles"
        )
        self.calibration[shot_id] = _Calib(homography, geom)
        self._cam_ref = cam_ref
        self._main_calib = self.calibration[shot_id]  # broadcasts return to the main camera after cuts
        if shot_id == 0 or self.identity.net_image_y is None:
            self.identity.net_image_y = geom.net_ground_y
        if not emit:
            return None
        frame = max(self._last_frame, 0)
        quality = (extra or {}).get("quality") or {}
        # confidence: the court-line fit's precision when there is one (it is measured against the frame's own
        # lines); else the clicked points' fit error — exact for 4 points, so it says little
        conf = (
            float(quality["precision"])
            if "precision" in quality
            else float(np.clip(1.0 - homography.reprojection_error_px / 20.0, 0.0, 1.0))
        )
        ev = self._event(
            "calibration",
            frame,
            frame,
            payload={
                **(extra or {}),
                "shot_id": shot_id,
                **homography.to_json(),
                "net_ground_y": geom.net_ground_y,
                "net_top_y": geom.net_top_y,
                "source": source,
                "cam_ref": cam_ref,
                "ref_frame": ref_frame,
            },
            confidence=conf,
            status=EventStatus.CONFIRMED,
            model=str((extra or {}).get("method") or "calibration"),
        )
        self._emit([ev])
        return ev

    def on_ocr(self, reading: ScoreReading) -> None:
        self._ocr_seen = True
        self.ocr.add(reading)

    def ingest(self, chunk: ChunkPerception) -> None:
        if chunk.start != self._last_frame + 1:
            raise ValueError(f"chunk starts at {chunk.start}, expected {self._last_frame + 1}")
        self._provenance.update(chunk.models)
        for r in chunk.ocr:
            self.on_ocr(r)
        tracked = chunk.cam_ref is not None and chunk.cam_ref == self._cam_ref
        for fp in chunk.frames:
            self._append(fp, tracked)
        self._last_frame = chunk.end
        self._emit_scenes(self.scenes.drain())
        self._advance(self._last_frame - self.cfg.lookahead)
        self._finalize_pending(self._last_frame)
        self._maybe_checkpoint()
        self._trim()

    def flush(self) -> None:
        """End of stream: finalise everything."""
        if self._last_frame < 0:
            return
        self._emit_scenes(self.scenes.flush())
        self._emit_activity(self.activity.flush())
        self._advance(self._last_frame)
        upd = self.fsm.flush(self._last_frame)
        self._handle_fsm(upd, self._last_frame)
        self._finalize_pending(self._last_frame + 10**9)

    def _emit_scenes(self, segs: list[SceneSegment]) -> None:
        """Scene timeline: one event per final segment (which camera, analysed or not, court-fit quality)."""
        if not segs:
            return
        self._emit(
            [
                self._event(
                    "scene",
                    s.start,
                    s.end,
                    payload={
                        "view": s.view,
                        "camera": s.head,
                        "analysed": s.view == "main",
                        "court_quality": s.quality,
                        "duration_s": round(s.frames / self.cfg.fps, 2),
                    },
                    confidence=s.quality,
                    model="scene_v1",
                    status=EventStatus.CONFIRMED,
                )
                for s in segs
            ]
        )

    def _emit_activity(self, interval: ActivityInterval | None) -> None:
        if interval is None:
            return
        self._emit(
            [
                self._event(
                    "activity_interval",
                    interval.start_frame,
                    interval.end_frame,
                    payload={
                        "state": interval.state.value,
                        "basis": interval.basis,
                        "evidence_coverage": interval.evidence_coverage,
                        "match_intent": interval.match_intent,
                    },
                    model=interval.version,
                    status=EventStatus.CONFIRMED,
                )
            ]
        )

    # ================================================================== buffering
    def _append(self, fp: FramePerception, tracked: bool = False) -> None:
        G = _usable_camera_pose(fp) if tracked else None
        self._cam.append(G)
        Ginv = np.linalg.inv(G) if G is not None else None
        sxy = fp.shuttle_xy
        if sxy is not None and Ginv is not None:
            sx, sy = project(Ginv, [sxy])[0]
            sxy = (float(sx), float(sy))
        if sxy is not None:
            self._sx.append(float(sxy[0]))
            self._sy.append(float(sxy[1]))
            self._svis.append(True)
        else:
            self._sx.append(np.nan)
            self._sy.append(np.nan)
            self._svis.append(False)
        self._sconf.append(fp.shuttle_conf)
        self._replay.append(fp.replay)
        self._shot.append(fp.shot_id)
        # a tracked camera has one calibration (in the reference view) wherever the court is in view
        calib = (self._main_calib if G is not None else None) if tracked else self._calib(fp.shot_id)
        persons = [_stabilise(p, Ginv) for p in fp.persons] if Ginv is not None else fp.persons
        # A lost or non-main view cannot support authoritative court coordinates,
        # even if an upstream observation carries a stale position.
        geometry_unavailable = (
            fp.cam_lost
            or fp.scene != "main"
            or (tracked and G is None)
            or fp.calibration_state not in (None, CalibrationState.VALID)
        )
        if geometry_unavailable:
            calib = None
            persons = [replace(p, court_xy=None) for p in persons]
        for p in persons:
            if p.court_xy is None and calib is not None:
                feet = np.array([[(p.bbox[0] + p.bbox[2]) / 2, p.bbox[3]]])
                cx, cy = calib.homography.image_to_court(feet)[0]
                p.court_xy = (float(cx), float(cy))
        # A shot reset, long unavailable coverage, or recalibration can reuse
        # visual track IDs. Start a fresh deterministic epoch rather than link them.
        geometry_valid = not geometry_unavailable and calib is not None
        self._geometry_valid.append(geometry_valid)
        coverage_valid = geometry_valid and bool(self._provenance.get("player_detector")) and not fp.replay
        reason = None
        if self.participants is not None:
            if self._participant_reference_changed:
                reason = "calibration_changed"
            elif self._participant_shot_id is not None and fp.shot_id != self._participant_shot_id:
                reason = "visual_tracker_reset"
            elif (
                coverage_valid
                and self._participant_last_coverage is not None
                and fp.frame_idx - self._participant_last_coverage > max(1, round(2 * self.cfg.fps))
            ):
                reason = "prolonged_coverage_loss"
        if self.participants is None or reason is not None:
            epoch = sha256(f"{self.session_id}:{fp.frame_idx}".encode()).hexdigest()[:16]
            self.participants = ParticipantTracker(float(self.cfg.frame_height), fps=self.cfg.fps, instance_id=epoch)
            if reason is not None:
                self._participant_last_coverage = None
                self.doubles_teams = DoublesTeamTracker(self.cfg.fps)
                self._activity_positions.clear()
                self._multi_person_identity_ambiguous = True
                self._emit(
                    [
                        self._event(
                            "identity_ambiguity",
                            fp.frame_idx,
                            fp.frame_idx,
                            payload={"reason": reason, "certainty": "hypothesis", "tracker_instance": epoch},
                            model="participant_tracker_v1",
                            status=EventStatus.PROVISIONAL,
                        )
                    ]
                )
        self._participant_reference_changed = False
        self._participant_shot_id = fp.shot_id
        if coverage_valid:
            self._participant_last_coverage = fp.frame_idx
        participant_frame = self.participants.update(
            fp.frame_idx,
            persons,
            coverage_valid=coverage_valid,
            absence_valid=coverage_valid and fp.detector_observed is True,
        )
        participant_events = [
            self._event(
                "participant_observation",
                event.frame_idx,
                event.frame_idx,
                payload=asdict(event),
                model="participant_tracker_v1",
                status=EventStatus.PROVISIONAL,
            )
            for event in participant_frame.events
        ]
        self._emit(participant_events)
        # Movement is a supporting visual cue, not evidence of match intent.
        positions = {
            p.track_id: (float((p.bbox[0] + p.bbox[2]) / 2), float(p.bbox[3]))
            for p in persons
            if np.isfinite(p.conf) and p.conf >= 0.5 and np.isfinite(p.bbox).all()
        }
        movement = None
        if coverage_valid:
            if self._activity_positions and self._activity_positions[-1][0] != fp.frame_idx - 1:
                self._activity_positions.clear()
            if len(self._activity_positions) >= 2:
                previous = self._activity_positions[0][1]
                common = positions.keys() & previous.keys()
                if len(common) >= 2:
                    movement = any(
                        np.hypot(positions[k][0] - previous[k][0], positions[k][1] - previous[k][1])
                        >= max(2.0, self.cfg.frame_height * 0.005)
                        for k in common
                    )
            self._activity_positions.append((fp.frame_idx, positions))
        else:
            self._activity_positions.clear()
        activity_estimate, activity_interval = self.activity.update(
            ActivityObservation(
                frame_idx=fp.frame_idx,
                view_valid=geometry_valid and not fp.replay,
                person_count=len(participant_frame.participants) if coverage_valid else None,
                moving=movement,
                shuttle_visible=True if fp.shuttle_xy is not None and fp.shuttle_conf >= 0.5 else None,
                shuttle_position=(sxy[0] / self.cfg.frame_width, sxy[1] / self.cfg.frame_height)
                if geometry_valid and sxy is not None and fp.shuttle_conf >= 0.5 and np.isfinite(sxy).all()
                else None,
            )
        )
        self._emit_activity(activity_interval)
        # Doubles hypotheses require actual court-relative positions, not image-side fallback.
        by_track = {p.track_id: p for p in persons}
        team_geometry_valid = geometry_valid and len(participant_frame.participants) == 4
        if team_geometry_valid:
            for participant in participant_frame.participants:
                obs = by_track.get(participant.track_id)
                if (
                    obs is None
                    or obs.court_xy is None
                    or not np.isfinite(obs.court_xy).all()
                    or abs(obs.court_xy[1]) < 0.35
                    or participant.side != ("near" if obs.court_xy[1] < 0 else "far")
                ):
                    team_geometry_valid = False
                    break
        team_estimate = self.doubles_teams.update(
            participant_frame,
            court_valid=team_geometry_valid,
            active_play_evidence=activity_estimate.state == ActivityState.ACTIVE_PLAY,
        )
        team_key = tuple((team.team_id, team.members, team.side) for team in team_estimate.teams)
        if team_estimate.status == "provisional" and team_key != self._current_team_key:
            self._emit(
                [
                    self._event(
                        "doubles_team_hypothesis",
                        fp.frame_idx,
                        fp.frame_idx,
                        payload=asdict(team_estimate),
                        model=team_estimate.version,
                        status=EventStatus.PROVISIONAL,
                    )
                ]
            )
            self._current_team_key = team_key
        elif team_estimate.status != "provisional" and self._current_team_key is not None:
            self._emit(
                [
                    self._event(
                        "doubles_team_hypothesis",
                        fp.frame_idx,
                        fp.frame_idx,
                        payload=asdict(team_estimate),
                        model=team_estimate.version,
                        status=EventStatus.PROVISIONAL,
                    )
                ]
            )
            self._current_team_key = None
        # The legacy P1/P2 resolver models two individuals. Three or more
        # visible court tracks cannot safely be forced into those slots.
        visible_ids = {p.track_id for p in persons if p.track_id >= 0 and np.isfinite(p.conf) and p.conf >= 0.5}
        if coverage_valid and len(visible_ids) >= 3 and not self._multi_person_identity_ambiguous:
            self._multi_person_identity_ambiguous = True
            self._emit(
                [
                    self._event(
                        "identity_ambiguity",
                        fp.frame_idx,
                        fp.frame_idx,
                        payload={
                            "reason": "multiple_court_tracks",
                            "certainty": "hypothesis",
                            "track_count": len(visible_ids),
                        },
                        model="participant_tracker_v1",
                        status=EventStatus.PROVISIONAL,
                    )
                ]
            )
        assigned = (
            self.identity.assign(persons, {k: v.value for k, v in self.state.ends.items()})
            if geometry_valid and not fp.replay and not self._multi_person_identity_ambiguous
            else {}
        )
        for pid, buf in self._players.items():
            a = assigned.get(pid)
            buf["bbox"].append(a.bbox if a is not None else None)
            buf["kps"].append(a.kps if a is not None and a.kps is not None else None)
            buf["court"].append(a.court_xy if a is not None else None)
        # identity-resolved track samples for the track store / live overlays (raw frame pixels)
        self._track_out.append(
            TrackSample(
                frame_idx=fp.frame_idx,
                obj=TrackObject.SHUTTLE,
                x=fp.shuttle_xy[0] if fp.shuttle_xy else None,
                y=fp.shuttle_xy[1] if fp.shuttle_xy else None,
                visible=fp.shuttle_xy is not None,
                conf=float(fp.shuttle_conf),
                model=self._provenance.get("shuttle", ""),
            )
        )
        raw = {q.track_id: q for q in fp.persons}
        if self._multi_person_identity_ambiguous and geometry_valid:
            # Keep visual trajectories usable for overlays without assigning a
            # singles player or allowing them into player-specific statistics.
            for p in fp.persons:
                if p.track_id < 0 or not np.isfinite(p.conf) or not 0 <= p.conf <= 1 or not np.isfinite(p.bbox).all():
                    continue
                self._track_out.append(
                    TrackSample(
                        frame_idx=fp.frame_idx,
                        obj=TrackObject.PLAYER,
                        track_id=p.track_id,
                        player_id=None,
                        x=float((p.bbox[0] + p.bbox[2]) / 2),
                        y=float(p.bbox[3]),
                        bbox=box_tuple(p.bbox),
                        keypoints=keypoint_rows(p.kps),
                        conf=float(p.conf),
                        model=self._provenance.get("pose", self._provenance.get("player_detector", "")),
                    )
                )
        for pid, p in assigned.items():
            r = raw.get(p.track_id, p)
            self._track_out.append(
                TrackSample(
                    frame_idx=fp.frame_idx,
                    obj=TrackObject.PLAYER,
                    track_id=p.track_id,
                    player_id=pid,
                    x=float((r.bbox[0] + r.bbox[2]) / 2),
                    y=float(r.bbox[3]),
                    court_x=p.court_xy[0] if p.court_xy else None,
                    court_y=p.court_xy[1] if p.court_xy else None,
                    bbox=box_tuple(r.bbox),
                    keypoints=keypoint_rows(r.kps),
                    conf=float(p.conf),
                    model=self._provenance.get("pose", self._provenance.get("player_detector", "")),
                )
            )
        if tracked:
            self._track_out.append(camera_sample(fp))
        self.scenes.add(fp.frame_idx, fp.scene, fp.head, fp.court_q)

    def _raw_xy(self, frame: int, xy: tuple[float, float] | None) -> tuple[float, float] | None:
        """A stabilised (reference-view) image point as it appears in frame ``frame``'s pixels."""
        if xy is None:
            return None
        i = frame - self._buf0
        G = self._cam[i] if 0 <= i < len(self._cam) else None
        if G is None:
            return xy
        x, y = project(G, [xy])[0]
        return float(x), float(y)

    def _calib(self, shot_id: int) -> _Calib | None:
        return self.calibration.get(shot_id) or self._main_calib

    def drain_tracks(self) -> list[TrackSample]:
        """Identity-resolved per-frame samples appended since the last call."""
        out, self._track_out = self._track_out, []
        return out

    def _trim(self) -> None:
        keep_from = min(self._final - self.cfg.history, self._final - self.cfg.context_back - 1)
        pend = [p.seg.start for p in self._pending] + [c.cand.frame for c in self._open_contacts]
        if pend:
            ph = self.cfg.phase
            margin = max(60, int(max(ph.post_cut_s, ph.still_window_s) * self.cfg.fps) + 10)
            keep_from = min(keep_from, min(pend) - margin)
        drop = keep_from - self._buf0
        if drop <= 0:
            return
        for lst in (
            self._sx,
            self._sy,
            self._svis,
            self._sconf,
            self._replay,
            self._shot,
            self._cam,
            self._geometry_valid,
        ):
            del lst[:drop]
        for buf in self._players.values():
            for lst in buf.values():
                del lst[:drop]
        self._buf0 += drop

    def _window(self, lo: int, hi: int) -> WindowObs:
        """Dense observation arrays for absolute frames [lo, hi]."""
        a, b = lo - self._buf0, hi - self._buf0 + 1
        track = process(
            Track.from_arrays(
                np.array(self._sx[a:b]), np.array(self._sy[a:b]), np.array(self._svis[a:b]), np.array(self._sconf[a:b])
            )
        )
        n = b - a
        players = {}
        for pid, buf in self._players.items():
            s = PlayerSeries.empty(n)
            for i in range(n):
                bb = buf["bbox"][a + i]
                if bb is not None:
                    s.bbox[i] = bb
                k = buf["kps"][a + i]
                if k is not None:
                    s.kps[i] = k
                c = buf["court"][a + i]
                if c is not None:
                    s.court_xy[i] = c
            players[pid] = s
        return WindowObs(
            frame0=lo, fps=self.cfg.fps, shuttle=track, players=players, replay=np.array(self._replay[a:b], bool)
        )

    # ================================================================== frame advance
    def _advance(self, upto: int) -> None:
        start = self._final + 1
        if upto < start:
            return
        lo = max(self._buf0, start - self.cfg.context_back)
        w = self._window(lo, self._last_frame)
        self._proc, self._proc0 = w.shuttle, lo
        i0, i1 = w.idx(start), w.idx(upto) + 1
        contacts = {c.frame: c for c in detect_contacts(w, start=i0, stop=i1)}
        t = w.shuttle
        spd = np.zeros(w.n)
        spd[1:] = np.nan_to_num(np.hypot(np.diff(t.x), np.diff(t.y)))
        for i in range(i0, i1):
            f = w.frame0 + i
            c = contacts.get(f)
            if c is not None:
                self._handle_fsm(self.fsm.on_contact(f), f)
                self._on_contact(c, w)
            self._handle_fsm(self.fsm.step(f, bool(t.vis[i]), float(spd[i]), bool(w.replay[i])), f)
        self._final = upto

    def _handle_fsm(self, upd: Any, frame: int) -> None:
        if upd.started is not None:
            self._rally_start_event = self._event(
                "rally_start",
                upd.started,
                upd.started,
                payload={"rally_no": self.state.rally_no + 1},
                confidence=0.6,
                model="rally_fsm_v1",
            )
            self._emit([self._rally_start_event])
        if upd.cancelled_start is not None and self._rally_start_event is not None:
            self._emit([self._rally_start_event.retract(self._prov("rally_fsm_v1"), "rally shorter than minimum")])
            for c in self._open_contacts:
                self._retract_contact(c, "rally cancelled")
            self._open_contacts, self._rally_start_event = [], None
        if upd.finalized is not None:
            seg: RallySegment = upd.finalized
            in_rally = [c for c in self._open_contacts if seg.start - 3 <= c.cand.frame <= seg.end + 3]
            self._open_contacts = [c for c in self._open_contacts if c not in in_rally]
            self._pending.append(_PendingRally(seg, in_rally, self._rally_start_event))
            self._rally_start_event = None

    # ================================================================== contacts & strokes
    def _retract_contact(self, c: _Contact, note: str) -> None:
        """Withdraw a contact *and* the stroke classified from it (and its analytics)."""
        prov = self._prov("rally_fsm_v1")
        out = [c.event.retract(prov, note)]
        if c.stroke_event is not None:
            out.append(c.stroke_event.retract(prov, note))
        self._emit(out)

    def _on_contact(self, c: ContactCandidate, w: WindowObs) -> None:
        ev = self._event(
            "contact",
            c.frame,
            c.frame,
            actors=Actors(player_id=c.player_id),
            payload={"shuttle_xy": list(self._raw_xy(c.frame, c.shuttle_xy) or ()) or None},
            confidence=c.p,
            evidence=(
                Evidence(kind=EvidenceKind.COMPONENT_SCORES, scores=c.components),
                Evidence(kind=EvidenceKind.TRACK_WINDOW, obj="shuttle", frames=(c.frame - 3, c.frame + 3)),
            ),
            model=CONTACT_MODEL,
        )
        self._emit([ev])
        prev = self._open_contacts[-1] if self._open_contacts else None
        self._open_contacts.append(_Contact(c, ev))
        if prev is not None and prev.stroke_event is None:
            self._classify(prev, next_frame=c.frame, is_serve=len(self._open_contacts) == 2, receiver=c)

    def _shuttle_around(self, frame: int) -> tuple[Track, int] | None:
        """Processed shuttle track covering ``frame`` and ``frame``'s index in it.

        ``_proc`` is only the *latest* window.  A rally is finalised ``ocr_wait_s`` after it ends (once
        the scoreboard OCR is live), by which time that window has moved past its last contact — a
        negative index there either wraps silently or raises.  Re-derive a window around the frame
        from the dense buffers instead; ``None`` when the frame has left them."""
        if self._proc is not None and 0 <= frame - self._proc0 < len(self._proc):
            return self._proc, frame - self._proc0
        if not self._buf0 <= frame <= self._last_frame:
            return None
        lo = max(self._buf0, frame - self.cfg.context_back)
        w = self._window(lo, min(self._last_frame, frame + self.cfg.lookahead))
        return w.shuttle, frame - lo

    def _post_contact_kinematics(self, frame: int) -> tuple[float | None, float | None]:
        """Initial shuttle speed (px/s) and vertical velocity over the 4 frames after contact."""
        located = self._shuttle_around(frame)
        if located is None:
            return None, None
        t, i = located
        idx = [j for j in range(i + 1, min(len(t), i + 6)) if t.vis[j]]
        if len(idx) < 2:
            return None, None
        dt = (idx[-1] - idx[0]) / self.cfg.fps
        vx = (t.x[idx[-1]] - t.x[idx[0]]) / dt
        vy = (t.y[idx[-1]] - t.y[idx[0]]) / dt
        return float(np.hypot(vx, vy)), float(vy)

    def _player_at(
        self, pid: str | None, frame: int
    ) -> tuple[np.ndarray | None, np.ndarray | None, tuple[float, float] | None]:
        if pid is None:
            return None, None, None
        i = frame - self._buf0
        if not (0 <= i < len(self._players[pid]["bbox"])):
            return None, None, None
        b = self._players[pid]
        return b["bbox"][i], b["kps"][i], b["court"][i]

    def _classify(self, c: _Contact, next_frame: int | None, is_serve: bool, receiver: ContactCandidate | None) -> None:
        cand = c.cand
        bbox, _, court_xy = self._player_at(cand.player_id, cand.frame)
        speed, vy = self._post_contact_kinematics(cand.frame)
        above_head: bool | None = None
        if bbox is not None and cand.shuttle_xy is not None:
            above_head = bool(cand.shuttle_xy[1] < bbox[1] + 0.12 * (bbox[3] - bbox[1]))
        flight = (next_frame - cand.frame) / self.cfg.fps if next_frame is not None else None
        hitter_side = None
        if cand.player_id is not None:
            hitter_side = self.state.ends[cand.player_id].value
        ctx = StrokeContext(
            frame=cand.frame,
            player_id=cand.player_id,
            is_serve=is_serve,
            hitter_court_xy=court_xy,
            speed_after_px_s=speed,
            frame_height_px=float(self.cfg.frame_height),
            flight_time_s=flight,
            vy_after_px_s=vy,
            hitter_side=hitter_side,
            contact_above_head=above_head,
        )
        pred = self.stroke_clf.predict(ctx)
        stroke, p = pred.top
        payload: dict[str, Any] = {
            "stroke": stroke,
            "label": self.ont.stroke(stroke).label,
            "probs": dict(sorted(pred.probs.items(), key=lambda kv: -kv[1])[:4]),
            "is_serve": is_serve,
            "hitter_court_xy": list(court_xy) if court_xy else None,
            "speed_px_s": speed,
            "flight_time_s": flight,
            "contact_event_id": c.event.event_id,
            "receiver_id": receiver.player_id if receiver else None,
        }
        if receiver is not None:
            _, _, rc = self._player_at(receiver.player_id, receiver.frame)
            payload["receiver_court_xy"] = list(rc) if rc else None
            # Retain the legacy field for existing clients, but disclose that
            # these are receiver feet rather than an observed shuttle landing.
            payload["landing_court_xy"] = list(rc) if rc else None
            payload["landing_source"] = "receiver_position"
        comps: dict[str, float] = {}
        if stroke == "smash" or pred.probs.get("smash", 0.0) > 0.3:
            jf = self._jump_features(cand.player_id, cand.frame)
            sa = assess_smash(pred.probs.get("smash", 0.0), speed, float(self.cfg.frame_height), above_head, jf)
            payload["p_smash"] = round(sa.p_smash, 3)
            comps = {k: round(v, 4) for k, v in sa.components.items()}
            if sa.p_smash >= 0.5:
                stroke, p = "smash", max(p, sa.p_smash)
                payload["stroke"], payload["label"] = "smash", self.ont.stroke("smash").label
                if sa.p_jump is not None:
                    payload["p_jump"] = round(sa.p_jump, 3)
                    if sa.p_jump >= 0.5:
                        payload["subtype"] = "jump_smash"
                        payload["label"] = self.ont.subtypes["jump_smash"]["label"]
        margin = pred.margin
        conf = float(min(p, 0.99))
        band = self.ont.band(conf)
        if margin < 0.15 and band is ConfidenceBand.CONFIRMED:
            band = ConfidenceBand.PROBABLE
        ev = self._event(
            "stroke",
            cand.frame,
            cand.frame,
            actors=Actors(player_id=cand.player_id, opponent_id=_OPPONENT.get(cand.player_id or "")),
            payload=payload,
            confidence=conf,
            band=band,
            evidence=(
                Evidence(kind=EvidenceKind.EVENT, event_id=c.event.event_id),
                Evidence(kind=EvidenceKind.COMPONENT_SCORES, scores=comps or {"margin": round(margin, 4)}),
                Evidence(kind=EvidenceKind.POSE, frames=(cand.frame - 20, cand.frame + 6)),
            ),
            model=pred.model,
            status=EventStatus.CONFIRMED,
        )
        c.stroke_event = ev
        confirmed_contact = c.event.correct(
            status=EventStatus.CONFIRMED, payload={**c.event.payload, "stroke_event_id": ev.event_id}
        )
        c.event = confirmed_contact
        self._emit([ev, confirmed_contact])
        # Classification confirms a physical event; match statistics require
        # its containing rally's official-play decision below.

    def _jump_features(self, pid: str | None, frame: int) -> dict[str, float] | None:
        if pid is None:
            return None
        lo, hi = frame - 22, frame + 8
        a, b = lo - self._buf0, hi - self._buf0
        buf = self._players[pid]
        if a < 0 or b > len(buf["kps"]):
            return None
        n = b - a
        ank = np.full((n, 2), np.nan)
        hips = np.full(n, np.nan)
        hts = np.full(n, np.nan)
        for i in range(n):
            k = buf["kps"][a + i]
            bb = buf["bbox"][a + i]
            if k is None or bb is None:
                continue
            ank[i] = (k[KP.L_ANKLE, 1], k[KP.R_ANKLE, 1])
            hips[i] = (k[KP.L_HIP, 1] + k[KP.R_HIP, 1]) / 2
            hts[i] = bb[3] - bb[1]
        if np.isnan(hips).mean() > 0.5:
            return None
        return jump_features(ank, hips, hts, frame - lo)

    # ================================================================== rally end → point
    def _finalize_pending(self, frontier: int) -> None:
        wait = int(self.cfg.ocr_wait_s * self.cfg.fps) if self._ocr_seen else 0
        ready = [p for p in self._pending if frontier >= p.seg.end + wait]
        for p in ready:
            self._pending.remove(p)
            self._finalize_rally(p, until=p.seg.end + wait)
            self._maybe_seed_from_board()

    def _finalize_rally(self, p: _PendingRally, until: int) -> None:
        seg = p.seg
        # classify the last stroke (no next contact) before deciding the rally
        if p.contacts and p.contacts[-1].stroke_event is None:
            self._classify(p.contacts[-1], next_frame=None, is_serve=len(p.contacts) == 1, receiver=None)
        outcome, fault, check, conf_s = self._outcome(seg)
        before = self.state
        geometry_winner: str | None = None
        if fault in ("near", "far") and not self._multi_person_identity_ambiguous:
            loser = next(pid for pid, e in before.ends.items() if e.value == fault)
            geometry_winner = other(loser)  # type: ignore[arg-type]
        evidence = self._phase_evidence(seg, until)
        phase_before = self.phase.phase
        decision = self.phase.decide(seg.start, evidence, end=seg.end, match_finished=before.finished)
        observed, source = self.ocr.winner_from_ocr(
            dict(before.score), seg.start, seg.end, until, geometry_winner, lookback=int(30 * self.cfg.fps)
        )
        self._last_rally_end = seg.end
        winner = observed if decision.official else None
        loser_pid = other(winner) if winner in ("P1", "P2") else None  # type: ignore[arg-type]
        shots = [
            {
                "event_id": c.stroke_event.event_id if c.stroke_event else None,
                "frame": c.cand.frame,
                "player_id": c.cand.player_id,
                "stroke": c.stroke_event.payload.get("stroke") if c.stroke_event else "unknown",
                "subtype": c.stroke_event.payload.get("subtype") if c.stroke_event else None,
                "is_serve": c.stroke_event.payload.get("is_serve") if c.stroke_event else False,
            }
            for c in p.contacts
        ]
        rally_no = before.rally_no + 1 if decision.official else None
        conf = conf_s if source == "geometry" else 0.97
        rally_end = self._event(
            "rally_end",
            seg.start,
            seg.end,
            payload={
                "rally_no": rally_no,
                "serve_frame": seg.serve_frame,
                "end_reason": seg.reason,
                "outcome": outcome,
                "fault_side": fault,
                "winner": winner,
                "loser": loser_pid,
                "observed_winner": observed,
                "winner_source": source,
                "rule_check": check,
                "n_shots": len(shots),
                "shots": shots,
                "rally_start_event_id": p.start_event.event_id if p.start_event else None,
                "duration_s": round((seg.end - seg.start + 1) / self.cfg.fps, 2),
                **self._phase_payload(decision, evidence, None),
            },
            confidence=conf if winner else 0.2,
            evidence=(
                Evidence(
                    kind=EvidenceKind.TRACK_WINDOW,
                    obj="shuttle",
                    frames=(max(seg.start, seg.end - int(3 * self.cfg.fps)), seg.end),
                ),
                Evidence(kind=EvidenceKind.SCORE_OCR if source == "ocr" else EvidenceKind.COURT, note=source),
            ),
            model="rally_outcome_v1",
            status=EventStatus.CONFIRMED,
        )
        self._emit([rally_end])
        if decision.phase is not phase_before:
            self._emit_phase(decision, phase_before, seg.start, rally_end.event_id)
        record = RallyRecord(
            rally_id=rally_end.event_id,
            rally_no=rally_no or 0,
            start=seg.start,
            end=seg.end,
            winner=winner,
            loser=loser_pid,
            outcome=outcome,
            shots=shots,
            score_after=dict(before.score),
            game_no=before.game_no,
            flags_before=before.flags(self.match_cfg),
            duration_s=(seg.end - seg.start + 1) / self.cfg.fps,
            official=decision.official,
        )
        if decision.official:
            # Accept shots only when their rally is accepted as official play.
            for c in p.contacts:
                if c.stroke_event is not None:
                    self.analytics.on_stroke(c.stroke_event)
        point: Event | None = None
        transitions: list[Event] = []
        if winner in ("P1", "P2") and not before.finished:
            res = apply_rally(before, winner, self.match_cfg)  # type: ignore[arg-type]
            point, transitions = self._point_events(res, rally_end, seg, source)
            self.state = res.after
            record.score_after = self._score_after(res)
            record.score_available = True
            self.store.put_state(
                StateSnapshot(
                    session_id=self.session_id,
                    frame_idx=seg.end,
                    state=self.state.to_public(self.match_cfg),
                    event_seq=point.seq,
                )
            )
        presence = self._presence(seg)
        if decision.official:
            for pid, pts in presence.items():
                self.analytics.on_presence(pid, pts)
        self.analytics.on_rally(record)
        self._rallies.append(
            _RallyEvents(
                rally_end, point, transitions, record, geometry_winner, outcome, evidence, observed, None, presence
            )
        )
        if not decision.official:
            return
        h = self.analytics.score_rally(record)
        if h.score >= self.cfg.highlight_min_score:
            self._emit(
                [
                    self._event(
                        "highlight",
                        seg.start,
                        seg.end,
                        actors=Actors(player_id=h.player),
                        payload=h.to_public(),
                        confidence=min(1.0, h.score / 10),
                        model="highlight_mmr_v1",
                        status=EventStatus.CONFIRMED,
                        evidence=(Evidence(kind=EvidenceKind.EVENT, event_id=rally_end.event_id),),
                    )
                ]
            )

    # ================================================================== match phase
    def _phase_evidence(self, seg: RallySegment, until: int) -> RallyEvidence:
        """Evidence for "was this rally official play?" (see :mod:`bai_badminton.events.match_phase`)."""
        ph, fps = self.cfg.phase, self.cfg.fps
        lo = max(self._buf0, seg.start - int(ph.still_window_s * fps))
        a, b = lo - self._buf0, seg.start - self._buf0 + 1
        pos: dict[str, tuple[float, float]] = {}
        spread: list[float] = []
        for pid in PLAYERS:
            pts = [c for c in self._players[pid]["court"][a:b] if c is not None]
            if len(pts) < max(2, (b - a) // 3):
                continue
            arr = np.asarray(pts, dtype=float)
            med = np.median(arr, axis=0)
            pos[pid] = (float(med[0]), float(med[1]))
            # robust extent of the feet track (detector jitter on the far player is large)
            spread.append(float(np.linalg.norm(np.percentile(arr, 90, axis=0) - np.percentile(arr, 10, axis=0))))
        both = len(pos) == 2
        cut_lo = max(self._buf0, seg.start - int(ph.post_cut_s * fps)) - self._buf0
        recent_shots = {*self._shot[cut_lo : b - 1], self._shot_at(seg.start)}
        return RallyEvidence(
            calibrated=(
                0 <= seg.start - self._buf0 < len(self._geometry_valid) and self._geometry_valid[seg.start - self._buf0]
            ),
            formation=serve_formation(pos.get("P1"), pos.get("P2"), ph.court_tol_m) if both else None,
            still=all(x <= ph.still_max_m for x in spread) if both else None,
            gap_s=(seg.start - self._last_rally_end) / fps if self._last_rally_end is not None else None,
            after_cut=any(self._replay[cut_lo : b - 1]) or len(recent_shots) > 1,
            scoreboard=self.ocr.board_change(seg.start, seg.end, until, lookback=int(30 * fps)),
        )

    def _phase_payload(
        self, d: PhaseDecision, ev: RallyEvidence, override: bool | None, *, policy: str | None = None
    ) -> dict[str, Any]:
        if policy is None:
            policy = "legacy_heuristic_v1" if self.cfg.phase.allow_heuristic_official else "evidence_required_v1"
        return {
            "phase_policy": policy,
            "official": d.official,
            "phase": d.phase.value,
            "phase_reason": d.reason,
            "phase_basis": d.basis,
            "phase_evidence": ev.to_public(),
            "phase_override": override,
        }

    def _emit_phase(self, d: PhaseDecision, previous: Phase, frame: int, rally_event_id: str | None) -> None:
        self._emit(
            [
                self._event(
                    "match_phase",
                    frame,
                    frame,
                    payload={
                        "phase": d.phase.value,
                        "previous": previous.value,
                        "reason": d.reason,
                        "basis": d.basis,
                        "rally_event_id": rally_event_id,
                    },
                    confidence=1.0 if d.basis in ("human", "scoreboard") else 0.7,
                    model="match_phase_v1",
                    status=EventStatus.CONFIRMED,
                )
            ]
        )

    def _maybe_seed_from_board(self) -> None:
        """Video starting mid-game: once the scoreboard rows are mapped to players, take the score
        before the first official rally from the board instead of assuming 0-0, and re-fold.

        Only the current game's points are known (not earlier games or the server), so the match
        state is a partial observation; the ``match_phase`` event records the basis."""
        if self._seed_checked or self.ocr.row_map is None:
            return
        first = next((r for r in self._rallies if r.record.official), None)
        if first is None:
            return
        self._seed_checked = True
        val = self.ocr.stable_before(first.record.start, first.record.start - int(30 * self.cfg.fps))
        cfg = self.match_cfg
        if val is None or val == (0, 0) or max(val) >= cfg.point_cap:
            return
        hi, lo = max(val), min(val)
        if hi >= cfg.points_to_win and hi - lo >= 2:
            return  # a finished game's score: not a starting point
        score = {self.ocr.row_map[0]: val[0], self.ocr.row_map[1]: val[1]}
        self._base_state = self._base_state.model_copy(update={"score": score})
        f = first.record.start
        self._emit(
            [
                self._event(
                    "match_phase",
                    f,
                    f,
                    payload={
                        "phase": self.phase.phase.value,
                        "basis": "scoreboard",
                        "reason": "video starts mid-game: starting score read from the scoreboard",
                        "base_state": self._base_state.model_dump(mode="json"),
                        "server_known": False,
                    },
                    confidence=0.9,
                    model="score_ocr",
                    status=EventStatus.CONFIRMED,
                )
            ]
        )
        self._refold(self._prov("score_ocr"), force=True)

    @staticmethod
    def _score_after(res: RallyResult) -> dict[str, int]:
        if Transition.GAME_END in res.transitions:
            g = res.after.completed_games[-1]
            return {"P1": g[0], "P2": g[1]}
        return dict(res.after.score)

    def _outcome(self, seg: RallySegment) -> tuple[str, str, str, float]:
        # A camera cut or EOF closes our observation interval, not the rally.
        # Applying landing/extrapolation heuristics to an airborne shuttle
        # invents a winner. OCR and reviewers can still resolve the outcome.
        if seg.reason in ("cut", "flush"):
            return Outcome.UNKNOWN.value, "unknown", "incomplete_rally", 0.2

        calib = self._calib(self._shot_at(seg.end))
        if calib is None or self._proc is None:
            return Outcome.UNKNOWN.value, "unknown", "uncalibrated", 0.2
        # The FSM marks the *start* of the end condition (first stationary / invisible frame);
        # the outcome cascade must also see the shuttle at rest on the floor (CHECK 0), as the
        # legacy pipeline did with its stop-frame end times.
        settle = self.fsm.params.stationary_window if seg.reason == "stationary" else 3
        end = min(self._last_frame, seg.end + settle)
        lo = max(self._buf0, end - int(3.5 * self.cfg.fps))
        a, b = lo - self._buf0, end - self._buf0 + 1
        if a < 0 or b > len(self._geometry_valid) or not all(self._geometry_valid[a:b]):
            return Outcome.UNKNOWN.value, "unknown", "invalid_court_geometry", 0.2
        w = self._window(lo, end)
        res = analyze_rally_end(w.frames, w.shuttle.x, w.shuttle.y, w.shuttle.vis, end, calib.geometry, self.cfg.fps)
        return res.outcome.value, res.fault, res.check, outcome_confidence(res)

    def _shot_at(self, frame: int) -> int:
        i = frame - self._buf0
        return self._shot[i] if 0 <= i < len(self._shot) else 0

    def _presence(self, seg: RallySegment) -> dict[str, list[tuple[float, float]]]:
        a, b = max(0, seg.start - self._buf0), max(0, seg.end - self._buf0 + 1)
        out = {}
        for pid, buf in self._players.items():
            pts = [c for c in buf["court"][a:b] if c is not None]
            if pts:
                out[pid] = pts
        return out

    def _point_events(
        self, res: RallyResult, rally_end: Event, seg: RallySegment, source: str
    ) -> tuple[Event, list[Event]]:
        cfg = self.match_cfg
        f = seg.end
        point = self._event(
            "point",
            f,
            f,
            actors=Actors(player_id=res.winner, opponent_id=other(res.winner)),
            payload={
                "winner": res.winner,
                "rally_no": res.after.rally_no,
                "state_before": res.before.to_public(cfg),
                "state_after": res.after.to_public(cfg),
                "flags_before": res.before.flags(cfg),
                "transitions": [t.value for t in res.transitions],
                "game_point_saved": res.game_point_saved,
                "source": source,
            },
            confidence=rally_end.confidence,
            evidence=(Evidence(kind=EvidenceKind.EVENT, event_id=rally_end.event_id),),
            model="bwf_rules_v1",
            status=EventStatus.CONFIRMED,
            parent_id=rally_end.event_id,
        )
        out = [point]
        for t in res.transitions:
            if t is Transition.POINT:
                continue
            payload: dict[str, Any] = {"rally_no": res.after.rally_no}
            if t is Transition.GAME_END:
                payload.update(
                    {"game_no": res.before.game_no, "winner": res.winner, "score": list(res.after.completed_games[-1])}
                )
            elif t is Transition.MATCH_END:
                payload.update({"winner": res.winner, "games": [list(g) for g in res.after.completed_games]})
            elif t is Transition.SIDE_SWITCH:
                payload.update({"ends": {k: v.value for k, v in res.after.ends.items()}})
            elif t is Transition.INTERVAL:
                payload.update({"kind": "between_games" if Transition.GAME_END in res.transitions else "mid_game"})
            out.append(
                self._event(
                    t.value,
                    f,
                    f,
                    payload=payload,
                    confidence=point.confidence,
                    model="bwf_rules_v1",
                    status=EventStatus.CONFIRMED,
                    parent_id=point.event_id,
                )
            )
        appended = self._emit(out)
        return appended[0], appended[1:]

    # ================================================================== corrections
    def correct_rally_winner(self, rally_event_id: str, winner: str, provenance: Provenance) -> list[Event]:
        """Human (or OCR) correction of a rally winner: re-fold the match from that rally.

        Naming a winner says the rally was played for a point, so it also marks it official."""
        idx = self._rally_index(rally_event_id)
        r = self._rallies[idx]
        r.observed_winner, r.override = winner, True
        return self._refold(provenance, human={idx: {"winner_source": "human"}})

    def set_rally_official(self, rally_event_id: str, official: bool, provenance: Provenance) -> list[Event]:
        """Reviewer decision that a rally was (or was not) official play; re-scores what follows."""
        idx = self._rally_index(rally_event_id)
        self._rallies[idx].override = official
        return self._refold(provenance, human={idx: {}})

    def set_match_start(self, frame: int | None, provenance: Provenance) -> list[Event]:
        """Reviewer marker: rallies starting at/after ``frame`` are the match, earlier ones are not
        (``None`` removes the marker). Recorded as a human-verified ``match_phase`` event so it
        survives a re-analysis."""
        self.phase.match_start_frame = frame
        f = max(frame or 0, 0)
        marker = self._event(
            "match_phase",
            f,
            f,
            payload={"marker": "match_start", "frame": frame, "phase": "match_play", "basis": "human"},
            confidence=1.0,
            model="human",
            status=EventStatus.HUMAN_VERIFIED,
        )
        out = self._emit([marker.model_copy(update={"provenance": provenance})])
        return out + self._refold(provenance)

    def set_reviewed_match_intervals(
        self, intervals: list[tuple[int, int]] | None, provenance: Provenance
    ) -> list[Event]:
        """Set inclusive human-reviewed match windows; None removes this policy."""
        self.phase.set_reviewed_intervals(intervals)
        value = self.phase.reviewed_intervals
        frame = value[0][0] if value else 0
        marker = self._event(
            "match_phase",
            frame,
            frame,
            payload={"marker": "reviewed_intervals", "intervals": value, "basis": "human"},
            confidence=1.0,
            model="human",
            status=EventStatus.HUMAN_VERIFIED,
        )
        out = self._emit([marker.model_copy(update={"provenance": provenance})])
        return out + self._refold(provenance)

    def _rally_index(self, rally_event_id: str) -> int:
        for i, r in enumerate(self._rallies):
            if rally_event_id == r.rally_end.event_id or rally_event_id in self._lineage(r.rally_end):
                return i
        raise KeyError(rally_event_id)

    def _lineage(self, ev: Event) -> set[str]:
        from bai_badminton.analytics.rebuild import lineage_ids

        return set(lineage_ids(self.store, ev))

    def _refold(
        self, provenance: Provenance, human: dict[int, dict[str, Any]] | None = None, *, force: bool = False
    ) -> list[Event]:
        """Re-decide every rally's phase and re-fold the score; re-emit only what changed.

        Rallies before the first change keep their events; from the first change on, points and
        transitions are retracted and regenerated (the score after it may differ)."""
        human = human or {}
        cfg = self.match_cfg
        tracker = MatchPhaseTracker(
            self.cfg.phase,
            match_start_frame=self.phase.match_start_frame,
            reviewed_intervals=self.phase.reviewed_intervals,
        )
        state = self._base_state
        new_events: list[Event] = []
        retractions: list[Event] = []
        dirty = force  # e.g. a new base score: every point changes
        for i, r in enumerate(self._rallies):
            phase_before = tracker.phase
            # Historical events without a policy were generated by the legacy formation heuristic.
            # Preserve that policy during refolds so a correction cannot silently reclassify them.
            policy = r.rally_end.payload.get("phase_policy", "legacy_heuristic_v1")
            tracker.params = replace(self.cfg.phase, allow_heuristic_official=policy == "legacy_heuristic_v1")
            d = tracker.decide(
                r.record.start, r.evidence, end=r.record.end, match_finished=state.finished, override=r.override
            )
            winner = r.observed_winner if d.official else None
            loser = other(winner) if winner in PLAYERS else None
            rally_no = state.rally_no + 1 if d.official else None
            pay = r.rally_end.payload
            changed = (
                pay.get("official", True) != d.official
                or pay.get("winner") != winner
                or pay.get("rally_no") != rally_no
                or pay.get("phase_override") != r.override
            )
            if changed or i in human:
                dirty = True
                payload = {
                    **pay,
                    **self._phase_payload(d, r.evidence, r.override, policy=policy),
                    **human.get(i, {}),
                    "winner": winner,
                    "loser": loser,
                    "observed_winner": r.observed_winner,
                    "rally_no": rally_no,
                }
                kw: dict[str, Any] = {"payload": payload, "provenance": provenance}
                if i in human:
                    kw.update(status=EventStatus.HUMAN_VERIFIED, confidence=1.0)
                elif r.rally_end.status is EventStatus.HUMAN_VERIFIED:
                    kw.update(status=EventStatus.HUMAN_VERIFIED)
                r.rally_end = self._emit([r.rally_end.correct(**kw)])[0]  # stored before its points
                new_events.append(r.rally_end)
                if d.phase is not phase_before:
                    self._emit_phase(d, phase_before, r.record.start, r.rally_end.event_id)
            rec = r.record
            rec.rally_id, rec.official, rec.winner, rec.loser = r.rally_end.event_id, d.official, winner, loser
            rec.rally_no, rec.game_no, rec.flags_before = rally_no or 0, state.game_no, state.flags(cfg)
            if dirty:
                retractions.extend(old.retract(provenance, "re-folded") for old in [r.point, *r.transitions] if old)
                r.point, r.transitions = None, []
            if winner in PLAYERS and not state.finished:
                res = apply_rally(state, winner, cfg)
                if dirty:
                    seg = RallySegment(rec.start, rec.end, None, "correction")
                    r.point, r.transitions = self._point_events(
                        res, r.rally_end, seg, "human" if i in human else "refold"
                    )
                    new_events.extend([r.point, *r.transitions])
                state = res.after
                rec.score_after = self._score_after(res)
                rec.score_available = r.point is not None
            else:
                rec.score_after = dict(state.score)
                rec.score_available = False
            if dirty:  # overwrite the snapshot of the previous fold at this frame
                seq = r.point.seq if r.point else self.store.last_seq()
                self.store.put_state(
                    StateSnapshot(
                        session_id=self.session_id, frame_idx=rec.end, state=state.to_public(cfg), event_seq=seq
                    )
                )
        self.phase.phase = tracker.phase
        self.state = state
        new_events.extend(self._emit(retractions))
        self._rebuild_analytics()  # analytics are a fold: rebuild from the corrected rally records
        return new_events

    def on_superseded(self, ev: Event) -> None:
        """Keep the rally bookkeeping on the live version when an event is corrected outside the
        engine (e.g. a human verification appended by the plugin)."""
        for r in self._rallies:
            if r.rally_end.event_id == ev.supersedes:
                r.rally_end = ev
                r.record.rally_id = ev.event_id

    # ================================================================== restart / re-analysis
    def restore_from_log(self, last_frame: int) -> int:
        """Re-attach to a finished analysis: rebuild rally bookkeeping, match state and analytics
        from the stored live view, so corrections and calibration work after a restart without
        re-running (and re-emitting) the analysis. Returns the number of rallies restored."""
        from bai_badminton.analytics.rebuild import lineage_ids, rally_records

        self._multi_person_identity_ambiguous = bool(self.store.query(types=["identity_ambiguity"]))
        prior_teams = self.store.query(types=["doubles_team_hypothesis"])
        if prior_teams and prior_teams[-1].payload.get("status") == "provisional":
            # Restart does not restore visual continuity; close the old hypothesis on the next frame.
            self._current_team_key = ("restart_requires_reobservation",)
        rallies = self.store.query(types=["rally_end"])
        records = rally_records(self.store)
        point_by_parent = {p.parent_id: p for p in self.store.query(types=["point"])}
        trans_by_parent: dict[str | None, list[Event]] = {}
        for t in self.store.query(types=[t.value for t in Transition if t is not Transition.POINT]):
            trans_by_parent.setdefault(t.parent_id, []).append(t)
        phases = self.store.query(types=["match_phase"])
        for ph in phases:
            if ph.payload.get("base_state"):
                self._base_state = MatchState.model_validate(ph.payload["base_state"])
                self._seed_checked = True
            if not ph.payload.get("marker") and ph.payload.get("phase"):
                self.phase.phase = Phase(ph.payload["phase"])
        # Marker positions are video timestamps, not edit order. Later user
        # corrections win even when they move or clear a marker to an earlier frame.
        for ph in sorted(phases, key=lambda e: e.seq if e.seq is not None else -1):
            if ph.payload.get("marker") == "match_start":
                self.phase.match_start_frame = ph.payload.get("frame")
            elif ph.payload.get("marker") == "reviewed_intervals":
                self.phase.set_reviewed_intervals(ph.payload.get("intervals"))
        state = self._base_state
        self._rallies = []
        for ev, rec in zip(rallies, records, strict=True):
            pay = ev.payload
            point = next((point_by_parent[i] for i in lineage_ids(self.store, ev) if i in point_by_parent), None)
            if rec.official and rec.winner in PLAYERS and not state.finished:
                state = apply_rally(state, rec.winner, self.match_cfg).after
            transitions = trans_by_parent.get(point.event_id, []) if point else []
            evidence = RallyEvidence(**pay["phase_evidence"]) if pay.get("phase_evidence") else RallyEvidence()
            # logs from before match-phase gating counted every rally: keep that decision on re-fold
            override = pay["phase_override"] if "official" in pay else True
            observed = pay.get("observed_winner", pay.get("winner"))
            self._rallies.append(
                _RallyEvents(ev, point, transitions, rec, pay.get("winner"), rec.outcome, evidence, observed, override)
            )
            self._last_rally_end = rec.end
        self.state = state
        self._rebuild_analytics()
        self._last_frame = self._final = last_frame
        if not self._sx:
            # Restored engines have no pre-restart observation buffer.
            self._buf0 = last_frame + 1
        return len(self._rallies)

    def carry_over(self, events: list[Event], provenance: Provenance) -> int:
        """Re-apply human-verified events from an earlier analysis of the same video. Ids change
        on re-analysis, so events are matched by frames: rallies by overlap, other events by the
        nearest same-type event within a few frames. Idempotent; returns how many applied."""
        applied = 0
        changed_strokes = False
        # Coalesce policy markers by their append sequence before applying them;
        # replaying all historical markers would undo clears and break idempotence.
        latest_markers: dict[str, Event] = {}
        for _, item in sorted(enumerate(events), key=lambda pair: pair[1].seq if pair[1].seq is not None else pair[0]):
            marker = item.payload.get("marker")
            if (
                item.type == "match_phase"
                and item.status is EventStatus.HUMAN_VERIFIED
                and marker in ("match_start", "reviewed_intervals")
            ):
                latest_markers[marker] = item
        for h in sorted(events, key=lambda e: e.frame_start):
            if h.status is not EventStatus.HUMAN_VERIFIED:
                continue
            if h.type == "match_phase":
                marker = h.payload.get("marker")
                if marker in latest_markers and h.event_id != latest_markers[marker].event_id:
                    continue
                if marker == "match_start" and self.phase.match_start_frame != h.payload.get("frame"):
                    self.set_match_start(h.payload.get("frame"), provenance)
                    applied += 1
                elif h.payload.get("marker") == "reviewed_intervals":
                    intervals = h.payload.get("intervals")
                    normalized = None if intervals is None else tuple(tuple(pair) for pair in intervals)
                    if self.phase.reviewed_intervals != normalized:
                        self.set_reviewed_match_intervals(intervals, provenance)
                        applied += 1
                continue
            if h.type == "rally_end":
                tgt = self._match_rally(h.frame_start, h.frame_end)
                if tgt is None:
                    continue
                w = h.payload.get("winner")
                override = h.payload.get("phase_override")
                if w in ("P1", "P2") and tgt.rally_end.payload.get("winner") != w:
                    self.correct_rally_winner(tgt.rally_end.event_id, w, provenance)
                    applied += 1
                elif override is not None and tgt.override != override:
                    self.set_rally_official(tgt.rally_end.event_id, override, provenance)
                    applied += 1
                elif tgt.rally_end.status is not EventStatus.HUMAN_VERIFIED:
                    corr = tgt.rally_end.correct(
                        payload=tgt.rally_end.payload,
                        status=EventStatus.HUMAN_VERIFIED,
                        provenance=provenance,
                        confidence=1.0,
                    )
                    tgt.rally_end = self._emit([corr])[0]
                    tgt.record.rally_id = tgt.rally_end.event_id
                    applied += 1
                continue
            cur = self._nearest(h.type, h.frame_start, tol=3)
            if cur is None:
                continue
            # labels only: ids inside the old payload point at the previous analysis
            labels = {k: v for k, v in h.payload.items() if not (k.endswith("_id") or k.endswith("_ids"))}
            payload = {**cur.payload, **labels}
            if cur.status is EventStatus.HUMAN_VERIFIED and payload == cur.payload:
                continue
            self._emit(
                [cur.correct(payload=payload, status=EventStatus.HUMAN_VERIFIED, provenance=provenance, confidence=1.0)]
            )
            changed_strokes |= h.type == "stroke"
            applied += 1
        if changed_strokes:
            self._rebuild_analytics()
        return applied

    def _match_rally(self, start: int, end: int) -> _RallyEvents | None:
        best, best_ov = None, 0
        for r in self._rallies:
            ov = min(end, r.record.end) - max(start, r.record.start)
            if ov > best_ov:
                best, best_ov = r, ov
        if best is None:
            return None
        shorter = min(end - start, best.record.end - best.record.start) or 1
        return best if best_ov / shorter >= 0.5 else None

    def _nearest(self, type_: str, frame: int, tol: int) -> Event | None:
        cands = [e for e in self.store.query(types=[type_]) if abs(e.frame_start - frame) <= tol]
        return min(cands, key=lambda e: abs(e.frame_start - frame), default=None)

    def _rebuild_analytics(self) -> None:
        from bai_badminton.analytics.rebuild import rally_records

        self.analytics = MatchAnalytics(self.cfg.fps)
        # Embedded shot ids refer to the original ledger revisions. Resolve
        # them before replay so corrections/retractions cannot re-admit a
        # warm-up stroke or retain a superseded player/classification.
        canonical = {r.rally_id: r for r in rally_records(self.store)}
        for rally in self._rallies:
            current = canonical.get(rally.rally_end.event_id)
            if current is not None:
                rally.record.shots = current.shots
                rally.record.score_available = current.score_available
        official = {s.get("event_id") for r in self._rallies if r.record.official for s in r.record.shots}
        for ev in self.store.query(types=["stroke"]):
            if ev.event_id in official:
                self.analytics.on_stroke(ev)
        for r in self._rallies:
            if r.record.official:
                for pid, pts in r.presence.items():
                    self.analytics.on_presence(pid, pts)
            self.analytics.on_rally(r.record)

    # ================================================================== helpers
    def _maybe_checkpoint(self) -> None:
        every = int(self.cfg.checkpoint_every_s * self.cfg.fps)
        if self._final - self._last_checkpoint_frame >= every:
            self.store.put_state(
                StateSnapshot(
                    session_id=self.session_id,
                    frame_idx=max(self._final, 0),
                    kind="checkpoint",
                    state=self.state.to_public(self.match_cfg),
                    event_seq=self.store.last_seq(),
                )
            )
            self._last_checkpoint_frame = self._final

    def _prov(self, model: str) -> Provenance:
        return Provenance(model=model, profile=self.cfg.profile)

    def _event(
        self,
        type_: str,
        frame_start: int,
        frame_end: int,
        *,
        actors: Actors | None = None,
        payload: dict[str, Any] | None = None,
        confidence: float | None = None,
        band: ConfidenceBand | None = None,
        evidence: tuple[Evidence, ...] = (),
        model: str,
        status: EventStatus = EventStatus.PROVISIONAL,
        parent_id: str | None = None,
    ) -> Event:
        return Event(
            session_id=self.session_id,
            type=type_,
            frame_start=frame_start,
            frame_end=frame_end,
            pts_us=self.timeline.frame_to_pts_us(frame_start),
            actors=actors or Actors(),
            payload=payload or {},
            confidence=confidence,
            band=band or self.ont.band(confidence),
            status=status,
            evidence=evidence,
            provenance=self._prov(model),
            parent_id=parent_id,
        )

    def _emit(self, events: list[Event]) -> list[Event]:
        if not events:
            return []
        appended = self.store.append_many(events)
        if self._emit_cb is not None:
            self._emit_cb(appended)
        return appended

    # ================================================================== public views
    @property
    def final_frame(self) -> int:
        return self._final

    def public_state(self) -> dict[str, Any]:
        return self.state.to_public(self.match_cfg)
