"""The application loader hands TrackNet the registry's verified snapshot."""

import hashlib
from types import SimpleNamespace

import yaml

from bai_badminton.perception import pipeline, tracknet
from bai_engine.config import ModelChoice
from bai_engine.runtime.registry import ModelRegistry


def _setup(tmp_path):
    models = tmp_path / "models"
    models.mkdir()
    digest = hashlib.sha256(b"trusted checkpoint").hexdigest()
    (models / "manifest.yaml").write_text(yaml.safe_dump({"models": {"tracknetv3": {
        "task": "shuttle", "version": "3.0", "format": "torch",
        "source": {"file": "weights.pt"}, "sha256": digest,
    }}}), encoding="utf-8")
    registry = ModelRegistry(models)
    path = models / "cache" / "tracknetv3" / "weights.pt"
    path.parent.mkdir()
    path.write_bytes(b"trusted checkpoint")
    perception = pipeline.BadmintonPerception.__new__(pipeline.BadmintonPerception)
    perception.models, perception.runtimes, perception.degraded = {}, {}, []
    return perception, registry, path, digest


def test_shuttle_application_load_consumes_snapshot_and_scopes_provider_to_graph(monkeypatch, tmp_path):
    perception, registry, path, digest = _setup(tmp_path)
    observed = {}

    def build(weights, **kwargs):
        path.write_bytes(b"path replaced after registry verification")
        stream = kwargs["checkpoint_stream"]
        observed.update(path=weights, data=stream.read(), digest=kwargs["expected_sha256"], stream=stream)
        assert kwargs["provider_factory"]("f" * 64) == ["CPUExecutionProvider"]
        return SimpleNamespace(runtime={"backend_fallback": False})

    def providers(_choice, _cache, *, model_digest=None):
        observed["graph_digest"] = model_digest
        return ["CPUExecutionProvider"]

    monkeypatch.setattr(tracknet, "TrackNetV3", build)
    monkeypatch.setattr(perception, "_providers", providers)
    model = perception._load_shuttle(ModelChoice(model="tracknetv3", backend="onnx-cpu"), registry, tmp_path)
    assert model is not None and not perception.degraded
    assert observed["path"] == path and observed["data"] == b"trusted checkpoint"
    assert observed["digest"] == digest and observed["graph_digest"] == "f" * 64
    assert observed["stream"].closed


def test_changed_checkpoint_is_degraded_before_shuttle_deserialization(monkeypatch, tmp_path):
    perception, registry, path, _digest = _setup(tmp_path)
    path.write_bytes(b"untrusted replacement")

    def forbidden_load(*_args, **_kwargs):
        raise AssertionError("unverified checkpoint reached TrackNet")

    monkeypatch.setattr(tracknet, "TrackNetV3", forbidden_load)
    assert perception._load_shuttle(ModelChoice(model="tracknetv3", backend="torch-cpu"), registry, tmp_path) is None
    assert len(perception.degraded) == 1
    assert "sha256 mismatch" in perception.degraded[0].reason
