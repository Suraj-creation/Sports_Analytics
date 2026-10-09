"""Badminton sport plugin — wires perception, the match engine and calibration into the platform."""

from __future__ import annotations

from typing import Any

import msgpack
import numpy as np

from bai_badminton.court import CalibrationError, Homography, fit_homography
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.rally_fsm import RallyState
from bai_badminton.perception.pipeline import BadmintonPerception
from bai_badminton.perception.scene import propose_corners
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs
from bai_engine.config import Profile, get_settings
from bai_engine.decode import DecodedChunk
from bai_engine.obs import get_logger
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import Event, EventStatus, Provenance, Session, TrackObject, TrackSample
from bai_engine.sport import EmitFn
from bai_engine.store import EventStore

log = get_logger(__name__)
AUTO_CALIBRATION_MIN_SCORE = 0.6


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
        self.perception = BadmintonPerception(profile, registry, fps, get_settings().models_dir)
        self.calibration: Homography | None = None
        self._emit = emit
        self._restore_calibration()

    # ------------------------------------------------------------------ calibration
    def _restore_calibration(self) -> None:
        """Re-apply the latest stored calibration (session restart / re-analysis)."""
        cal = self.store.query(types=["calibration"])
        if cal:
            h = Homography.from_json(cal[-1].payload)
            self._apply_calibration(h, emit=False)

    def _apply_calibration(
        self,
        h: Homography,
        emit: bool = True,
        net_top: tuple[tuple[float, float], tuple[float, float]] | None = None,
        source: str = "auto",
    ) -> None:
        self.calibration = h
        self.perception.set_calibration(h)
        self.engine.set_calibration(0, h, *(net_top or (None, None)), emit=emit, source=source)

    def seed(self, keyframes: list[Any]) -> None:
        self.perception.seed_background(keyframes)
        if self.calibration is not None or not keyframes:
            return
        best = None
        for f in keyframes:
            prop = propose_corners(f)
            if prop is not None and (best is None or prop[1] > best[1]):
                best = prop
        if best is None or best[1] < AUTO_CALIBRATION_MIN_SCORE:
            log.info("calibration.auto_failed", score=None if best is None else round(best[1], 2))
            return
        try:
            h = fit_homography(best[0])
        except CalibrationError as e:
            log.info("calibration.auto_invalid", error=str(e))
            return
        self._apply_calibration(h)
        log.info("calibration.auto", score=round(best[1], 2), err=round(h.reprojection_error_px, 2))

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
                        bbox=tuple(float(v) for v in person.bbox),  # type: ignore[arg-type]
                        keypoints=tuple(tuple(float(v) for v in r) for r in person.kps)
                        if person.kps is not None
                        else None,
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
            self._apply_calibration(h, net_top=net_top, source="human")
            return {"ok": True, "reprojection_error_px": h.reprojection_error_px, "n_points": h.n_points}
        if cmd == "correct_winner":
            evs = self.engine.correct_rally_winner(
                command["rally_event_id"], command["winner"], Provenance(model="human", worker="review-ui")
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
            {"v": 1, "start": p.start, "end": p.end, "models": p.models, "frames": frames}, use_bin_type=True
        )
        assert isinstance(out, bytes)
        return out

    def decode_perception(self, data: bytes) -> ChunkPerception:
        d = msgpack.unpackb(data, raw=False)
        frames = [
            FramePerception(
                frame_idx=f["f"],
                shuttle_xy=tuple(f["s"]) if f["s"] else None,
                shuttle_conf=f["c"],
                replay=f["r"],
                shot_id=f["sh"],
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
        return ChunkPerception(start=d["start"], end=d["end"], frames=frames, models=d.get("models", {}))


class BadmintonPlugin:
    name = "badminton"

    def create_session(
        self, session: Session, store: EventStore, profile: Profile, registry: ModelRegistry, emit: EmitFn
    ) -> BadmintonSession:
        return BadmintonSession(session, store, profile, registry, emit)
