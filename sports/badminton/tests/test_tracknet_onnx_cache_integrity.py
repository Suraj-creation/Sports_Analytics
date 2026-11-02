"""TrackNet's derived ONNX must correspond to the loaded checkpoint and exporter."""

import sys
from types import SimpleNamespace

import pytest
import torch

from bai_badminton.perception import tracknet


class _Model:
    def load_state_dict(self, state, strict):
        return [], []

    def eval(self):
        return self


@pytest.fixture
def controlled_onnx(monkeypatch, tmp_path):
    source = tmp_path / "tracknet_source.py"
    source.write_bytes(b"exporter version A")
    monkeypatch.setattr(tracknet, "__file__", str(source))
    monkeypatch.setattr(tracknet, "_build_torch_model", lambda *_: _Model())
    monkeypatch.setattr(torch, "load", lambda *_args, **_kwargs: {"model": {}, "param_dict": {"seq_len": 8}})
    used_paths = []
    exports = []

    class Session:
        def __init__(self, path, providers, **_kwargs):
            used_paths.append(path)

        def get_providers(self):
            return ["CPUExecutionProvider"]

        def get_inputs(self):
            return [SimpleNamespace(name="frames", type="tensor(float)", shape=["batch", 27, 288, 512])]

        def get_outputs(self):
            return [SimpleNamespace(name="heatmaps", type="tensor(float)", shape=["batch", 8, 288, 512])]

    def export(_self, path):
        exports.append(path)
        path.write_bytes(b"complete exported model")

    monkeypatch.setitem(
        sys.modules, "onnxruntime", SimpleNamespace(InferenceSession=Session, SessionOptions=SimpleNamespace)
    )
    monkeypatch.setattr(tracknet.TrackNetV3, "export_onnx", export)
    weights = tmp_path / "weights.pt"
    weights.write_bytes(b"checkpoint A")
    cache = tmp_path / "onnx"
    cache.mkdir()
    return weights, cache, source, used_paths, exports


def test_changed_checkpoint_does_not_reuse_legacy_or_previous_export(controlled_onnx):
    weights, cache, _source, used, exports = controlled_onnx
    legacy = cache / "tracknetv3_seq8_concat.onnx"
    legacy.write_bytes(b"old legacy cache")

    tracknet.TrackNetV3(weights, backend="onnx-cpu", onnx_dir=cache)
    first = used[-1]
    tracknet.TrackNetV3(weights, backend="onnx-cpu", onnx_dir=cache)
    assert used[-1] == first and len(exports) == 1
    assert first != str(legacy)

    weights.write_bytes(b"checkpoint B")
    tracknet.TrackNetV3(weights, backend="onnx-cpu", onnx_dir=cache)
    assert used[-1] != first
    assert len(exports) == 2
    assert legacy.read_bytes() == b"old legacy cache"


def test_changed_exporter_source_does_not_reuse_previous_export(controlled_onnx):
    weights, cache, source, used, exports = controlled_onnx
    tracknet.TrackNetV3(weights, backend="onnx-cpu", onnx_dir=cache)
    first = used[-1]
    source.write_bytes(b"exporter version B")
    tracknet.TrackNetV3(weights, backend="onnx-cpu", onnx_dir=cache)
    assert used[-1] != first
    assert len(exports) == 2


def test_changed_loaded_model_builder_does_not_reuse_previous_export(monkeypatch, controlled_onnx):
    weights, cache, _source, used, exports = controlled_onnx
    tracknet.TrackNetV3(weights, backend="onnx-cpu", onnx_dir=cache)
    first = used[-1]

    def replacement_builder(*_args):
        model = _Model()
        return model

    monkeypatch.setattr(tracknet, "_build_torch_model", replacement_builder)
    tracknet.TrackNetV3(weights, backend="onnx-cpu", onnx_dir=cache)
    assert used[-1] != first
    assert len(exports) == 2


def test_changed_torch_version_does_not_reuse_previous_export(monkeypatch, controlled_onnx):
    weights, cache, _source, used, exports = controlled_onnx
    monkeypatch.setattr(torch, "__version__", "exporter-version-A")
    tracknet.TrackNetV3(weights, backend="onnx-cpu", onnx_dir=cache)
    first = used[-1]
    monkeypatch.setattr(torch, "__version__", "exporter-version-B")
    tracknet.TrackNetV3(weights, backend="onnx-cpu", onnx_dir=cache)
    assert used[-1] != first
    assert len(exports) == 2


def test_failed_export_does_not_publish_a_partial_cache(monkeypatch, controlled_onnx):
    weights, cache, _source, used, _exports = controlled_onnx

    def fail(_self, path):
        path.write_bytes(b"partial")
        raise RuntimeError("interrupted export")

    monkeypatch.setattr(tracknet.TrackNetV3, "export_onnx", fail)
    with pytest.raises(RuntimeError, match="interrupted export"):
        tracknet.TrackNetV3(weights, backend="onnx-cpu", onnx_dir=cache)
    assert list(cache.iterdir()) == []
    assert used == []


@pytest.mark.parametrize("raise_during_export", [False, True])
def test_sidecar_export_is_not_published_and_temporary_files_are_removed(
    monkeypatch, controlled_onnx, raise_during_export
):
    weights, cache, _source, used, _exports = controlled_onnx

    def sidecar_export(_self, path):
        path.write_bytes(b"graph referencing external data")
        path.with_name(path.name + ".data").write_bytes(b"external weights")
        if raise_during_export:
            raise RuntimeError("export interrupted after sidecar")

    monkeypatch.setattr(tracknet.TrackNetV3, "export_onnx", sidecar_export)
    error = RuntimeError if raise_during_export else ValueError
    with pytest.raises(error):
        tracknet.TrackNetV3(weights, backend="onnx-cpu", onnx_dir=cache)
    assert list(cache.iterdir()) == []
    assert used == []


def test_export_asks_torch_for_embedded_weights(monkeypatch, tmp_path):
    calls = []

    class ExportModel:
        def float(self):
            return self

        def cpu(self):
            return self

    monkeypatch.setattr(torch, "zeros", lambda *_: object())
    monkeypatch.setattr(torch.onnx, "export", lambda *args, **kwargs: calls.append(kwargs))
    model = tracknet.TrackNetV3.__new__(tracknet.TrackNetV3)
    model._torch = ExportModel()
    model.in_dim = 27
    model.export_onnx(tmp_path / "graph.onnx")
    assert calls[0]["external_data"] is False


def test_checkpoint_changed_during_load_is_not_exported(monkeypatch, controlled_onnx):
    weights, cache, _source, used, exports = controlled_onnx

    def changing_load(_stream, **_kwargs):
        weights.write_bytes(b"different checkpoint")
        return {"model": {}, "param_dict": {"seq_len": 8}}

    monkeypatch.setattr(torch, "load", changing_load)
    with pytest.raises(ValueError, match="checkpoint changed"):
        tracknet.TrackNetV3(weights, backend="onnx-cpu", onnx_dir=cache)
    assert list(cache.iterdir()) == []
    assert not used and not exports
