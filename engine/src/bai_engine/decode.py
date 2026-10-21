"""Frame decoding of the canonical proxy.

``SegmentDecoder`` decodes HLS fMP4 segment ``k`` (``init.mp4`` + ``seg_k.m4s``) into frames
``[k·F, (k+1)·F − 1]``.  Because every segment starts with an IDR frame, segments decode
independently — that is what makes chunk scheduling around the playhead (and seeking) cheap.

CPU decoding uses PyAV (FFmpeg).  On the GPU profile ``torchcodec`` with CUDA decoding can be
plugged in behind the same interface (``make_decoder``); frames are returned as ``uint8`` BGR
arrays (H, W, 3) on the host, which is what the ONNX/TensorRT runners consume.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import av
import numpy as np
from numpy.typing import NDArray

from bai_engine.media.proxy import init_path, segment_path
from bai_engine.store.sessions import MediaPaths

Frame = NDArray[np.uint8]


@dataclass
class DecodedChunk:
    start: int  # absolute frame index of frames[0]
    frames: list[Frame]

    @property
    def end(self) -> int:
        return self.start + len(self.frames) - 1


class Decoder(Protocol):
    def decode_segment(self, k: int) -> DecodedChunk: ...


class SegmentDecoder:
    def __init__(self, media: MediaPaths, frames_per_segment: int, threads: int = 2) -> None:
        self.media = media
        self.F = frames_per_segment
        self.threads = threads
        self._init: bytes | None = None

    def _init_bytes(self) -> bytes:
        if self._init is None:
            self._init = init_path(self.media).read_bytes()
        return self._init

    def decode_segment(self, k: int) -> DecodedChunk:
        seg = segment_path(self.media, k)
        data = self._init_bytes() + seg.read_bytes()
        frames: list[Frame] = []
        with av.open(io.BytesIO(data), format="mp4") as container:
            stream = container.streams.video[0]
            stream.thread_type = "AUTO"
            stream.codec_context.thread_count = self.threads
            for fr in container.decode(stream):
                frames.append(fr.to_ndarray(format="bgr24"))
        if len(frames) > self.F:
            frames = frames[: self.F]
        return DecodedChunk(start=k * self.F, frames=frames)

    def decode_frame(self, frame_idx: int) -> Frame:
        k, i = divmod(frame_idx, self.F)
        chunk = self.decode_segment(k)
        return chunk.frames[min(i, len(chunk.frames) - 1)]

    def keyframe(self, k: int) -> Frame:
        """First frame of segment ``k`` only (cheap: decodes one IDR)."""
        data = self._init_bytes() + segment_path(self.media, k).read_bytes()
        with av.open(io.BytesIO(data), format="mp4") as container:
            for fr in container.decode(container.streams.video[0]):
                return fr.to_ndarray(format="bgr24")
        raise RuntimeError(f"segment {k} has no frames")


class FileDecoder:
    """Sequential decoder over an arbitrary file (used for live/raw sources and tests)."""

    def __init__(self, path: Path, chunk_frames: int) -> None:
        self.path = path
        self.chunk = chunk_frames

    def iter_chunks(self):  # type: ignore[no-untyped-def]
        with av.open(str(self.path)) as container:
            stream = container.streams.video[0]
            stream.thread_type = "AUTO"
            buf: list[Frame] = []
            start = 0
            for fr in container.decode(stream):
                buf.append(fr.to_ndarray(format="bgr24"))
                if len(buf) == self.chunk:
                    yield DecodedChunk(start, buf)
                    start += len(buf)
                    buf = []
            if buf:
                yield DecodedChunk(start, buf)


def make_decoder(media: MediaPaths, frames_per_segment: int, device: str = "cpu") -> SegmentDecoder:
    # torchcodec CUDA decoding is wired here on the GPU profile once benchmarked (E1).
    return SegmentDecoder(media, frames_per_segment)
