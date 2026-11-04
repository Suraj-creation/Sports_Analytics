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
    MediaInfo,
    PlayerInfo,
    Session,
    SessionStatus,
    Source,
    SourceKind,
    TrackObject,
    samples_to_table,
)
from bai_engine.store import SessionRepository


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
    return {
        "session_id": session.session_id,
        "rally_event_ids": [event.event_id for event in store.query(types=["rally_end"])],
        "frame": match.n_frames - 2,
        "score": engine.public_state()["score"],
    }
