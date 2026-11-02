"""First-use integrity pins must survive failed or simultaneous publication."""

import hashlib
import json
import multiprocessing
from pathlib import Path

import pytest
import yaml

from bai_engine.runtime.registry import ModelRegistry


def _models(tmp_path):
    models = tmp_path / "models"
    models.mkdir()
    manifest = {"models": {}}
    for name in ("first", "second"):
        manifest["models"][name] = {
            "task": "test",
            "format": "torch",
            "source": {"file": "checkpoint.pt"},
            "sha256": "pin-on-first-fetch",
        }
        artifact = models / "cache" / name / "checkpoint.pt"
        artifact.parent.mkdir(parents=True)
        artifact.write_bytes(name.encode())
    (models / "manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    return models


def test_failed_atomic_pin_publication_preserves_existing_pins(monkeypatch, tmp_path):
    models = _models(tmp_path)
    registry = ModelRegistry(models)
    pins = models / "cache" / "lock.json"
    original = {"existing": "a" * 64}
    pins.write_text(json.dumps(original), encoding="utf-8")
    replace = Path.replace
    attempted = []

    def fail_pin_commit(source, destination):
        if Path(destination) == pins:
            attempted.append(source)
            assert json.loads(pins.read_text(encoding="utf-8")) == original
            raise OSError("injected pin publication failure")
        return replace(source, destination)

    monkeypatch.setattr(Path, "replace", fail_pin_commit)
    with pytest.raises(OSError, match="injected pin publication failure"):
        with registry.open_verified("first", fetch=False):
            pytest.fail("failed integrity pin must not reach its loader")
    assert attempted
    assert json.loads(pins.read_text(encoding="utf-8")) == original
    assert not any(path.exists() for path in attempted)


def _pin_worker(models, name, entered, release, completed):
    registry = ModelRegistry(Path(models))
    locked = registry._locked

    def delayed_pin_read():
        data = locked()
        if name == "first":
            entered.set()
            if not release.wait(15):
                raise TimeoutError("parent did not release pin read")
        return data

    registry._locked = delayed_pin_read
    if name == "second":
        entered.set()
    with registry.open_verified(name, fetch=False):
        pass
    completed.set()


def test_independent_registry_processes_preserve_both_first_use_pins(tmp_path):
    models = _models(tmp_path)
    context = multiprocessing.get_context("spawn")
    first_entered, second_entered = context.Event(), context.Event()
    release, first_done, second_done = context.Event(), context.Event(), context.Event()
    first = context.Process(target=_pin_worker, args=(str(models), "first", first_entered, release, first_done))
    second = context.Process(target=_pin_worker, args=(str(models), "second", second_entered, release, second_done))
    first.start()
    try:
        assert first_entered.wait(15), "first process did not enter pin transaction"
        second.start()
        assert second_entered.wait(15), "second process did not start verification"
        # The first reader is paused inside its transaction. A second writer
        # must wait, otherwise its pin can be overwritten by the first snapshot.
        completed_before_release = second_done.wait(0.5)
        release.set()
        first.join(15)
        second.join(15)
        assert first.exitcode == 0 and second.exitcode == 0
        assert not completed_before_release, "independent registry writers did not serialize their pin transaction"
        pins = json.loads((models / "cache" / "lock.json").read_text(encoding="utf-8"))
        assert pins == {name: hashlib.sha256(name.encode()).hexdigest() for name in ("first", "second")}
    finally:
        release.set()
        for process in (first, second):
            if process.pid is not None:
                process.join(2)
                if process.is_alive():
                    process.terminate()
                    process.join(2)
