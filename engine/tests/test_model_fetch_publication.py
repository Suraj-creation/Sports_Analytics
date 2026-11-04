"""An overlapping download must not publish or pin another writer's partial bytes."""

import hashlib
import io
import json
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import pytest
import yaml

from bai_engine.runtime.registry import ModelError, ModelRegistry


def _models(tmp_path):
    models = tmp_path / "models"
    models.mkdir()
    url = "https://models.invalid/checkpoint.pt"
    manifest = {"models": {"checkpoint": {
        "task": "shuttle",
        "format": "torch",
        "source": {"url": url},
        "sha256": "pin-on-first-fetch",
    }}}
    (models / "manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    return models, url


def test_incomplete_concurrent_fetch_cannot_become_first_use_pin(monkeypatch, tmp_path):
    models, url = _models(tmp_path)
    first_registry, second_registry = ModelRegistry(models), ModelRegistry(models)
    payload = b"trusted complete checkpoint\n" * 4096
    digest = hashlib.sha256(payload).hexdigest()
    first_copied, second_partial = threading.Event(), threading.Event()
    release_first, release_second = threading.Event(), threading.Event()
    request_lock = threading.Lock()
    requests = 0

    class Response(io.BytesIO):
        def __init__(self, first):
            super().__init__(payload)
            self.first = first

        def read(self, size=-1):
            if self.first and self.tell() == len(payload):
                # The first writer has copied the complete response but has
                # not yet closed/published its staging file.
                first_copied.set()
                if not release_first.wait(15):
                    raise TimeoutError("first response was not released")
            elif not self.first:
                if self.tell() == 0:
                    # Exceed the buffered writer size so this prefix reaches
                    # the staging file before the next read blocks.
                    return super().read(16 * 1024)
                if self.tell() == 16 * 1024:
                    second_partial.set()
                    if not release_second.wait(15):
                        raise TimeoutError("second response was not released")
            return super().read(size)

    def open_response(request_url, timeout):
        nonlocal requests
        assert request_url == url and timeout > 0
        with request_lock:
            requests += 1
            return Response(first=requests == 1)

    monkeypatch.setattr(urllib.request, "urlopen", open_response)

    def load(registry):
        try:
            with registry.open_verified("checkpoint") as artifact:
                return artifact.stream.read(), artifact.sha256
        except Exception as error:
            return error

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(load, first_registry)
        try:
            assert first_copied.wait(15), "first download did not finish copying"
            second = executor.submit(load, second_registry)
            assert second_partial.wait(15), "second download did not copy its prefix"
            # With a shared .part path, this publishes the SECOND writer's
            # incomplete response and lets open_verified pin that snapshot.
            release_first.set()
            first_result = first.result(timeout=15)
        finally:
            release_first.set()
            release_second.set()
        second_result = second.result(timeout=15)

    assert first_result == (payload, digest), "a partial concurrent download reached the verified loader"
    assert second_result == (payload, digest), "an independent download lost its staging artifact"
    pins = json.loads((models / "cache" / "lock.json").read_text(encoding="utf-8"))
    assert pins == {"checkpoint": digest}
    artifact = models / "cache" / "checkpoint" / "checkpoint.pt"
    assert artifact.read_bytes() == payload
    assert list(artifact.parent.iterdir()) == [artifact]


def test_interrupted_fetch_removes_only_its_unpublished_staging_file(monkeypatch, tmp_path):
    models, url = _models(tmp_path)
    registry = ModelRegistry(models)
    artifact = models / "cache" / "checkpoint" / "checkpoint.pt"
    artifact.parent.mkdir()
    unrelated = artifact.parent / "user-notes.txt"
    unrelated.write_text("preserve", encoding="utf-8")

    class InterruptedResponse(io.BytesIO):
        def read(self, size=-1):
            if self.tell():
                raise OSError("injected interrupted download")
            return super().read(size)

    def open_response(request_url, timeout):
        assert request_url == url and timeout > 0
        return InterruptedResponse(b"incomplete checkpoint" * 4096)

    monkeypatch.setattr(urllib.request, "urlopen", open_response)
    with pytest.raises(OSError, match="injected interrupted download"), registry.open_verified("checkpoint"):
        pytest.fail("an incomplete transfer reached the loader")
    assert not artifact.exists()
    assert not (models / "cache" / "lock.json").exists()
    assert list(artifact.parent.iterdir()) == [unrelated]
    assert unrelated.read_text(encoding="utf-8") == "preserve"


def test_conflicting_concurrent_fetch_cannot_replace_the_pinned_artifact(monkeypatch, tmp_path):
    models, url = _models(tmp_path)
    first_registry, second_registry = ModelRegistry(models), ModelRegistry(models)
    trusted = b"trusted complete checkpoint"
    conflicting = b"different complete checkpoint"
    second_requested, release_second = threading.Event(), threading.Event()
    request_lock = threading.Lock()
    requests = 0

    def open_response(request_url, timeout):
        nonlocal requests
        assert request_url == url and timeout > 0
        with request_lock:
            requests += 1
            delayed = requests == 1
        if delayed:
            # This caller already saw an absent artifact. Hold its response
            # until another registry has published and pinned complete bytes.
            second_requested.set()
            if not release_second.wait(15):
                raise TimeoutError("conflicting response was not released")
        return io.BytesIO(conflicting if delayed else trusted)

    monkeypatch.setattr(urllib.request, "urlopen", open_response)

    def load(registry):
        with registry.open_verified("checkpoint") as artifact:
            return artifact.stream.read()

    with ThreadPoolExecutor(max_workers=1) as executor:
        second = executor.submit(load, second_registry)
        try:
            assert second_requested.wait(15), "conflicting request did not start"
            assert load(first_registry) == trusted
        finally:
            release_second.set()
        with pytest.raises(ModelError, match="sha256 mismatch"):
            second.result(timeout=15)

    artifact = models / "cache" / "checkpoint" / "checkpoint.pt"
    assert artifact.read_bytes() == trusted, "a rejected download replaced the previously verified artifact"
    pins = json.loads((models / "cache" / "lock.json").read_text(encoding="utf-8"))
    assert pins == {"checkpoint": hashlib.sha256(trusted).hexdigest()}
    assert list(artifact.parent.iterdir()) == [artifact]
