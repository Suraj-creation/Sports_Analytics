"""Capability probes must not suspend a background server through its terminal."""

import subprocess
from types import SimpleNamespace

from bai_engine.media import ffmpeg


def test_nvenc_probe_does_not_inherit_interactive_terminal(monkeypatch):
    ffmpeg.nvenc_works.cache_clear()
    monkeypatch.setattr(ffmpeg, "available_encoders", lambda _: {"h264_nvenc"})

    def run(command, **kwargs):
        assert "-nostdin" in command or kwargs.get("stdin") == subprocess.DEVNULL
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(ffmpeg.subprocess, "run", run)
    try:
        assert ffmpeg.nvenc_works("controlled-ffmpeg")
    finally:
        ffmpeg.nvenc_works.cache_clear()
