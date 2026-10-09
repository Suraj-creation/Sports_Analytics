"""FFmpeg / ffprobe process helpers (no shell, timeouts, cancellation, progress parsing)."""

from __future__ import annotations

import functools
import json
import shutil
import subprocess
import threading
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from bai_engine.obs import get_logger

log = get_logger(__name__)


class MediaError(RuntimeError):
    """A media file could not be probed, decoded or transcoded."""


@dataclass(frozen=True)
class Tools:
    ffmpeg: str
    ffprobe: str

    @classmethod
    def resolve(cls, ffmpeg: str = "ffmpeg", ffprobe: str = "ffprobe") -> Tools:
        f, p = shutil.which(ffmpeg), shutil.which(ffprobe)
        if not f or not p:
            raise MediaError("ffmpeg/ffprobe not found on PATH (install FFmpeg ≥ 6)")
        return cls(f, p)


def run_json(cmd: Sequence[str], timeout: float) -> dict[str, object]:
    try:
        out = subprocess.run(list(cmd), capture_output=True, timeout=timeout, check=False)  # noqa: S603
    except subprocess.TimeoutExpired as e:
        raise MediaError(f"{Path(cmd[0]).name} timed out after {timeout}s") from e
    if out.returncode != 0:
        raise MediaError(out.stderr.decode(errors="replace")[-2000:] or f"exit {out.returncode}")
    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError as e:
        raise MediaError("invalid ffprobe output") from e
    assert isinstance(data, dict)
    return data


@functools.cache
def available_encoders(ffmpeg: str) -> frozenset[str]:
    out = subprocess.run([ffmpeg, "-hide_banner", "-encoders"], capture_output=True, timeout=20, check=False)  # noqa: S603
    names = set()
    for line in out.stdout.decode(errors="replace").splitlines():
        parts = line.split()
        if len(parts) >= 2 and len(parts[0]) == 6 and parts[0][0] in "VAS":
            names.add(parts[1])
    return frozenset(names)


@functools.cache
def nvenc_works(ffmpeg: str) -> bool:
    """True if h264_nvenc is compiled in *and* a CUDA device accepts a 1-frame encode."""
    if "h264_nvenc" not in available_encoders(ffmpeg):
        return False
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "lavfi",
        "-i",
        "color=s=256x144:d=0.1",
        "-frames:v",
        "1",
        "-c:v",
        "h264_nvenc",
        "-f",
        "null",
        "-",
    ]
    try:
        return subprocess.run(cmd, capture_output=True, timeout=20, check=False).returncode == 0  # noqa: S603
    except (OSError, subprocess.TimeoutExpired):
        return False


class FFmpegJob:
    """A running ffmpeg process with ``-progress pipe:1`` parsing and cooperative cancellation."""

    def __init__(
        self,
        cmd: Sequence[str],
        on_progress: Callable[[int], None] | None = None,
        stdin: int | None = None,
        cwd: Path | None = None,
    ) -> None:
        self.cmd = list(cmd)
        self.cwd = cwd
        self.on_progress = on_progress
        self._stdin = stdin
        self._proc: subprocess.Popen[bytes] | None = None
        self._stderr_tail: list[str] = []
        self._cancelled = threading.Event()

    def run(self) -> None:
        log.info("ffmpeg.start", cmd=" ".join(self.cmd[:3]) + " …")
        self._proc = subprocess.Popen(  # noqa: S603
            self.cmd, stdin=self._stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.cwd
        )
        t = threading.Thread(target=self._drain_stderr, daemon=True)
        t.start()
        assert self._proc.stdout is not None
        for raw in self._proc.stdout:
            line = raw.decode(errors="replace").strip()
            if line.startswith("out_time_us=") and self.on_progress is not None:
                v = line.split("=", 1)[1]
                if v.isdigit():
                    self.on_progress(int(v))
            if self._cancelled.is_set():
                self._proc.kill()
                break
        rc = self._proc.wait()
        t.join(timeout=5)
        if self._cancelled.is_set():
            raise MediaError("cancelled")
        if rc != 0:
            raise MediaError("ffmpeg failed: " + "\n".join(self._stderr_tail[-15:]))

    def _drain_stderr(self) -> None:
        assert self._proc is not None and self._proc.stderr is not None
        for raw in self._proc.stderr:
            self._stderr_tail.append(raw.decode(errors="replace").rstrip())
            if len(self._stderr_tail) > 200:
                del self._stderr_tail[:100]

    def cancel(self) -> None:
        self._cancelled.set()
        if self._proc is not None and self._proc.poll() is None:
            self._proc.kill()
