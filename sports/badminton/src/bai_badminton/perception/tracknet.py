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

import hashlib
import json
import marshal
import sys
import tempfile
from collections import deque
from collections.abc import Callable
from contextlib import nullcontext
from dataclasses import dataclass, field
from itertools import pairwise
from pathlib import Path
from typing import Any, BinaryIO

import cv2
import numpy as np
from numpy.typing import NDArray

from bai_engine.obs import get_logger
from bai_engine.runtime.device import ort_runtime

log = get_logger(__name__)

WIDTH, HEIGHT = 512, 288
# Bump for export-contract changes not represented by the other inputs. This
# is not a TensorRT engine-cache or complete dependency/toolchain fingerprint.
ONNX_EXPORT_CONTRACT = "tracknetv3-onnx-opset17-embedded-v3"


def _sha256_stream(stream: BinaryIO) -> str:
    """Hash a seekable binary stream without retaining checkpoint bytes in RAM."""
    stream.seek(0)
    digest = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(block)
    return digest.hexdigest()


def _onnx_cache_key(checkpoint_digest: str, torch_version: str) -> str:
    """Key an exported graph by its checkpoint and loaded export implementation.

    The executing code-object digest includes nested builder code. Including it
    avoids conflating an already-running process's old code with new source on
    disk after an edit. It does not fingerprint every exporter dependency.
    """
    with Path(__file__).open("rb") as stream:
        source_digest = _sha256_stream(stream)
    digest = hashlib.sha256()
    components = (
        ONNX_EXPORT_CONTRACT,
        checkpoint_digest,
        source_digest,
        torch_version,
        str(sys.version_info[:3]),
        str(WIDTH),
        str(HEIGHT),
    )
    for value in components:
        digest.update(value.encode("utf-8"))
        digest.update(b"\0")
    for function in (_build_torch_model, TrackNetV3.export_onnx):
        digest.update(marshal.dumps(function.__code__))
    return digest.hexdigest()


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


