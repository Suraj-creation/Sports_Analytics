"""Future cache-completion provenance contracts; no inference or sporting truth."""

from __future__ import annotations

import copy
import json
from contextlib import contextmanager
from types import SimpleNamespace

import msgpack
import pytest

from research import production_external_stress as tool


def cache(path, frame_start, frame_end, **changes):
    value = {
        "v": 20,
        "start": frame_start,
        "end": frame_end,
        "ci": {"fps": 30.0, "frame_size": [16, 8]},
        "models": {},
        "frames": [{"f": i} for i in range(frame_start, frame_end + 1)],
    }
    value.update(changes)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(msgpack.packb(value, use_bin_type=True))


@pytest.fixture
def completed(tmp_path):
    output = tmp_path / "run"
    directory = output / "data/sessions/Controlled/perception"
    cache(directory / "seg_00000.msgpack", 0, 1)
    cache(directory / "seg_00001.msgpack", 2, 3)
    bindings = {
        "session_id": "Controlled",
        "source_sha256": "a" * 64,
        "proxy_sha256": "b" * 64,
        "media": {"n_frames": 4, "width": 16, "height": 8, "fps_num": 30, "fps_den": 1},
    }
    return output, directory, bindings


def test_completion_catalog_binds_exact_population_bytes_headers_and_frames(completed):
    output, directory, bindings = completed
    receipt = tool.write_perception_catalog(output, **bindings)
    verified = tool.verify_perception_catalog(output, receipt, **bindings)
    assert receipt["schema"] == tool.PERCEPTION_CATALOG_SCHEMA
    assert verified["frame_count"] == 4 and verified["file_count"] == 2
    assert [(row["start"], row["end"]) for row in verified["files"]] == [(0, 1), (2, 3)]
    assert all(row["sha256"] == tool.digest(output / row["path"]) for row in verified["files"])
    assert verified["total_bytes"] == sum(path.stat().st_size for path in directory.iterdir())
    assert "no physical accuracy" in verified["scope"]
    before = (output / tool.PERCEPTION_CATALOG_NAME).read_bytes()
    with pytest.raises(FileExistsError):
        tool.write_perception_catalog(output, **bindings)
    assert (output / tool.PERCEPTION_CATALOG_NAME).read_bytes() == before


@pytest.mark.parametrize("mutation", ["altered", "missing", "extra", "foreign_name"])
def test_parent_rejects_changed_cache_population(completed, mutation):
    output, directory, bindings = completed
    receipt = tool.write_perception_catalog(output, **bindings)
    if mutation == "altered":
        cache(directory / "seg_00000.msgpack", 0, 1, models={"changed": "provider"})
    elif mutation == "missing":
        (directory / "seg_00001.msgpack").unlink()
    elif mutation == "extra":
        cache(directory / "seg_00002.msgpack", 4, 4)
    else:
        (directory / "seg_00001.msgpack").rename(directory / "foreign.msgpack")
    with pytest.raises(ValueError):
        tool.verify_perception_catalog(output, receipt, **bindings)


@pytest.mark.parametrize("binding", ["session_id", "source_sha256", "proxy_sha256", "media"])
def test_foreign_catalog_binding_is_rejected(completed, binding):
    output, _, bindings = completed
    receipt = tool.write_perception_catalog(output, **bindings)
    foreign = copy.deepcopy(bindings)
    if binding == "media":
        foreign[binding]["width"] += 1
    else:
        foreign[binding] = "ForeignSession" if binding == "session_id" else "c" * 64
    with pytest.raises(ValueError):
        tool.verify_perception_catalog(output, receipt, **foreign)


def test_forged_catalog_digest_cannot_bypass_exact_population(completed):
    output, _, bindings = completed
    receipt = tool.write_perception_catalog(output, **bindings)
    path = output / tool.PERCEPTION_CATALOG_NAME
    value = json.loads(path.read_text())
    value["files"][0]["path"] = "../../foreign.msgpack"
    path.write_text(json.dumps(value))
    receipt["sha256"] = tool.digest(path)
    with pytest.raises(ValueError, match="binding mismatch"):
        tool.verify_perception_catalog(output, receipt, **bindings)


@pytest.mark.parametrize("kind", ["cache", "directory", "catalog", "output"])
def test_catalog_rejects_symlinks_without_following_escape(completed, tmp_path, kind):
    output, directory, bindings = completed
    receipt = tool.write_perception_catalog(output, **bindings)
    if kind == "cache":
        target = tmp_path / "foreign.msgpack"
        target.write_bytes((directory / "seg_00000.msgpack").read_bytes())
        (directory / "seg_00000.msgpack").unlink()
        (directory / "seg_00000.msgpack").symlink_to(target)
    elif kind == "directory":
        directory.rename(tmp_path / "foreign_directory")
        directory.symlink_to(tmp_path / "foreign_directory", target_is_directory=True)
    elif kind == "catalog":
        path = output / tool.PERCEPTION_CATALOG_NAME
        path.rename(tmp_path / "foreign_catalog.json")
        path.symlink_to(tmp_path / "foreign_catalog.json")
    else:
        alias = tmp_path / "alias"
        alias.symlink_to(output, target_is_directory=True)
        output = alias
    with pytest.raises(ValueError, match="symlink"):
        tool.verify_perception_catalog(output, receipt, **bindings)


