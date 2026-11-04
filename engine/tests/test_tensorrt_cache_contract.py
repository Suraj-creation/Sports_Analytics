"""ORT's own caches must be separated by their complete compatibility inputs."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from bai_engine.runtime.device import ort_providers


@pytest.fixture
def runtime(monkeypatch):
    monkeypatch.setitem(
        sys.modules,
        "onnxruntime",
        SimpleNamespace(
            __version__="1.29.0",
            get_available_providers=lambda: [
                "TensorrtExecutionProvider", "CUDAExecutionProvider", "CPUExecutionProvider"
            ],
        ),
    )
    return {
        "onnxruntime": "1.29.0",
        "tensorrt": "10.9.0",
        "cuda_runtime": "12.6",
        "cuda_driver": "560.35.03",
        "gpu_uuid": "GPU-test-a",
        "gpu_compute_capability": "6.1",
        "device_id": "0",
    }


def _options(root, context, *, digest="a" * 64, fp16=True):
    providers = ort_providers(
        "tensorrt", engine_cache=root, fp16=fp16, model_digest=digest, cache_context=context
    )
    return providers[0][1]


def test_engine_and_timing_caches_share_one_compatibility_namespace(tmp_path, runtime):
    opts = _options(tmp_path, runtime)
    namespace = Path(opts["trt_engine_cache_path"])
    assert namespace.parent == tmp_path
    assert namespace.is_dir()
    assert opts["trt_engine_cache_enable"] is True
    assert opts["trt_timing_cache_enable"] is True
    assert Path(opts["trt_timing_cache_path"]) == namespace
    assert _options(tmp_path, dict(runtime))["trt_engine_cache_path"] == str(namespace)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("onnxruntime", "1.30.0"),
        ("tensorrt", "10.10.0"),
        ("cuda_runtime", "12.8"),
        ("cuda_driver", "570.0"),
        ("gpu_uuid", "GPU-test-b"),
        ("gpu_compute_capability", "8.9"),
        ("device_id", "1"),
    ],
)
def test_runtime_or_hardware_change_does_not_reuse_an_engine(tmp_path, runtime, field, value):
    first = _options(tmp_path, runtime)["trt_engine_cache_path"]
    changed = {**runtime, field: value}
    assert _options(tmp_path, changed)["trt_engine_cache_path"] != first


def test_model_and_precision_change_do_not_reuse_an_engine(tmp_path, runtime):
    first = _options(tmp_path, runtime)["trt_engine_cache_path"]
    assert _options(tmp_path, runtime, digest="b" * 64)["trt_engine_cache_path"] != first
    assert _options(tmp_path, runtime, fp16=False)["trt_engine_cache_path"] != first


@pytest.mark.parametrize("incomplete", [None, {}, {"onnxruntime": "1.29.0"}])
def test_incomplete_runtime_identity_disables_persistent_caches(tmp_path, runtime, incomplete):
    # None explicitly exercises failed discovery rather than trusting a guessed identity.
    if incomplete is None:
        incomplete = {**runtime, "gpu_uuid": None}
    opts = _options(tmp_path, incomplete)
    assert not opts.get("trt_engine_cache_enable", False)
    assert not opts.get("trt_timing_cache_enable", False)
    assert not list(tmp_path.iterdir())


def test_missing_graph_digest_disables_persistent_caches(tmp_path, runtime):
    opts = _options(tmp_path, runtime, digest=None)
    assert not opts.get("trt_engine_cache_enable", False)
    assert not opts.get("trt_timing_cache_enable", False)
