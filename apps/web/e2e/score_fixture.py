"""Disposable score synchronization fixture using real temporal/rule/store code.

Synthetic observations test propagation, never real-video perception accuracy.
This helper is installed only by the test server, not by the production app.
"""

import tempfile
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

import av
import numpy as np

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.match_phase import PhaseParams
from bai_badminton.testing.synth import make_match
from bai_engine.media.ffmpeg import Tools
from bai_engine.media.proxy import ProxyPlan, transcode
from bai_engine.schema import (
    Actors,
    Event,
    EventStatus,
    MediaInfo,
    PlayerInfo,
    Provenance,
    Session,
    SessionStatus,
    Source,
    SourceKind,
    TrackObject,
    samples_to_table,
)
from bai_engine.store import SessionRepository


def apply_reviewed_synthetic_labels(
    engine: BadmintonMatchEngine, labelled: list[tuple[str | None, int, list[tuple[int, str]]]]
) -> None:
    """Install explicit fixture review labels without claiming automatic athlete binding.

    Each entry supplies the labelled winner, source frame offset and known
    synthetic contact sequence. None marks an unscored warm-up exchange.
    The real engine supplies initial segments; explicit fixture span/contact
    labels then establish reviewed exchanges, score refolding and storage.
    """
    store = engine.store
    rallies = store.query(types=["rally_end"])
    if len(rallies) != len(labelled):
        raise AssertionError("Synthetic labels must match the segmented rally count")
    for rally, (_winner, offset, contacts) in zip(rallies, labelled, strict=True):
        shots = []
        # The fixture reviewer replaces inferred labels rather than counting
        # anonymous automatic strokes alongside its explicit labelled sequence.
        for original in rally.payload.get("shots", []):
            stroke = store.get(original.get("event_id")) if original.get("event_id") else None
            if stroke is not None and stroke.type == "stroke":
                store.append(stroke.retract(Provenance(model="human"), "replaced by explicit synthetic review labels"))
        reviewed_start = min(rally.frame_start, offset + contacts[0][0])
        reviewed_end = max(rally.frame_end, offset + contacts[-1][0])
        for index, (frame, player) in enumerate(contacts):
            absolute = offset + frame
            if not reviewed_start <= absolute <= reviewed_end:
                continue
            payload = {"stroke": "serve" if index == 0 else "clear", "is_serve": index == 0,
                       "evidence_kind": "human_reviewed", "fixture_source": "synthetic-contact-label"}
            stroke = store.append(Event(
                session_id=engine.session_id, type="stroke", frame_start=absolute, frame_end=absolute,
                pts_us=round(absolute / engine.cfg.fps * 1e6), actors=Actors(player_id=player),
                payload=payload, status=EventStatus.HUMAN_VERIFIED, provenance=Provenance(model="human"),
            ))
            shots.append({"event_id": stroke.event_id, "frame": absolute, "player_id": player, **payload})
        store.append(rally.correct(frame_start=reviewed_start, frame_end=reviewed_end,
                                   pts_us=round(reviewed_start / engine.cfg.fps * 1e6),
                                   payload={**rally.payload, "shots": shots, "n_shots": len(shots),
                                            "serve_frame": shots[0]["frame"],
                                            "duration_s": (reviewed_end - reviewed_start + 1) / engine.cfg.fps},
                                   status=EventStatus.HUMAN_VERIFIED, provenance=Provenance(model="human")))
    engine.restore_from_log(max(rally.frame_end for rally in rallies) + 1)
    for index, (winner, _, _) in enumerate(labelled):
        if winner is not None:
            current = store.query(types=["rally_end"])[index]
            engine.correct_rally_winner(current.event_id, winner, Provenance(model="human"))


def create_score_fixture(repo: SessionRepository, profile: str, *, media: bool = False) -> dict:
    match = make_match(["P1", "P2"])
    source = Source(kind=SourceKind.UPLOAD, uri="synthetic-score-observations", original_name="score-integrity.mp4")
    if media:
        # The clip only supplies a playable timeline; the controlled observations
        # below are the stated test evidence and are not inferred from these pixels.
        with tempfile.TemporaryDirectory(prefix="bai-score-media-") as temporary:
            video = Path(temporary) / "fixture.mp4"
            with av.open(str(video), "w") as output:
                stream = output.add_stream("libx264", rate=30)
                stream.width, stream.height, stream.pix_fmt = 1280, 720, "yuv420p"
                for frame in range(match.n_frames):
                    pixels = np.full((720, 1280, 3), (41, 49, 16), np.uint8)
                    x = (frame * 5) % 1260
                    pixels[120:130, x:x + 10] = 255
                    for packet in stream.encode(av.VideoFrame.from_ndarray(pixels, format="bgr24")):
                        output.mux(packet)
                for packet in stream.encode():
                    output.mux(packet)
            digest = sha256(video.read_bytes()).hexdigest()
            paths = repo.media_paths(digest)
            paths.root.mkdir(parents=True, exist_ok=True)
            paths.source(".mp4").write_bytes(video.read_bytes())
            source.sha256, source.uri = digest, str(paths.source(".mp4"))
            plan = ProxyPlan(Fraction(30), 720, 60, "libx264", False)
            transcode(str(video), paths, plan, Tools.resolve(), match.n_frames / 30).run()
    session = repo.save(Session(
        title="Score integrity synthetic fixture", source=source, profile=profile,
        players=[PlayerInfo(player_id="P1", name="Alpha"), PlayerInfo(player_id="P2", name="Beta")],
        status=SessionStatus.ANALYSED, frontier_frame=match.n_frames - 1, analysed_frames=match.n_frames,
        media=MediaInfo(fps_num=30, fps_den=1, n_frames=match.n_frames, width=1280, height=720,
                        duration_us=round(match.n_frames / 30 * 1e6)),
        meta={"fixture": "synthetic-score-observations-v1", "frames_per_segment": 60, "encoder": "libx264"},
    ))
    store = repo.events(session.session_id)
    engine = BadmintonMatchEngine(session.session_id, EngineConfig(
        fps=30, frame_width=1280, frame_height=720, phase=PhaseParams(allow_heuristic_official=True),
    ), store)
    engine.set_calibration(0, match.homography)
    tracks = repo.tracks(session.session_id)
    for chunk in match.chunks:
        engine.ingest(chunk)
        samples = engine.drain_tracks()
        for kind in TrackObject:
            rows = [sample for sample in samples if sample.obj == kind]
            if rows:
                tracks.write_chunk(kind, chunk.start, chunk.end, samples_to_table(rows))
    engine.flush()
    apply_reviewed_synthetic_labels(engine, [
        (winner, offset, rally.contacts)
        for winner, offset, rally in zip(match.winners, match.offsets, match.rallies, strict=True)
    ])
    return {
        "session_id": session.session_id,
        "rally_event_ids": [event.event_id for event in store.query(types=["rally_end"])],
        "frame": match.n_frames - 2,
        "score": engine.public_state()["score"],
    }
