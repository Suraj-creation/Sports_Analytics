"""TrackNetV3 shuttle detector (VOD profile).

Model definition vendored from qaz812345/TrackNetV3 (MIT License, Copyright (c) 2024 qaz812345)
— see ``third_party/TrackNetV3/LICENSE``.  Only the network is reused; inference is rewritten:

* **non-overlapping 8-frame windows** (``step = seq_len``): one forward per 8 frames instead of
  the legacy ``sliding_step=1`` (≈8× compute);
* **background median per camera shot** from a bounded reservoir of frames seen so far (the
  legacy code sampled 1 800 frames from the whole video up front: minutes of seeking and up to
  ~15 GB of RAM);
* **thresholding on the raw heatmap** and ``confidence = peak heatmap value`` (the legacy
  ``CONF_TH`` was compared against an already-binarised map and had no effect);
* the same weights run through PyTorch (CPU/CUDA) or ONNX Runtime / TensorRT FP16.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
from numpy.typing import NDArray

from bai_engine.obs import get_logger

log = get_logger(__name__)

WIDTH, HEIGHT = 512, 288


def _build_torch_model(in_dim: int, out_dim: int):  # type: ignore[no-untyped-def]
    import torch
    from torch import nn

    class Conv2DBlock(nn.Module):
        def __init__(self, i: int, o: int) -> None:
            super().__init__()
            self.conv = nn.Conv2d(i, o, kernel_size=3, padding="same", bias=False)
            self.bn = nn.BatchNorm2d(o)
            self.relu = nn.ReLU()

        def forward(self, x):  # type: ignore[no-untyped-def]
            return self.relu(self.bn(self.conv(x)))

    class Double2DConv(nn.Module):
        def __init__(self, i: int, o: int) -> None:
            super().__init__()
            self.conv_1, self.conv_2 = Conv2DBlock(i, o), Conv2DBlock(o, o)

        def forward(self, x):  # type: ignore[no-untyped-def]
            return self.conv_2(self.conv_1(x))

    class Triple2DConv(nn.Module):
        def __init__(self, i: int, o: int) -> None:
            super().__init__()
            self.conv_1, self.conv_2, self.conv_3 = Conv2DBlock(i, o), Conv2DBlock(o, o), Conv2DBlock(o, o)

        def forward(self, x):  # type: ignore[no-untyped-def]
            return self.conv_3(self.conv_2(self.conv_1(x)))

    class TrackNet(nn.Module):
        def __init__(self, in_dim: int, out_dim: int) -> None:
            super().__init__()
            self.down_block_1 = Double2DConv(in_dim, 64)
            self.down_block_2 = Double2DConv(64, 128)
            self.down_block_3 = Triple2DConv(128, 256)
            self.bottleneck = Triple2DConv(256, 512)
            self.up_block_1 = Triple2DConv(768, 256)
            self.up_block_2 = Double2DConv(384, 128)
            self.up_block_3 = Double2DConv(192, 64)
            self.predictor = nn.Conv2d(64, out_dim, (1, 1))
            self.pool = nn.MaxPool2d((2, 2), stride=(2, 2))
            self.up = nn.Upsample(scale_factor=2)

        def forward(self, x):  # type: ignore[no-untyped-def]
            x1 = self.down_block_1(x)
            x2 = self.down_block_2(self.pool(x1))
            x3 = self.down_block_3(self.pool(x2))
            x = self.bottleneck(self.pool(x3))
            x = self.up_block_1(torch.cat([self.up(x), x3], dim=1))
            x = self.up_block_2(torch.cat([self.up(x), x2], dim=1))
            x = self.up_block_3(torch.cat([self.up(x), x1], dim=1))
            return torch.sigmoid(self.predictor(x))

    return TrackNet(in_dim, out_dim)


@dataclass
class BackgroundModel:
    """Per camera-shot median background (RGB, 512×288) from a bounded frame reservoir."""

    every: int = 15  # sample one frame every N frames
    capacity: int = 120
    refresh: int = 20  # recompute the median after this many new samples
    _samples: dict[int, deque[NDArray[np.uint8]]] = field(default_factory=dict)
    _median: dict[int, NDArray[np.uint8]] = field(default_factory=dict)
    _since: dict[int, int] = field(default_factory=dict)
    _count: dict[int, int] = field(default_factory=dict)

    def observe(self, shot: int, rgb_small: NDArray[np.uint8]) -> None:
        c = self._count.get(shot, 0)
        self._count[shot] = c + 1
        if c % self.every:
            return
        dq = self._samples.setdefault(shot, deque(maxlen=self.capacity))
        dq.append(rgb_small)
        self._since[shot] = self._since.get(shot, 0) + 1
        if shot not in self._median or self._since[shot] >= self.refresh:
            self._median[shot] = np.median(np.stack(dq), axis=0).astype(np.uint8)
            self._since[shot] = 0

    def seed(self, shot: int, frames: list[NDArray[np.uint8]]) -> None:
        """Pre-fill from frames sampled across the video at ingest (VOD warm start)."""
        dq = self._samples.setdefault(shot, deque(maxlen=self.capacity))
        for f in frames:
            dq.append(f)
        if dq:
            self._median[shot] = np.median(np.stack(dq), axis=0).astype(np.uint8)

    def get(self, shot: int, fallback: NDArray[np.uint8]) -> NDArray[np.uint8]:
        return self._median.get(shot, fallback)


@dataclass(frozen=True)
class ShuttleDetection:
    x: float  # analysis-frame px
    y: float
    conf: float


def heatmap_to_point(hm: NDArray[np.float32], threshold: float) -> tuple[float, float, float] | None:
    """Centroid (heatmap-weighted) of the blob containing the peak; ``conf`` = peak value."""
    peak = float(hm.max())
    if peak < threshold:
        return None
    binary = (hm >= threshold).astype(np.uint8)
    _, labels = cv2.connectedComponents(binary, connectivity=8)
    py, px = np.unravel_index(int(hm.argmax()), hm.shape)
    lab = labels[py, px]
    ys, xs = np.nonzero(labels == lab)
    w = hm[ys, xs]
    return float((xs * w).sum() / w.sum()), float((ys * w).sum() / w.sum()), peak


class TrackNetV3:
    """Shuttle detector over non-overlapping windows of ``seq_len`` frames."""

    def __init__(
        self,
        weights: Path,
        backend: str = "torch-cpu",
        threshold: float = 0.5,
        onnx_dir: Path | None = None,
        providers: list[object] | None = None,
        batch: int = 1,
    ) -> None:
        import torch

        ckpt = torch.load(weights, map_location="cpu", weights_only=False)
        p = ckpt.get("param_dict", {})
        self.seq_len = int(p.get("seq_len", 8))
        self.bg_mode = str(p.get("bg_mode", "concat"))
        if self.bg_mode != "concat":
            raise ValueError(f"unsupported TrackNetV3 bg_mode {self.bg_mode!r} (expected 'concat')")
        self.in_dim = (self.seq_len + 1) * 3
        self.threshold = threshold
        self.batch = max(1, batch)
        self.backend = backend
        self.bg = BackgroundModel()
        model = _build_torch_model(self.in_dim, self.seq_len)
        state = ckpt["model"]
        # legacy checkpoints have no separate pool/up modules — those are parameter-free
        missing, unexpected = model.load_state_dict(state, strict=False)
        if unexpected or [m for m in missing if not m.startswith(("pool", "up."))]:
            raise ValueError(f"checkpoint mismatch: missing={missing} unexpected={unexpected}")
        model.eval()
        self._torch = model
        self._ort = None
        if backend.startswith("torch-cuda"):
            self._torch = model.cuda().half() if torch.cuda.is_available() else model
        elif backend in ("onnx-cpu", "onnx-cuda", "tensorrt"):
            onnx_path = (onnx_dir or weights.parent) / f"tracknetv3_seq{self.seq_len}_{self.bg_mode}.onnx"
            if not onnx_path.exists():
                self.export_onnx(onnx_path)
            import onnxruntime as ort

            self._ort = ort.InferenceSession(str(onnx_path), providers=providers or ["CPUExecutionProvider"])
        log.info("tracknet.loaded", seq_len=self.seq_len, backend=backend)

    @property
    def model_ref(self) -> str:
        return "tracknetv3@3.0"

    def export_onnx(self, path: Path) -> None:
        import torch

        path.parent.mkdir(parents=True, exist_ok=True)
        dummy = torch.zeros(1, self.in_dim, HEIGHT, WIDTH)
        torch.onnx.export(
            self._torch.float().cpu(),
            dummy,
            str(path),
            input_names=["frames"],
            output_names=["heatmaps"],
            dynamic_axes={"frames": {0: "batch"}, "heatmaps": {0: "batch"}},
            opset_version=17,
        )
        log.info("tracknet.onnx_exported", path=str(path))

    # ------------------------------------------------------------------ inference
    def _prep(self, frames_bgr: list[NDArray[np.uint8]], shots: list[int]) -> list[NDArray[np.uint8]]:
        small = []
        for f, s in zip(frames_bgr, shots, strict=True):
            rgb = cv2.cvtColor(cv2.resize(f, (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
            self.bg.observe(s, rgb)
            small.append(rgb)
        return small

    def _forward(self, x: NDArray[np.float32]) -> NDArray[np.float32]:
        if self._ort is not None:
            out = self._ort.run(None, {"frames": x})[0]
            return np.asarray(out, dtype=np.float32)
        import torch

        with torch.inference_mode():
            t = torch.from_numpy(x)
            dev = next(self._torch.parameters())
            t = t.to(device=dev.device, dtype=dev.dtype)
            return self._torch(t).float().cpu().numpy()

    def detect(
        self, frames_bgr: list[NDArray[np.uint8]], shots: list[int] | None = None, step: int | None = None
    ) -> list[ShuttleDetection | None]:
        """Detect the shuttle in every frame.

        ``step`` = window stride.  ``step == seq_len`` (default) runs each frame once; a smaller
        step runs overlapping windows and averages each frame's heatmaps (the legacy "average"
        ensemble) — ``seq_len / step`` × the compute, used by the refinement escalation.
        """
        if not frames_bgr:
            return []
        L = self.seq_len
        step = L if step is None else max(1, min(step, L))
        shots = shots or [0] * len(frames_bgr)
        h, w = frames_bgr[0].shape[:2]
        sx, sy = w / WIDTH, h / HEIGHT
        small = self._prep(frames_bgr, shots)
        n = len(small)
        starts = list(range(0, max(1, n - L + 1), step))
        if starts[-1] + L < n:
            starts.append(n - L if n >= L else 0)
        acc = np.zeros((n, HEIGHT, WIDTH), np.float32)
        cnt = np.zeros(n, np.float32)
        windows, spans = [], []
        for s0 in starts:
            idx = [min(s0 + j, n - 1) for j in range(L)]
            bg = self.bg.get(shots[s0], small[s0])
            stack = np.concatenate([bg[None], np.stack([small[i] for i in idx])], axis=0)
            windows.append(np.moveaxis(stack, -1, 1).reshape(self.in_dim, HEIGHT, WIDTH))
            spans.append(idx)
        for b in range(0, len(windows), self.batch):
            x = np.stack(windows[b : b + self.batch]).astype(np.float32) / 255.0
            hms = self._forward(x)  # (B, L, H, W)
            for win, idx in zip(hms, spans[b : b + self.batch], strict=True):
                seen: set[int] = set()
                for j, i in enumerate(idx):
                    if i in seen:  # padded tail repeats the last frame
                        continue
                    seen.add(i)
                    acc[i] += win[j]
                    cnt[i] += 1
        out: list[ShuttleDetection | None] = []
        for i in range(n):
            pt = heatmap_to_point(acc[i] / max(cnt[i], 1.0), self.threshold)
            out.append(None if pt is None else ShuttleDetection(pt[0] * sx, pt[1] * sy, pt[2]))
        return out
