"""Controlled sessions validate device routing; these tests never execute CUDA."""

from types import SimpleNamespace

import pytest
import torch

from bai_badminton.perception import tracknet
from bai_badminton.perception.pipeline import BadmintonPerception
from bai_engine.config import ModelChoice


@pytest.mark.parametrize(
    "backend,actual,fallback",
    [
        ("onnx-cuda", ["CUDAExecutionProvider", "CPUExecutionProvider"], False),
        ("onnx-cuda", ["CPUExecutionProvider"], True),
        ("tensorrt", ["CUDAExecutionProvider", "CPUExecutionProvider"], True),
        ("onnx-cpu", ["CPUExecutionProvider"], False),
    ],
)
def test_actual_onnx_providers_determine_backend_status(backend, actual, fallback):
    from bai_engine.runtime.device import ort_runtime

    runtime = ort_runtime(backend, SimpleNamespace(get_providers=lambda: actual))
    assert runtime["providers"] == actual
    assert runtime["backend_fallback"] is fallback
    assert runtime["requested_backend"] == backend


def test_person_cpu_fallback_is_reported_even_when_the_model_load_succeeds(monkeypatch, tmp_path):
    import bai_badminton.perception.pipeline as pipeline

    perception = BadmintonPerception.__new__(BadmintonPerception)
    perception.models, perception.degraded = {}, []
    perception._providers = lambda *_: ["CPUExecutionProvider"]
    session = SimpleNamespace(get_providers=lambda: ["CPUExecutionProvider"])
    monkeypatch.setattr(
        pipeline, "PlayerDetector", lambda *a, **kw: SimpleNamespace(tool=SimpleNamespace(session=session))
    )
    registry = SimpleNamespace(
        path=lambda _: tmp_path / "unused.onnx",
        get=lambda _: SimpleNamespace(ref="rfdetr@test", input={"width": 384, "height": 384}),
    )
    assert perception._load_detector(ModelChoice(model="rfdetr_nano", backend="onnx-cuda"), registry, tmp_path)
    assert perception.runtimes["player_detector"]["backend_fallback"] is True
    assert perception.degraded[0].stage == "player_detector_backend"


@pytest.mark.parametrize(
    "available,precision,device,dtype",
    [
        (False, "fp16", "cpu", torch.float32),
        (True, "fp16", "cuda:0", torch.float16),
        (True, "fp32", "cuda:0", torch.float32),
    ],
)
def test_tracknet_preserves_requested_precision_and_discloses_cpu_fallback(
    monkeypatch,
    tmp_path,
    available,
    precision,
    device,
    dtype,
):
    class ControlledModel:
        def __init__(self):
            self.device, self.dtype = torch.device("cpu"), torch.float32

        def load_state_dict(self, *args, **kwargs):
            return [], []

        def eval(self):
            return self

        def cuda(self):
            self.device = torch.device("cuda:0")
            return self

        def half(self):
            self.dtype = torch.float16
            return self

        def float(self):
            self.dtype = torch.float32
            return self

        def parameters(self):
            return iter([SimpleNamespace(device=self.device, dtype=self.dtype)])

    monkeypatch.setattr(torch, "load", lambda *a, **kw: {"model": {}, "param_dict": {"seq_len": 8}})
    monkeypatch.setattr(torch.cuda, "is_available", lambda: available)
    monkeypatch.setattr(tracknet, "_build_torch_model", lambda *args: ControlledModel())
    model = tracknet.TrackNetV3(tmp_path / "unused.pt", backend="torch-cuda", precision=precision)
    param = next(model._torch.parameters())
    assert str(param.device) == device and param.dtype == dtype
    assert model.runtime["device"] == device
    assert model.runtime["backend_fallback"] is (not available)
