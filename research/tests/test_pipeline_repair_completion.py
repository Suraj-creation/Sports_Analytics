"""Completion recovery must reject unrelated failures, tampering and stale evidence."""

from __future__ import annotations

import copy
import json
from types import SimpleNamespace

import msgpack
import pytest

from research import pipeline_repair_completion as recovery
from scripts.benchmarking.evaluate_rallies import write_predictions


def failure(tmp_path):
    plan = tmp_path / "plan.json"
    plan.write_text("{}")
    run = tmp_path / "actual"
    receipt = {
        "status": "partial_or_failed",
        "case": "test1",
        "worker_exit_code": 1,
        "frozen_source_inputs_unchanged": True,
        "plan_sha256": recovery.digest(plan),
        "command": [
            "python",
            str(recovery.ROOT / "research/production_external_stress.py"),
            "upload-worker",
            "--case",
            "test1",
            "--plan",
            str(plan),
            "--output",
            str(run),
        ],
    }
    log = (
        "Traceback (most recent call last):\n in perception_catalog\n"
        "ValueError: unsupported cache codec version\n"
        "Traceback (most recent call last):\n in upload_worker\n in write_perception_catalog\n"
        "ValueError: invalid bounded cache header/frames: seg_00000.msgpack: unsupported cache codec version\n"
    )
    return receipt, log, plan, run


def test_known_failure_requires_exact_frozen_receipt_and_actual_terminal_exception(tmp_path):
    receipt, log, plan, run = failure(tmp_path)
    recovery.validate_failure(receipt, log, plan_path=plan, run=run, case="test1")


@pytest.mark.parametrize(
    "key,value",
    [
        ("status", "completed"),
        ("worker_exit_code", 2),
        ("frozen_source_inputs_unchanged", False),
        ("case", "test2"),
        ("plan_sha256", "b" * 64),
    ],
)
def test_other_original_status_or_source_binding_cannot_be_recovered(tmp_path, key, value):
    receipt, log, plan, run = failure(tmp_path)
    receipt[key] = value
    with pytest.raises(ValueError, match="failure receipt"):
        recovery.validate_failure(receipt, log, plan_path=plan, run=run, case="test1")


@pytest.mark.parametrize("mutation", ["different_exception", "later_failure", "extra_traceback", "other_source"])
def test_failure_reason_or_worker_arguments_cannot_be_substituted(tmp_path, mutation):
    receipt, log, plan, run = failure(tmp_path)
    if mutation == "different_exception":
        log = log.replace("unsupported cache codec version", "CUDA out of memory")
    elif mutation == "later_failure":
        log += "ValueError: another failure\n"
    elif mutation == "extra_traceback":
        log = "Traceback (most recent call last):\n" + log
    else:
        receipt["command"][-1] += "_different"
    with pytest.raises(ValueError):
        recovery.validate_failure(receipt, log, plan_path=plan, run=run, case="test1")


def wire():
    from bai_engine.config import Profile

    profile = {
        "components": {
            "content_continuity": {
                "implementation": "foreground-content-continuity-v2",
                "params": {"mode": "barrier_detector_layout_v2"},
            }
        }
    }
    profile["name"] = "experiment"
    profile["components"]["content_continuity"].update(model="none", backend="none")
    profile = Profile.model_validate(profile).model_dump(mode="json")
    identity = {"profile": profile, "loaded_models": {}, "frame_size": [1280, 720], "fps": 30}
    frame = {
        "f": 0,
        "s": None,
        "c": 0.0,
        "r": False,
        "sh": 0,
        "g": None,
        "l": False,
        "v": "main",
        "h": 0,
        "q": 0.9,
        "cs": "VALID",
        "do": False,
        "ps": 0,
        "sa": None,
        "ce": 0,
        "cc": None,
        "cd": None,
        "dg": None,
        "p": [],
    }
    return {
        "v": 21,
        "ci": identity,
        "cr": None,
        "models": {},
        "start": 0,
        "end": 0,
        "frames": [frame],
        "ocr": [],
    }, profile


