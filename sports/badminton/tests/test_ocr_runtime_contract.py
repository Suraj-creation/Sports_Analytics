"""Configured OCR providers and actual artifact provenance must agree."""

import hashlib
from types import SimpleNamespace

import pytest

from bai_badminton.perception.pipeline import BadmintonPerception
from bai_badminton.perception.scoreboard import ScoreboardReader
from bai_engine.config import ModelChoice


def fake_rapidocr(monkeypatch, tmp_path, providers):
    import rapidocr

    calls = []
    files = {
        "det": "PP-OCRv6_det_small.onnx",
        "cls": "ch_ppocr_mobile_v2.0_cls_mobile.onnx",
        "rec": "PP-OCRv6_rec_small.onnx",
    }
    cfg, components = {}, {}
    for stage, filename in files.items():
        path = tmp_path / filename
        path.write_bytes(stage.encode())
        session = SimpleNamespace(
            _model_path=str(path),
            get_providers=lambda: list(providers),
            get_provider_options=lambda: {provider: {} for provider in providers},
        )
        cfg[stage.title()] = SimpleNamespace(ocr_version=SimpleNamespace(value="PP-OCRv6"))
        components[f"text_{stage}"] = SimpleNamespace(session=SimpleNamespace(session=session))
        components[f"_load_{stage}_model"] = lambda: None

    def create(*, params):
        calls.append(params)
        return SimpleNamespace(cfg=SimpleNamespace(**cfg), **components)

    monkeypatch.setattr(rapidocr, "RapidOCR", create)
    monkeypatch.setattr("bai_badminton.perception.scoreboard.version", lambda package: "3.10.0")
    return calls


@pytest.mark.parametrize(
    "backend,providers",
    [
        ("onnx-cpu", ["CPUExecutionProvider"]),
        ("onnx-cuda", ["CUDAExecutionProvider", "CPUExecutionProvider"]),
    ],
)
def test_loader_honors_backend_without_changing_weights_or_preprocessing(monkeypatch, tmp_path, backend, providers):
    calls = fake_rapidocr(monkeypatch, tmp_path, providers)
    reader = ScoreboardReader.load(25, backend=backend)
    assert calls == [{"EngineConfig.onnxruntime.use_cuda": backend == "onnx-cuda"}]
    assert reader.every == 25
    assert reader.runtime["package_version"] == "3.10.0"
    assert reader.runtime["requested_backend"] == backend
    assert reader.runtime["backend_fallback"] is False
    for stage, metadata in reader.runtime["stages"].items():
        assert metadata["sha256"] == hashlib.sha256(stage.encode()).hexdigest()
        assert metadata["providers"] == providers
    assert reader.runtime["stages"]["det"]["model_file"] == "PP-OCRv6_det_small.onnx"
    assert reader.runtime["stages"]["cls"]["model_file"] == "ch_ppocr_mobile_v2.0_cls_mobile.onnx"
    assert reader.model_ref.startswith("rapidocr@3.10.0+")
    assert "rapidocr_v4@4" not in reader.model_ref


def test_cuda_provider_fallback_is_observed_not_assumed(monkeypatch, tmp_path):
    fake_rapidocr(monkeypatch, tmp_path, ["CPUExecutionProvider"])
    reader = ScoreboardReader.load(25, backend="onnx-cuda")
    assert reader.runtime["backend_fallback"] is True
    assert all(stage["providers"] == ["CPUExecutionProvider"] for stage in reader.runtime["stages"].values())


def test_wrong_engine_is_rejected_instead_of_silently_running_cpu():
    with pytest.raises(ValueError, match="unsupported RapidOCR backend"):
        ScoreboardReader.load(25, backend="torch-cuda")


def test_pipeline_passes_backend_records_actual_ref_and_exposes_fallback(monkeypatch):
    perception = BadmintonPerception.__new__(BadmintonPerception)
    perception.models, perception.degraded = {}, []
    perception.profile = SimpleNamespace(ocr_every_s=1.2)
    calls = []
    reader = SimpleNamespace(
        model_ref="rapidocr@3.10.0+actualweights",
        runtime={
            "backend_fallback": True,
            "stages": {"det": {"providers": ["CPUExecutionProvider"]}},
        },
    )

    def load(*, every, backend):
        calls.append((every, backend))
        return reader

    monkeypatch.setattr(ScoreboardReader, "load", load)
    choice = ModelChoice(model="rapidocr_v4", backend="onnx-cuda")
    registry = SimpleNamespace(get=lambda _: SimpleNamespace(format="package", source={"package": "rapidocr"}))
    assert perception._load_ocr(choice, registry, 25) is reader
    assert calls == [(30, "onnx-cuda")]
    assert perception.models["ocr"] == reader.model_ref
    assert perception.degraded[0].stage == "ocr_backend"
    assert "CPUExecutionProvider" in perception.degraded[0].reason


def test_non_ocr_artifact_cannot_be_reported_as_the_loaded_scoreboard_model():
    perception = BadmintonPerception.__new__(BadmintonPerception)
    perception.models, perception.degraded = {}, []
    registry = SimpleNamespace(get=lambda _: SimpleNamespace(format="onnx", source={"file": "person.onnx"}))
    assert perception._load_ocr(ModelChoice(model="person", backend="onnx-cuda"), registry, 25) is None
    assert perception.models == {}
    assert "not a RapidOCR package alias" in perception.degraded[0].reason


def test_disabled_ocr_backend_does_not_initialize_models(monkeypatch):
    perception = BadmintonPerception.__new__(BadmintonPerception)

    def forbidden(**kwargs):
        raise AssertionError("disabled backend initialized OCR")

    monkeypatch.setattr(ScoreboardReader, "load", forbidden)
    assert perception._load_ocr(ModelChoice(model="rapidocr_v4", backend="none"), None, 25) is None


def test_capability_reports_actual_ocr_versions_weights_and_fallback(tmp_path):
    from test_plugin_discipline import make_session

    session = make_session(tmp_path, "singles")
    session.perception.models["ocr"] = "rapidocr@3.10.0+actualweights"
    session.perception.scoreboard = SimpleNamespace(
        runtime={
            "package_version": "3.10.0",
            "requested_backend": "onnx-cuda",
            "backend_fallback": True,
            "stages": {
                "det": {
                    "model_file": "PP-OCRv6_det_small.onnx",
                    "providers": ["CPUExecutionProvider"],
                    "sha256": "a" * 64,
                }
            },
        }
    )
    capability = session.capabilities()["ocr"]
    assert capability["status"] == "fallback"
    assert capability["active_model"] == "rapidocr@3.10.0+actualweights"
    assert capability["runtime"] == session.perception.scoreboard.runtime
    assert "PP-OCRv6_det_small.onnx via CPUExecutionProvider" in capability["reason"]
    assert "onnx-cuda" in capability["reason"]
