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
        uvicorn.run(create_app(settings), host="127.0.0.1", port=port, log_level="warning")
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