def test_strict21_decoder_preserves_unknown_decision_and_never_executes_neural_models():
    value, profile = wire()
    _, decoded = recovery.validate_cache21(
        msgpack.packb(value), profile, {"width": 1280, "height": 720, "fps_num": 30, "fps_den": 1}
    )
    assert decoded.frames[0].content_decision is None


@pytest.mark.parametrize("mutation", ["old_codec", "profile", "model", "missing_cd", "future_pose", "mandatory_cd"])
def test_strict21_cache_validation_denies_tampered_provenance(mutation):
    from bai_badminton.plugin import StaleCacheError

    value, profile = wire()
    value = copy.deepcopy(value)
    if mutation == "old_codec":
        value["v"] = 20
    elif mutation == "profile":
        value["ci"]["profile"]["changed"] = True
    elif mutation == "model":
        value["models"] = {"player_detector": "other"}
    elif mutation == "missing_cd":
        del value["frames"][0]["cd"]
    elif mutation == "future_pose":
        value["frames"][0]["p"] = [{"rt": 1, "dm": True, "im": "observed", "pf": 1, "rf": None}]
    else:
        value["frames"][0]["cc"] = {"hypothesis": True}
    with pytest.raises((ValueError, StaleCacheError)):
        recovery.validate_cache21(
            msgpack.packb(value), profile, {"width": 1280, "height": 720, "fps_num": 30, "fps_den": 1}
        )


def test_prediction_validation_preserves_every_live_event_and_rejects_manual_omission(tmp_path):
    path = tmp_path / "predicted.csv"
    events = [
        SimpleNamespace(type="rally_end", frame_start=10, frame_end=30),
        SimpleNamespace(type="rally_end", frame_start=50, frame_end=90),
    ]
    write_predictions(path, [(10, 30), (50, 90)], 30)
    assert recovery.validate_predictions(path, events, 30)["rally_end_count"] == 2
    path.unlink()
    write_predictions(path, [(10, 30)], 30)
    with pytest.raises(ValueError, match="ALL live"):
        recovery.validate_predictions(path, events, 30)


def test_symlink_artifact_is_rejected(tmp_path):
    original = tmp_path / "original"
    original.write_bytes(b"source")
    link = tmp_path / "alias"
    link.symlink_to(original)
    with pytest.raises(ValueError, match="nonsymlink"):
        recovery.digest(link)


def test_source_snapshot_tampering_is_rejected_even_if_current_source_not_required(tmp_path):
    source = recovery.ROOT / "engine/src/bai_engine/__init__.py"
    snapshot = tmp_path / "executed_source" / source.relative_to(recovery.ROOT)
    snapshot.parent.mkdir(parents=True)
    snapshot.write_bytes(source.read_bytes())
    plan = {
        "root": str(tmp_path),
        "source_files_sha256": {str(source): recovery.digest(source)},
        "input_files_sha256": {},
    }
    recovery.verify_frozen_plan(plan, current_source_guard=False)
    snapshot.write_text("changed")
    with pytest.raises(ValueError, match="snapshot"):
        recovery.verify_frozen_plan(plan, current_source_guard=False)


