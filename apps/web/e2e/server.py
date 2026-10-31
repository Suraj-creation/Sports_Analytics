"""End-to-end test server: a throwaway data dir, a model-free profile and a synthetic clip.

    uv run python apps/web/e2e/server.py 8765

Serves the built SPA (apps/web/dist) and the real API/engine in one process, so the browser
test exercises upload → FFmpeg proxy/HLS → engine scheduling → WebSocket → UI for real.
The synthetic clip is written to apps/web/e2e/.tmp/clip.mp4 for the test to upload.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import av
import numpy as np
import uvicorn

from bai_api.app import create_app
from bai_engine.config import REPO_ROOT, Settings

PROFILE = """
description: e2e — no models (ingest, HLS, scheduling, transport, UI)
device: cpu
chunk_frames: 60
lead_buffer_s: 1.0
shuttle: {model: none, backend: none}
player_detector: {model: none, backend: none}
pose: {model: none, backend: none}
stroke: {model: bst_cg_ap_shuttleset, backend: torch-cpu}
"""


def make_clip(path: Path, seconds: int = 8, fps: int = 30, size: tuple[int, int] = (640, 360)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with av.open(str(path), "w") as out:
        s = out.add_stream("libx264", rate=fps)
        s.width, s.height = size
        s.pix_fmt = "yuv420p"
        for i in range(seconds * fps):
            img = np.full((size[1], size[0], 3), (41, 49, 16), np.uint8)  # court mat
            x = (i * 5) % size[0]
            img[120:130, x : x + 10] = 255  # a moving "shuttle"
            for pkt in s.encode(av.VideoFrame.from_ndarray(img, format="bgr24")):
                out.mux(pkt)
        for pkt in s.encode():
            out.mux(pkt)


def install_review_fixture(app) -> None:  # type: ignore[no-untyped-def]
    """Controlled observations in this disposable test server only, never production API."""
    from fastapi import HTTPException

    from bai_engine.schema import Event, EventStatus, Provenance, SessionStatus, TrackObject, TrackSample
    from bai_engine.schema.session import ParticipantInfo, ParticipantRoster, TeamInfo
    from bai_engine.schema.tracks import samples_to_table

    @app.post("/__test__/review-fixture/{session_id}")
    def seed(session_id: str) -> dict:
        repo = app.state.repo
        session = repo.get(session_id)
        if session is None or session.status != SessionStatus.ANALYSED or session.media is None:
            raise HTTPException(409, "Upload and finish the synthetic test recording first")
        store = repo.events(session_id)
        if store.query(types=["participant_observation"]):
            raise HTTPException(409, "Fixture is already populated")
        roster = ParticipantRoster(
            match_format="doubles",
            teams=[TeamInfo(team_id="T1", score_slot="P1"), TeamInfo(team_id="T2", score_slot="P2")],
            participants=[
                ParticipantInfo(participant_id=f"person-{i}", name=name, team_id="T1" if i < 2 else "T2")
                for i, name in enumerate(("Alice", "Bob", "Cara", "Dev"))
            ],
        )
        repo.update(session_id, roster=roster)
        births, strokes = [], []
        for i in range(4):
            birth = store.append(
                Event(
                    session_id=session_id,
                    type="participant_observation",
                    frame_start=1,
                    frame_end=1,
                    pts_us=33333,
                    status=EventStatus.PROVISIONAL,
                    provenance=Provenance(model="participant_tracker_v1"),
                    payload={
                        "kind": "PLAYER_ENTERED",
                        "participant_id": f"participant-browser-{i:06d}",
                        "track_id": i,
                        "side": "near" if i < 2 else "far",
                    },
                )
            )
            births.append(birth)
            strokes.append(
                store.append(
                    Event(
                        session_id=session_id,
                        type="stroke",
                        frame_start=30 + i,
                        frame_end=30 + i,
                        pts_us=(30 + i) * 33333,
                        provenance=Provenance(model="controlled_browser_fixture"),
                        payload={
                            "stroke": "drive",
                            "participant_hypothesis": {
                                "status": "provisional",
                                "participant_id": birth.payload["participant_id"],
                                "track_id": i,
                                "observation_id": birth.event_id,
                            },
                        },
                    )
                )
            )
        store.append(
            Event(
                session_id=session_id,
                type="rally_end",
                frame_start=5,
                frame_end=90,
                pts_us=166667,
                provenance=Provenance(model="controlled_browser_fixture"),
                payload={
                    "official": True,
                    "rally_no": 1,
                    "duration_s": 3,
                    "shots": [{"event_id": stroke.event_id, "frame": stroke.frame_start} for stroke in strokes],
                },
            )
        )
        samples = []
        for frame in range(session.media.n_frames):
            for i, birth in enumerate(births):
                x, y = 80 + i * 140, 150 if i < 2 else 90
                samples.append(
                    TrackSample(
                        frame_idx=frame,
                        obj=TrackObject.PLAYER,
                        track_id=i,
                        participant_observation_id=birth.event_id,
                        bbox=(x - 20, y, x + 20, y + 100),
                        x=x,
                        y=y + 100,
                        court_x=-1 + frame * 0.01,
                        court_y=(-4, -2, 2, 4)[i],
                        conf=0.95,
                        detector_matched=True,
                        model="controlled_browser_fixture",
                    )
                )
                samples.append(
                    TrackSample(
                        frame_idx=frame,
                        obj=TrackObject.RACKET,
                        track_id=i,
                        participant_observation_id=birth.event_id,
                        bbox=(x - 12, y - 50, x + 12, y - 26),
                        x=x,
                        y=y - 38,
                        conf=0.9,
                        model="controlled_browser_fixture",
                    )
                )
            samples.append(
                TrackSample(
                    frame_idx=frame, obj=TrackObject.CAMERA, track_id=0, cam=(1, 0, 0, 0, 1, 0, 0, 0, 1), conf=0.95
                )
            )
        for kind in (TrackObject.PLAYER, TrackObject.RACKET, TrackObject.CAMERA):
            repo.tracks(session_id).write_chunk(
                kind, 0, session.media.n_frames - 1, samples_to_table([row for row in samples if row.obj is kind])
            )
        return {
            "births": [event.event_id for event in births],
            "strokes": [event.event_id for event in strokes],
            "analysis_revision": int(session.meta.get("analysis_revision", 0)),
        }


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    root = Path(tempfile.mkdtemp(prefix="bai-e2e-"))
    prof = root / "profiles"
    prof.mkdir()
    (prof / "e2e.yaml").write_text(PROFILE, encoding="utf-8")
    make_clip(Path(__file__).parent / ".tmp" / "clip.mp4")
    settings = Settings(
        data_dir=root / "data",
        profiles_dir=prof,
        models_dir=REPO_ROOT / "models",
        profile="e2e",
        redis_url=None,
        youtube_ingest=False,
        _env_file=None,
    )  # type: ignore[call-arg]
    try:
        app = create_app(settings)
        install_review_fixture(app)
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
