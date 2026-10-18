"""Badminton sport plugin — wires perception, the match engine and calibration into the platform."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import cv2
import msgpack
import numpy as np

from bai_badminton.court import REFERENCE_POINTS, WIDTH_DOUBLES, CalibrationError, Homography, fit_homography
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, box_tuple, camera_sample, keypoint_rows
from bai_badminton.events.rally_fsm import RallyState
from bai_badminton.perception.court_lines import METHOD as LINES_METHOD
from bai_badminton.perception.court_lines import CourtFit, camera_pose, choose_main, detect_court, refine_court
from bai_badminton.perception.pipeline import BadmintonPerception
from bai_badminton.perception.scene import propose_corners
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs, ScoreReading
from bai_engine.config import Profile, get_settings
from bai_engine.decode import DecodedChunk
from bai_engine.obs import get_logger
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import Event, EventStatus, Provenance, Session, TrackObject, TrackSample
from bai_engine.sport import EmitFn
from bai_engine.store import EventStore

log = get_logger(__name__)
AUTO_CALIBRATION_MIN_SCORE = 0.6
REF_FILE = "camera_ref.png"  # the frame the calibration was made on (lossless: its id is a content hash)
CODEC_VERSION = 3  # 2: per-frame camera pose + the reference it is relative to; 3: scene view / camera head
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
        self, session: Session, store: EventStore, profile: Profile, registry: ModelRegistry, emit: EmitFn
    ) -> None:
        assert session.media is not None, "session media must be known before analysis starts"
        self.session = session
        self.store = store
        m = session.media
        fps = float(m.fps)
        names = {p.player_id: p.name for p in session.players}
        self.engine = BadmintonMatchEngine(
            session.session_id,
            EngineConfig(fps=fps, frame_width=m.width, frame_height=m.height, profile=profile.name),
            store,
            emit=emit,
            player_names=names,
        )
        self.perception = BadmintonPerception(
            profile, registry, fps, get_settings().models_dir, frame_size=(m.width, m.height)
        )
        self.calibration: Homography | None = None
        self._emit = emit
        self._frame_at: Callable[[int], np.ndarray] | None = None
        self._ref_dir: Path | None = None
        self._restored_cam_ref: int | None = None  # reference view id the restored calibration was tracked against
        self._restore_calibration()

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
                h, emit=False, net_top=net_top, mode="lines" if pay.get("mode") == "lines" else "static"
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
        extra: dict[str, Any] = dict(record or {})
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
        if self.calibration is not None or not keyframes:
            return
        if self._auto_calibrate(keyframes):
            return
        best = None  # legacy fallback: the court mat's outline (no painted lines found)
        for f in keyframes:
            prop = propose_corners(f)
            if prop is not None and (best is None or prop[1] > best[1]):
                best = (prop[0], prop[1], f)
        if best is None or best[1] < AUTO_CALIBRATION_MIN_SCORE:
            log.info("calibration.auto_failed", score=None if best is None else round(best[1], 2))
            return
        try:
            h = fit_homography(best[0])
        except CalibrationError as e:
            log.info("calibration.auto_invalid", error=str(e))
            return
        self._apply_calibration(h, reference=best[2], source="mat_contour_v0")
        log.info("calibration.auto", method="mat_contour", score=round(best[1], 2))

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

    def ingest(self, perception: ChunkPerception) -> None:
        self.engine.ingest(perception)

    def flush(self) -> None:
        self.engine.flush()

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
            for side, person in self.engine.identity.select_players(fp.persons).items():
                pid = next((k for k, v in self.engine.state.ends.items() if v.value == side), None)
                out.append(
                    TrackSample(
                        frame_idx=fp.frame_idx,
                        obj=TrackObject.PLAYER,
                        track_id=person.track_id,
                        player_id=pid,
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
            payload = {**ev.payload, **(command.get("payload") or {})}
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
        return self.engine.public_state()

    def analytics(self) -> dict[str, Any]:
        a = self.engine.analytics.to_public()
        a["highlights"] = [h.to_public() for h in self.engine.analytics.highlights(k=12)]
        return a

    def degraded(self) -> list[dict[str, str]]:
        return [{"stage": d.stage, "reason": d.reason} for d in self.perception.degraded]

    # ------------------------------------------------------------------ cache codec
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
                    "p": [
                        {
                            "t": q.track_id,
                            "b": q.bbox.tolist(),
                            "c": q.conf,
                            "k": q.kps.tolist() if q.kps is not None else None,
                            "a": q.appearance.tolist() if q.appearance is not None else None,
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
                "end": p.end,
                "models": p.models,
                "frames": frames,
                "ocr": [{"f": r.frame_idx, "r": [list(x) for x in r.rows], "c": r.conf} for r in p.ocr],
            },
            use_bin_type=True,
        )
        assert isinstance(out, bytes)
        return out

    def decode_perception(self, data: bytes) -> ChunkPerception:
        d = msgpack.unpackb(data, raw=False)
        ref_id = self.perception.ref_id
        if ref_id is not None and (d.get("v", 1) < CODEC_VERSION or d.get("cr") != ref_id):
            # made before camera tracking existed, or against another reference view: its poses (and the
            # court-presence gating they fed) do not match the current calibration
            raise StaleCacheError(
                f"perception segment {d['start']} was made against reference {d.get('cr')}, not {ref_id}"
            )
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
                persons=[
                    PersonObs(
                        track_id=q["t"],
                        bbox=np.asarray(q["b"]),
                        conf=q["c"],
                        kps=np.asarray(q["k"]) if q["k"] is not None else None,
                        appearance=np.asarray(q["a"], np.float32) if q["a"] is not None else None,
                    )
                    for q in f["p"]
                ],
            )
            for f in d["frames"]
        ]
        ocr = [
            ScoreReading(
                frame_idx=o["f"], rows=((o["r"][0][0], o["r"][0][1]), (o["r"][1][0], o["r"][1][1])), conf=o["c"]
            )
            for o in d.get("ocr", [])
        ]
        return ChunkPerception(
            start=d["start"], end=d["end"], frames=frames, models=d.get("models", {}), ocr=ocr, cam_ref=d.get("cr")
        )


class BadmintonPlugin:
    name = "badminton"

    def create_session(
        self, session: Session, store: EventStore, profile: Profile, registry: ModelRegistry, emit: EmitFn
    ) -> BadmintonSession:
        return BadmintonSession(session, store, profile, registry, emit)