def test_recovery_publication_hash_tamper_rejected_before_source_claim(tmp_path):
    receipt = tmp_path / "completion_receipt.json"
    receipt.write_text("{}")
    manifest = {
        "schema": "independent-analysis-recovery-publication:v1",
        "original_run": str(tmp_path),
        "artifact_sha256": {
            "completion_receipt.json": "x",
            "perception_catalog.json": "x",
            "executed_recovery_source.py": "x",
        },
    }
    (tmp_path / "recovery_manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="digest"):
        recovery.verify_completion_receipt(tmp_path, tmp_path)


def test_recovery_catalog_accepts21_without_mutating_original_worker_allowlist(tmp_path):
    from research import production_external_stress as original

    before = copy.deepcopy(original.PERCEPTION_CATALOG_LIMITS)
    value, profile = wire()
    directory = tmp_path / "data/sessions/SOURCE/perception"
    directory.mkdir(parents=True)
    (directory / "seg_00000.msgpack").write_bytes(msgpack.packb(value))
    media = {"n_frames": 1, "width": 1280, "height": 720, "fps_num": 30, "fps_den": 1}
    catalog, _, _, counts = recovery.cache_catalog(
        tmp_path, session_id="SOURCE", source_sha256="a" * 64, proxy_sha256="b" * 64, media=media, profile=profile
    )
    assert counts["frames_strictly_decoded"] == 1
    assert catalog["snapshot_stage"] == "independent_readonly_verification_after_failed_worker_close"
    assert before == original.PERCEPTION_CATALOG_LIMITS
    value["v"] = 22
    (directory / "seg_00000.msgpack").write_bytes(msgpack.packb(value))
    with pytest.raises(ValueError, match="unsupported cache codec"):
        original.perception_catalog(
            tmp_path, session_id="SOURCE", source_sha256="a" * 64, proxy_sha256="b" * 64, media=media
        )


@pytest.mark.parametrize("mutation", ["missing_tail", "wrong_id", "symlink"])
def test_recovery_catalog_does_not_weaken_frame_population_or_file_guards(tmp_path, mutation):
    value, profile = wire()
    directory = tmp_path / "data/sessions/SOURCE/perception"
    directory.mkdir(parents=True)
    path = directory / "seg_00000.msgpack"
    if mutation == "wrong_id":
        value["frames"][0]["f"] = 1
    path.write_bytes(msgpack.packb(value))
    if mutation == "symlink":
        target = tmp_path / "foreign.msgpack"
        path.rename(target)
        path.symlink_to(target)
    media = {
        "n_frames": 2 if mutation == "missing_tail" else 1,
        "width": 1280,
        "height": 720,
        "fps_num": 30,
        "fps_den": 1,
    }
    with pytest.raises(ValueError):
        recovery.cache_catalog(
            tmp_path, session_id="SOURCE", source_sha256="a" * 64, proxy_sha256="b" * 64, media=media, profile=profile
        )


def test_all_loaded_model_sets_require_integrity_verification(tmp_path):
    declarations = {"loaded_models": {"first": {"shuttle": "valid@1"}, "later": {"shuttle": "other@2"}}}
    with pytest.raises(ValueError, match=r"loaded.model.*declaration"):
        recovery.verify_models(tmp_path, declarations, {})


@pytest.mark.parametrize("mutation", ["none", "graph", "manifest"])
def test_extracted_graph_is_bound_to_the_actual_pinned_archive(tmp_path, mutation):
    import hashlib
    import zipfile

    archive = tmp_path / "model.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("net.onnx", b"original graph")
    extraction = tmp_path / "extracted"
    (extraction / "files").mkdir(parents=True)
    (extraction / "files/net.onnx").write_bytes(b"original graph")
    record = {
        "schema": "verified-archive-extraction-v1",
        "archive_sha256": recovery.digest(archive),
        "files": {"net.onnx": hashlib.sha256(b"original graph").hexdigest()},
        "graph": "net.onnx",
    }
    if mutation != "none":
        (extraction / "files/net.onnx").write_bytes(b"changed graph")
    if mutation == "manifest":
        record["files"]["net.onnx"] = hashlib.sha256(b"changed graph").hexdigest()
    (extraction / "manifest.json").write_text(json.dumps(record))
    if mutation == "none":
        recovery.verify_archive_extraction(archive, extraction)
    else:
        with pytest.raises(ValueError, match="pinned archive"):
            recovery.verify_archive_extraction(archive, extraction)


def test_full_rational_source_proxy_comparison_supports_equal_nonzero_origins_and_rejects_shifts(monkeypatch):
    from fractions import Fraction

    import av

    class Container:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        streams = SimpleNamespace(video=[SimpleNamespace(codec_context=SimpleNamespace())])

        def decode(self, stream):
            return iter(
                [SimpleNamespace(width=1280, height=720, pts=100 + i, time_base=Fraction(1, 30)) for i in range(3)]
            )

    monkeypatch.setattr(av, "open", lambda path: Container())
    times = [Fraction(100 + i, 30) for i in range(3)]
    media = {"width": 1280, "height": 720, "fps_num": 30, "fps_den": 1, "n_frames": 3}
    assert recovery.verify_proxy("unused", media, {}, times)["source_proxy_full_rational_pts_equal"] is True
    with pytest.raises(ValueError, match="rational"):
        recovery.verify_proxy("unused", media, {}, [t + Fraction(1, 30000) for t in times])