@pytest.mark.parametrize("kind", ["absent_directory", "zero_files", "missing_catalog", "foreign_receipt"])
def test_completed_worker_cannot_claim_missing_cache_evidence(completed, kind):
    output, directory, bindings = completed
    receipt = tool.write_perception_catalog(output, **bindings)
    if kind in {"absent_directory", "zero_files"}:
        for path in directory.iterdir():
            path.unlink()
        if kind == "absent_directory":
            directory.rmdir()
    elif kind == "missing_catalog":
        (output / tool.PERCEPTION_CATALOG_NAME).unlink()
    else:
        receipt["path"] = "../foreign_catalog.json"
    with pytest.raises(ValueError):
        tool.verify_perception_catalog(output, receipt, **bindings)


@pytest.mark.parametrize("change", ["frame_ids", "fps", "dimensions", "codec", "extent"])
def test_header_frame_integrity_is_separate_from_hash_existence(completed, change):
    output, directory, bindings = completed
    updates = {}
    if change == "frame_ids":
        updates["frames"] = [{"f": 0}, {"f": 0}]
    elif change in {"fps", "dimensions"}:
        updates["ci"] = {
            "fps": 25.0 if change == "fps" else 30.0,
            "frame_size": [99, 8] if change == "dimensions" else [16, 8],
        }
    elif change == "codec":
        updates["v"] = 17
    else:
        updates["end"] = 100
    cache(directory / "seg_00000.msgpack", 0, 1, **updates)
    with pytest.raises(ValueError, match="header/frames"):
        tool.write_perception_catalog(output, **bindings)


def test_catalog_limits_are_enforced_before_unbounded_materialization(completed, monkeypatch):
    output, _, bindings = completed
    monkeypatch.setitem(tool.PERCEPTION_CATALOG_LIMITS, "max_cache_bytes", 8)
    with pytest.raises(ValueError, match="byte limit"):
        tool.write_perception_catalog(output, **bindings)


@pytest.mark.parametrize("after_close", ["unchanged", "changed_cache", "missing_receipt"])
def test_parent_verifies_after_worker_close_before_completed_receipt(tmp_path, monkeypatch, after_close):
    protocol = tmp_path / "protocol"
    protocol.mkdir()
    source = protocol / "session.json"
    source.write_text(json.dumps({"session_id": "Controlled"}))
    plan = {
        "root": str(protocol),
        "source_files_sha256": {},
        "input_files_sha256": {},
        "cases": {
            "test7": {"kind": "production_upload", "frames": 1, "source_sha256": "a" * 64, "session": str(source)}
        },
    }
    plan_path = protocol / "plan.json"
    plan_path.write_text(json.dumps(plan))
    output = tmp_path / "future_run"
    process = SimpleNamespace(pid=1, returncode=0, poll=lambda: 0, wait=lambda: 0)
    closed = []

    @contextmanager
    def worker(*args, **kwargs):
        output.mkdir()
        proxy = output / "data/media" / ("a" * 64) / "proxy.mp4"
        proxy.parent.mkdir(parents=True)
        proxy.write_bytes(b"controlled encoded proxy identity")
        media = {"n_frames": 1, "width": 16, "height": 8, "fps_num": 30, "fps_den": 1}
        target = output / "data/sessions/Controlled/perception/seg_00000.msgpack"
        cache(target, 0, 0)
        receipt = tool.write_perception_catalog(
            output, session_id="Controlled", source_sha256="a" * 64, proxy_sha256=tool.digest(proxy), media=media
        )
        details = {
            "status": "completed",
            "frames_processed": 1,
            "cached_perception_used": False,
            "source_sha256": "a" * 64,
            "proxy_sha256": tool.digest(proxy),
            "media": media,
            "models": {"artifacts": {}},
            "perception_cache_catalog": receipt,
        }
        if after_close == "missing_receipt":
            del details["perception_cache_catalog"]
        (output / "inference.json").write_text(json.dumps(details))
        yield process
        closed.append(True)
        if after_close == "changed_cache":
            cache(target, 0, 0, models={"changed_after_worker": True})

    @contextmanager
    def lease(*args):
        yield

    monkeypatch.setattr(tool, "gpu_uuid", lambda _: "GPU-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    monkeypatch.setattr(tool, "gpu_lease", lease)
    monkeypatch.setattr(tool, "managed_process", worker)
    code = tool.run(plan_path, "test7", output, 0)
    assert closed == [True]
    outer = json.loads(output.with_suffix(".executor.json").read_text())
    assert (code == 0) is (after_close == "unchanged")
    assert (outer["status"] == "completed") is (after_close == "unchanged")
    assert outer["perception_cache_catalog_verification"]["status"] == (
        "verified" if after_close == "unchanged" else "failed"
    )