def heatmap_to_point(
    hm: NDArray[np.float32], threshold: float, mask: NDArray[np.uint8] | None = None
) -> tuple[float, float, float] | None:
    """Centroid (heatmap-weighted) of the blob containing the peak; ``conf`` = peak value."""
    if hm.ndim != 2 or not hm.size or not np.isfinite(hm).all():
        raise ValueError(f"shuttle heatmap must be a nonempty, finite 2D array, got {hm.shape}")
    if not np.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("shuttle heatmap threshold must be finite and in [0, 1]")
    if mask is not None:
        if mask.shape != hm.shape:
            raise ValueError("shuttle mask must match the heatmap shape")
        hm = np.where(mask, hm, 0.0)
    peak = float(hm.max())
    if peak <= 0 or peak < threshold:
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
        precision: str = "fp32",
        *,
        checkpoint_stream: BinaryIO | None = None,
        expected_sha256: str | None = None,
        provider_factory: Callable[[str], list[object]] | None = None,
    ) -> None:
        import torch

        if backend not in ("torch-cpu", "torch-cuda", "onnx-cpu", "onnx-cuda", "tensorrt"):
            raise ValueError(f"unsupported TrackNet backend {backend!r}")
        if precision not in ("fp32", "fp16"):
            raise ValueError(f"unsupported TrackNet precision {precision!r}")
        # Registry callers supply their verified private snapshot. Direct callers
        # retain the legacy path API and may require an expected integrity pin.
        # Hashing is not publisher authentication or protection from unsafe pickle
        # contents; only previously trusted checkpoints may be deserialized.
        checkpoint_digest = None
        cache_key = None
        graph_digest = None
        onnx_path = None
        if checkpoint_stream is not None or expected_sha256 is not None or backend in (
            "onnx-cpu", "onnx-cuda", "tensorrt"
        ):
            context = nullcontext(checkpoint_stream) if checkpoint_stream is not None else weights.open("rb")
            with context as stream:
                checkpoint_digest = _sha256_stream(stream)
                if expected_sha256 is not None and checkpoint_digest != expected_sha256:
                    raise ValueError("TrackNet checkpoint sha256 mismatch; refusing to deserialize")
                stream.seek(0)
                ckpt = torch.load(stream, map_location="cpu", weights_only=False)
                if _sha256_stream(stream) != checkpoint_digest:
                    raise ValueError("TrackNet checkpoint changed during loading")
        else:
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
        if backend == "torch-cuda" and torch.cuda.is_available():
            self._torch = model.cuda().half() if precision == "fp16" else model.cuda().float()
        elif backend in ("onnx-cpu", "onnx-cuda", "tensorrt"):
            if checkpoint_digest is None:
                raise RuntimeError("TrackNet ONNX export requires a checkpoint digest")
            cache_key = _onnx_cache_key(checkpoint_digest, str(torch.__version__))
            base = (onnx_dir or weights.parent) / f"tracknetv3_seq{self.seq_len}_{self.bg_mode}_{cache_key}.onnx"
            cached = self._cached_onnx(base, cache_key)
            onnx_path, graph_digest = cached if cached is not None else self._publish_onnx(base, cache_key)
            import onnxruntime as ort

            selected = provider_factory(graph_digest) if provider_factory is not None else providers
            self._ort = ort.InferenceSession(str(onnx_path), providers=selected or ["CPUExecutionProvider"])
            self._validate_onnx_contract(self._ort)
        if self._ort is not None:
            self.runtime = ort_runtime(backend, self._ort)
        else:
            param = next(self._torch.parameters())
            actual = "torch-cuda" if param.device.type == "cuda" else "torch-cpu"
            self.runtime = {
                "requested_backend": backend, "actual_backend": actual,
                "device": str(param.device), "dtype": str(param.dtype),
                "backend_fallback": actual != backend,
            }
        self.runtime["requested_precision"] = precision
        if checkpoint_digest is not None:
            self.runtime["checkpoint_sha256"] = checkpoint_digest
        if cache_key is not None:
            self.runtime["onnx_cache_key"] = cache_key
            self.runtime["onnx_sha256"] = graph_digest
            self.runtime["onnx_path"] = str(onnx_path)
            self.runtime["onnx_export_contract"] = ONNX_EXPORT_CONTRACT
        if self.runtime["backend_fallback"]:
            log.warning("tracknet.backend_fallback", **self.runtime)
        log.info("tracknet.loaded", seq_len=self.seq_len, **self.runtime)

    @property
    def model_ref(self) -> str:
        return "tracknetv3@3.0"

    def _validate_onnx_contract(self, session: Any) -> None:
        """Validate the baseline tensor names, float32 type and NCHW dimensions."""
        for values, name, channels in (
            (session.get_inputs(), "frames", self.in_dim),
            (session.get_outputs(), "heatmaps", self.seq_len),
        ):
            if len(values) != 1:
                raise ValueError("TrackNet ONNX tensor contract requires one input and one output")
            value = values[0]
            shape = value.shape
            if (
                value.name != name
                or value.type != "tensor(float)"
                or len(shape) != 4
                or shape[1:] != [channels, HEIGHT, WIDTH]
                or isinstance(shape[0], int)
            ):
                raise ValueError(f"TrackNet ONNX tensor contract mismatch for {name}")

    def _validate_onnx(self, path: Path) -> str:
        """Load serialized graph bytes with CPU ORT; external tensor files fail closed.

        Loading bytes, rather than a model path, prevents resolving untracked
        external weight files. This is graph/IO validation, not model accuracy.
        """
        import onnxruntime as ort

        data = path.read_bytes()
        if not data:
            raise ValueError("TrackNet ONNX contract requires a nonempty graph")
        options = ort.SessionOptions()
        options.intra_op_num_threads = 1
        options.inter_op_num_threads = 1
        try:
            session = ort.InferenceSession(data, sess_options=options, providers=["CPUExecutionProvider"])
            self._validate_onnx_contract(session)
        except Exception as error:
            raise ValueError(f"TrackNet ONNX contract validation failed: {error}") from error
        return hashlib.sha256(data).hexdigest()

    def _cached_onnx(self, base: Path, cache_key: str) -> tuple[Path, str] | None:
        """A manifest commits a content-addressed single-file graph.

        These are application-owned cache paths. Verification does not protect
        against an independent hostile writer changing a graph between validation
        and the final ORT path open; registry checkpoint snapshots close that
        distinct checkpoint-to-deserialization race.
        """
        manifest_path = base.with_suffix(".json")
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            graph_digest = manifest["graph_sha256"]
            if (
                manifest["schema"] != 1
                or manifest["cache_key"] != cache_key
                or manifest["export_contract"] != ONNX_EXPORT_CONTRACT
                or not isinstance(graph_digest, str)
                or len(graph_digest) != 64
                or any(char not in "0123456789abcdef" for char in graph_digest)
            ):
                raise ValueError("invalid graph cache manifest contract")
            path = base.with_name(f"{base.stem}_{graph_digest}.onnx")
            if manifest["filename"] != path.name:
                raise ValueError("invalid graph cache manifest filename")
            with path.open("rb") as stream:
                if _sha256_stream(stream) != graph_digest:
                    raise ValueError("cached graph sha256 mismatch")
            if self._validate_onnx(path) != graph_digest:
                raise ValueError("cached graph changed during validation")
            return path, graph_digest
        except FileNotFoundError:
            return None
        except (OSError, ValueError, KeyError, TypeError) as error:
            log.warning("tracknet.onnx_cache_invalid", path=str(manifest_path), error=str(error))
            return None

    def _publish_onnx(self, path: Path, cache_key: str) -> tuple[Path, str]:
        """Atomically commit a verified graph through a manifest publication marker.

        Concurrent exports never pair one export's digest with another graph:
        filenames include the graph content hash, then the manifest is replaced
        atomically. An interrupted writer leaves no reusable partial manifest.
        Legacy graph files and complete unreferenced exports are preserved.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        cache_root = path.parent.resolve()
        # The unique directory confines this export's graph and any unexpected
        # auxiliary files. It is removed after success, rejection or failure.
        with tempfile.TemporaryDirectory(prefix=".tracknet-", dir=cache_root) as tmp:
            temporary_dir = Path(tmp).resolve()
            if temporary_dir.parent != cache_root:
                raise RuntimeError("TrackNet temporary export directory is outside the cache")
            temporary = temporary_dir / "model.onnx"
            self.export_onnx(temporary)
            if not temporary.is_file() or any(entry != temporary for entry in temporary_dir.iterdir()):
                raise ValueError("TrackNet ONNX export produced unexpected auxiliary files")
            if temporary.stat().st_size == 0:
                raise ValueError("TrackNet ONNX export produced an empty file")
            graph_digest = self._validate_onnx(temporary)
            published = path.with_name(f"{path.stem}_{graph_digest}.onnx")
            manifest = {
                "schema": 1,
                "cache_key": cache_key,
                "export_contract": ONNX_EXPORT_CONTRACT,
                "graph_sha256": graph_digest,
                "filename": published.name,
            }
            marker = temporary_dir / "manifest.json"
            marker.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
            temporary.replace(published)
            marker.replace(path.with_suffix(".json"))
            return published, graph_digest

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
            external_data=False,
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
        self,
        frames_bgr: list[NDArray[np.uint8]],
        shots: list[int] | None = None,
        step: int | None = None,
        masks: list[NDArray[np.uint8]] | None = None,
    ) -> list[ShuttleDetection | None]:
        """Detect the shuttle in every frame.

        ``step`` = window stride.  ``step == seq_len`` (default) runs each frame once; a smaller
        step runs overlapping windows and averages each frame's heatmaps (the legacy "average"
        ensemble) — ``seq_len / step`` × the compute, used by the refinement escalation.
        """
        if not frames_bgr:
            return []
        if masks is not None and len(masks) != len(frames_bgr):
            raise ValueError("one shuttle mask is required per frame")
        if shots is not None and len(shots) != len(frames_bgr):
            raise ValueError("one camera-shot ID is required per frame")
        L = self.seq_len
        step = L if step is None else max(1, min(step, L))
        shots = shots or [0] * len(frames_bgr)
        h, w = frames_bgr[0].shape[:2]
        sx, sy = w / WIDTH, h / HEIGHT
        small = self._prep(frames_bgr, shots)
        n = len(small)
        acc = np.zeros((n, HEIGHT, WIDTH), np.float32)
        cnt = np.zeros(n, np.float32)
        windows, spans = [], []
        # A temporal network must never see frames from different camera shots
        # in one input. Pad only within each shot, including very short tails.
        boundaries = [0, *[i for i in range(1, n) if shots[i] != shots[i - 1]], n]
        for lo, hi in pairwise(boundaries):
            starts = list(range(lo, max(lo + 1, hi - L + 1), step))
            if starts[-1] + L < hi:
                starts.append(max(lo, hi - L))
            for s0 in starts:
                idx = [min(s0 + j, hi - 1) for j in range(L)]
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
            pt = heatmap_to_point(acc[i] / max(cnt[i], 1.0), self.threshold, None if masks is None else masks[i])
            out.append(None if pt is None else ShuttleDetection(pt[0] * sx, pt[1] * sy, pt[2]))
        return out
