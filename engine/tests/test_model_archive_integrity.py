"""Verified archive bytes must determine complete, reusable derived model bytes."""

import hashlib
import io
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor

import pytest
import yaml

from bai_engine.runtime.registry import ModelError, ModelRegistry


def _zip(entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    return stream.getvalue()


def _install(tmp_path, data):
    models = tmp_path / "models"
    models.mkdir(exist_ok=True)
    manifest = {"models": {"pose": {
        "task": "pose", "version": "test", "format": "onnx-zip",
        "source": {"file": "bundle.zip"}, "sha256": hashlib.sha256(data).hexdigest(),
    }}}
    (models / "manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    registry = ModelRegistry(models)
    path = models / "cache" / "pose" / "bundle.zip"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return registry, path


def test_changed_verified_archive_cannot_reuse_an_old_graph(tmp_path):
    first, _ = _install(tmp_path, _zip({"model.onnx": b"graph-v1", "weights.bin": b"weights-v1"}))
    assert first.path("pose", fetch=False).read_bytes() == b"graph-v1"
    second, _ = _install(tmp_path, _zip({"model.onnx": b"graph-v2", "weights.bin": b"weights-v2"}))
    graph = second.path("pose", fetch=False)
    assert graph.read_bytes() == b"graph-v2"
    assert (graph.parent / "weights.bin").read_bytes() == b"weights-v2"


@pytest.mark.parametrize("member", ["model.onnx", "weights.bin"])
def test_mutated_extracted_artifact_cannot_be_silently_reused(tmp_path, member):
    expected = {"model.onnx": b"graph", "weights.bin": b"external-weights"}
    registry, _ = _install(tmp_path, _zip(expected))
    graph = registry.path("pose", fetch=False)
    (graph.parent / member).write_bytes(b"corrupted")
    # Either explicit rejection or reconstruction from verified archive bytes is
    # safe. Returning an unchecked mutated graph or external-data file is not.
    try:
        restored = registry.path("pose", fetch=False)
    except ModelError:
        return
    assert (restored.parent / member).read_bytes() == expected[member]


def test_failed_extraction_does_not_make_partial_archive_a_cache_hit(tmp_path):
    data = _zip({"model.onnx": b"good-first-file", "weights.bin": b"broken-payload"})
    damaged = data.replace(b"broken-payload", b"xroken-payload", 1)  # retain the original member CRC
    registry, _ = _install(tmp_path, damaged)
    for _ in range(2):
        with pytest.raises((zipfile.BadZipFile, ModelError)):
            registry.path("pose", fetch=False)


def test_concurrent_reader_never_receives_partly_extracted_graph(tmp_path, monkeypatch):
    expected = b"a complete graph payload"
    first, _ = _install(tmp_path, _zip({"model.onnx": expected}))
    second = ModelRegistry(first.models_dir)
    blocked, release = threading.Event(), threading.Event()
    original_open = zipfile.ZipFile.open
    lock = threading.Lock()
    wrapped_once = False

    class PausedReader:
        def __init__(self, stream):
            self.stream = stream
            self.reads = 0

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.stream.close()

        def read(self, size=-1):
            self.reads += 1
            if self.reads == 1:
                return self.stream.read(4)
            if self.reads == 2:
                blocked.set()
                assert release.wait(timeout=10)
            return self.stream.read(size)

        def __getattr__(self, name):
            return getattr(self.stream, name)

    def controlled_open(archive, name, *args, **kwargs):
        nonlocal wrapped_once
        stream = original_open(archive, name, *args, **kwargs)
        member = name.filename if isinstance(name, zipfile.ZipInfo) else name
        with lock:
            if member == "model.onnx" and not wrapped_once:
                wrapped_once = True
                return PausedReader(stream)
        return stream

    monkeypatch.setattr(zipfile.ZipFile, "open", controlled_open)
    with ThreadPoolExecutor(max_workers=2) as workers:
        writer = workers.submit(first.path, "pose", fetch=False)
        try:
            assert blocked.wait(timeout=10)
            reader = workers.submit(second.path, "pose", fetch=False)
            try:
                observed = reader.result(timeout=0.5).read_bytes()
            except TimeoutError:
                observed = None  # Serialized extraction is also valid.
        finally:
            release.set()
        assert writer.result(timeout=10).read_bytes() == expected
        assert reader.result(timeout=10).read_bytes() == expected
    assert observed is None or observed == expected


def test_sibling_prefix_traversal_is_rejected_even_when_zipfile_would_sanitize_it(tmp_path):
    registry, _ = _install(tmp_path, _zip({"../extracted-sibling/model.onnx": b"graph"}))
    with pytest.raises(ModelError, match=r"zip|archive|path"):
        registry.path("pose", fetch=False)
