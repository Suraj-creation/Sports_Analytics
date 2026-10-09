from __future__ import annotations

import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from bai_engine.config import REPO_ROOT, Settings

FAST_PROFILE = """
description: test profile — no models (exercises ingest, HLS, scheduling, transport)
device: cpu
chunk_frames: 60
lead_buffer_s: 2.0
shuttle: {model: none, backend: none}
player_detector: {model: none, backend: none}
pose: {model: none, backend: none}
stroke: {model: bst_cg_ap_shuttleset, backend: torch-cpu}
"""


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    prof = tmp_path / "profiles"
    prof.mkdir()
    (prof / "test-none.yaml").write_text(FAST_PROFILE, encoding="utf-8")
    shutil.copy(REPO_ROOT / "config" / "profiles" / "cpu-dev.yaml", prof / "cpu-dev.yaml")
    return Settings(
        data_dir=tmp_path / "data",
        profiles_dir=prof,
        models_dir=REPO_ROOT / "models",
        profile="test-none",
        redis_url=None,
        youtube_ingest=False,
        _env_file=None,
    )  # type: ignore[call-arg]


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    from bai_api.app import create_app

    with TestClient(create_app(settings)) as c:
        yield c


def make_video(path: Path, n: int = 150, fps: int = 30, size: tuple[int, int] = (640, 360)) -> Path:
    import av
    import numpy as np

    with av.open(str(path), "w") as out:
        s = out.add_stream("libx264", rate=fps)
        s.width, s.height = size
        s.pix_fmt = "yuv420p"
        for i in range(n):
            img = np.full((size[1], size[0], 3), 60, np.uint8)
            img[:, : size[0] // 2, 1] = 140  # half "court green"
            img[100:140, (i * 3) % size[0] : (i * 3) % size[0] + 20] = 255
            for pkt in s.encode(av.VideoFrame.from_ndarray(img, format="bgr24")):
                out.mux(pkt)
        for pkt in s.encode():
            out.mux(pkt)
    return path
