"""Small real ONNX graphs exercise cache lifecycle without loading model weights."""

import hashlib
import io
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import onnxruntime as ort
import pytest
import torch

from bai_badminton.perception import tracknet


def _varint(value):
    encoded = bytearray()
    while value > 127:
        encoded.append((value & 127) | 128)
        value >>= 7
    encoded.append(value)
    return bytes(encoded)


def _field(number, value):
    if isinstance(value, str):
        value = value.encode()
    if isinstance(value, bytes):
        return _varint((number << 3) | 2) + _varint(len(value)) + value
    return _varint(number << 3) + _varint(value)


def _graph(path, *, input_name="frames", input_channels=27, output_channels=8, dtype=1, note=""):
    # Tiny Slice graph serialized directly from the public ONNX protobuf schema:
    # https://github.com/onnx/onnx/blob/main/onnx/onnx.proto . No exporter package needed.
    def value_info(name, channels):
        shape = _field(1, _field(2, "batch"))
        shape += b"".join(_field(1, _field(1, size)) for size in (channels, 288, 512))
        tensor_type = _field(1, dtype) + _field(2, shape)
        return _field(1, name) + _field(2, _field(1, tensor_type))

    node = b"".join(_field(1, name) for name in (input_name, "start", "end", "axis", "step"))
    node += _field(2, "heatmaps") + _field(4, "Slice")
    graph = _field(1, node) + _field(2, "small-tracknet-contract")
    for name, value in (("start", 0), ("end", output_channels), ("axis", 1), ("step", 1)):
        # TensorProto: dims=[1], data_type=INT64(7), int64_data=[value], name.
        graph += _field(5, _field(1, 1) + _field(2, 7) + _field(7, value) + _field(8, name))
    graph += _field(11, value_info(input_name, input_channels))
    graph += _field(12, value_info("heatmaps", output_channels))
    # ModelProto: IR9, doc_string, graph, default ONNX opset17.
    path.write_bytes(_field(1, 9) + _field(6, note) + _field(7, graph) + _field(8, _field(2, 17)))


@pytest.fixture
def controlled(monkeypatch, tmp_path):
    class Model:
        def load_state_dict(self, _state, strict):
            return [], []

        def eval(self):
            return self

    monkeypatch.setattr(tracknet, "_build_torch_model", lambda *_args: Model())
    monkeypatch.setattr(torch, "load", lambda *_args, **_kwargs: {"model": {}, "param_dict": {"seq_len": 8}})
    exports, sessions = [], []
    session_factory = ort.InferenceSession

    def session(path, *args, **kwargs):
        sessions.append(path)
        return session_factory(path, *args, **kwargs)

    def export(_self, path):
        exports.append(path)
        _graph(path)

    monkeypatch.setattr(ort, "InferenceSession", session)
    monkeypatch.setattr(tracknet.TrackNetV3, "export_onnx", export)
    weights, cache = tmp_path / "weights.pt", tmp_path / "onnx"
    weights.write_bytes(b"trusted checkpoint")
    cache.mkdir()
    return weights, cache, exports, sessions


def _load(controlled, **kwargs):
    weights, cache, _exports, _sessions = controlled
    return tracknet.TrackNetV3(weights, backend="onnx-cpu", onnx_dir=cache, **kwargs)


def test_existing_corrupt_graph_is_rebuilt_before_loading(controlled):
    _weights, _cache, exports, sessions = controlled
    _load(controlled)
    Path(sessions[-1]).write_bytes(b"truncated graph")
    model = _load(controlled)
    assert len(exports) == 2
    assert model.runtime["onnx_sha256"] == hashlib.sha256(Path(sessions[-1]).read_bytes()).hexdigest()


def test_existing_valid_graph_with_changed_content_is_rebuilt(controlled):
    _weights, _cache, exports, sessions = controlled
    _load(controlled)
    _graph(Path(sessions[-1]), note="same schema but different graph bytes")
    _load(controlled)
    assert len(exports) == 2


@pytest.mark.parametrize(
    "changed",
    [
        {"input_name": "other_input"},
        {"input_channels": 24},
        {"output_channels": 7},
        {"dtype": 11},  # TensorProto.DOUBLE
    ],
)
def test_export_with_wrong_tensor_contract_is_not_published(monkeypatch, controlled, changed):
    _weights, cache, _exports, _sessions = controlled

    def wrong_contract(_self, path):
        _graph(path, **changed)

    monkeypatch.setattr(tracknet.TrackNetV3, "export_onnx", wrong_contract)
    with pytest.raises(ValueError, match="contract"):
        _load(controlled)
    assert not list(cache.iterdir())


def test_expected_checkpoint_digest_is_checked_before_deserialization(monkeypatch, controlled):
    _weights, cache, exports, _sessions = controlled
    loads = []
    monkeypatch.setattr(torch, "load", lambda *_args, **_kwargs: loads.append(True))
    with pytest.raises(ValueError, match="sha256 mismatch"):
        _load(controlled, expected_sha256="0" * 64)
    assert not loads and not exports and not list(cache.iterdir())


def test_verified_checkpoint_stream_is_used_instead_of_reopening_path(monkeypatch, controlled):
    weights, _cache, _exports, _sessions = controlled
    trusted = b"verified snapshot"
    weights.write_bytes(b"replaced checkpoint path")
    loaded = []

    def load(stream, **_kwargs):
        loaded.append(stream.read())
        return {"model": {}, "param_dict": {"seq_len": 8}}

    monkeypatch.setattr(torch, "load", load)
    model = _load(
        controlled,
        checkpoint_stream=io.BytesIO(trusted),
        expected_sha256=hashlib.sha256(trusted).hexdigest(),
    )
    assert loaded == [trusted]
    assert model.runtime["checkpoint_sha256"] == hashlib.sha256(trusted).hexdigest()


def test_provider_factory_receives_verified_graph_digest(controlled):
    _weights, _cache, _exports, sessions = controlled
    digests = []

    def providers(digest):
        digests.append(digest)
        return ["CPUExecutionProvider"]

    model = _load(controlled, provider_factory=providers)
    assert digests == [hashlib.sha256(Path(sessions[-1]).read_bytes()).hexdigest()]
    assert model.runtime["onnx_sha256"] == digests[0]


def test_concurrent_exports_publish_a_complete_reusable_graph(monkeypatch, controlled):
    _weights, cache, exports, sessions = controlled
    rendezvous = threading.Barrier(2)
    export_lock = threading.Lock()

    def concurrent_export(_self, path):
        with export_lock:
            exports.append(path)
            note = str(len(exports))
        _graph(path, note=note)
        rendezvous.wait(timeout=15)

    monkeypatch.setattr(tracknet.TrackNetV3, "export_onnx", concurrent_export)
    with ThreadPoolExecutor(max_workers=2) as executor:
        models = list(executor.map(lambda _index: _load(controlled), range(2)))
    assert all(model.runtime["onnx_sha256"] for model in models)
    assert len(exports) == 2
    _load(controlled)
    assert len(exports) == 2
    assert Path(sessions[-1]).is_file()
    assert not any(path.name.startswith(".tracknet-") for path in cache.iterdir())
