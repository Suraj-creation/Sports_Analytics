"""A verified loader must consume the bytes checked against the registry pin."""

import hashlib
import json

import pytest
import yaml

from bai_engine.runtime.registry import ModelError, ModelRegistry


def _registry(tmp_path, data=b"trusted checkpoint", *, pinned=True):
    models = tmp_path / "models"
    models.mkdir()
    digest = hashlib.sha256(data).hexdigest()
    manifest = {
        "models": {
            "checkpoint": {
                "task": "shuttle",
                "version": "test",
                "format": "torch",
                "source": {"file": "checkpoint.pt"},
                "sha256": digest if pinned else "pin-on-first-fetch",
            }
        }
    }
    (models / "manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    registry = ModelRegistry(models)
    path = models / "cache" / "checkpoint" / "checkpoint.pt"
    path.parent.mkdir(parents=True)
    path.write_bytes(data)
    return registry, path, digest


def test_verified_snapshot_survives_original_path_replacement(tmp_path):
    registry, path, digest = _registry(tmp_path)
    with registry.open_verified("checkpoint", fetch=False) as artifact:
        assert artifact.path == path
        assert artifact.sha256 == digest
        replacement = path.with_suffix(".replacement")
        replacement.write_bytes(b"different checkpoint")
        replacement.replace(path)
        assert artifact.stream.read() == b"trusted checkpoint"
    assert artifact.stream.closed


def test_verified_snapshot_survives_in_place_original_mutation(tmp_path):
    registry, path, _digest = _registry(tmp_path)
    with registry.open_verified("checkpoint", fetch=False) as artifact:
        path.write_bytes(b"in-place replacement")
        assert artifact.stream.read() == b"trusted checkpoint"


def test_snapshot_rejects_a_replaced_previously_verified_path(tmp_path):
    registry, path, _digest = _registry(tmp_path)
    assert registry.path("checkpoint", fetch=False) == path
    path.write_bytes(b"replacement after path verification")
    with pytest.raises(ModelError, match="sha256 mismatch"):
        with registry.open_verified("checkpoint", fetch=False):
            pytest.fail("unverified bytes reached the loader")


def test_first_use_pins_the_snapshot_bytes_and_closes_it_on_loader_failure(tmp_path):
    registry, _path, digest = _registry(tmp_path, pinned=False)
    with pytest.raises(RuntimeError, match="loader failed"):
        with registry.open_verified("checkpoint", fetch=False) as artifact:
            assert artifact.sha256 == digest
            assert artifact.stream.read() == b"trusted checkpoint"
            raise RuntimeError("loader failed")
    assert artifact.stream.closed
    pins = json.loads((registry.cache / "lock.json").read_text(encoding="utf-8"))
    assert pins["checkpoint"] == digest
