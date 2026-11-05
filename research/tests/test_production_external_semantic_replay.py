"""Source-proof controls; fake hashes validate contracts, never sports accuracy."""

import copy

import pytest

from research import production_external_semantic_replay as replay


def proof():
    return {
        "schema": "cached-external-semantic:v2",
        "baseline_parity": True,
        "geometry_bracket": False,
        "contact_motion_reliability": False,
        "source_report_sha256": "report",
        "executed_source_sha256": {"sports/model.py": "engine"},
        "harness_source_sha256": {
            "research/runner.py": "runner",
            "research/reference.py": "reference",
            "research/parity.py": "parity",
            "research/event_fold.py": "fold",
            "research/production_external_stress.py": "catalogue",
        },
    }


def verify(document):
    replay.require_baseline_proof(
        document,
        report_sha="report",
        engine_sources={"sports/model.py": "engine"},
        harness_sources=proof()["harness_source_sha256"],
    )


def test_identical_runner_helpers_engine_and_source_report_allow_proof():
    verify(proof())


@pytest.mark.parametrize("version", [None, "cached-external-semantic:v1"])
def test_old_missing_or_v1_schema_cannot_authorize_future_arm(version):
    value = proof()
    value["schema"] = version
    value.pop("harness_source_sha256")
    with pytest.raises(ValueError, match="baseline parity proof"):
        verify(value)


@pytest.mark.parametrize(
    "file",
    [
        "research/runner.py",
        "research/reference.py",
        "research/parity.py",
        "research/event_fold.py",
        "research/production_external_stress.py",
    ],
)
def test_changed_runner_or_direct_or_transitive_helper_cannot_reuse_baseline(file):
    value = proof()
    value["harness_source_sha256"][file] = "different implementation"
    with pytest.raises(ValueError, match="baseline parity proof"):
        verify(value)


def test_missing_helper_digest_cannot_be_treated_as_compatible_legacy():
    value = proof()
    del value["harness_source_sha256"]["research/reference.py"]
    with pytest.raises(ValueError, match="baseline parity proof"):
        verify(value)


@pytest.mark.parametrize(
    "field,value",
    [
        ("baseline_parity", False),
        ("geometry_bracket", True),
        ("contact_motion_reliability", True),
        ("source_report_sha256", "other"),
        ("executed_source_sha256", {"sports/model.py": "other"}),
    ],
)
def test_nonbaseline_other_input_or_other_engine_cannot_supply_proof(field, value):
    document = proof()
    document[field] = value
    with pytest.raises(ValueError, match="baseline parity proof"):
        verify(document)


def test_capture_detaches_original_bytes_and_changed_helper_is_detected_afterward(tmp_path):
    a, b = tmp_path / "runner.py", tmp_path / "helper.py"
    a.write_bytes(b"original runner\n")
    b.write_bytes(b"original helper\n")
    paths = {"research/runner.py": a, "research/helper.py": b}
    captured, hashes = replay.capture_harness_sources(paths)
    replay.verify_harness_sources(hashes, paths)
    b.write_bytes(b"changed helper\n")
    assert captured["research/helper.py"] == b"original helper\n"
    with pytest.raises(ValueError, match="runner/helper changed"):
        replay.verify_harness_sources(hashes, paths)


def test_extra_dependency_also_changes_exact_harness_identity(tmp_path):
    path = tmp_path / "runner.py"
    path.write_bytes(b"runner")
    paths = {"research/runner.py": path}
    _, hashes = replay.capture_harness_sources(paths)
    before = copy.deepcopy(hashes)
    paths["research/new_helper.py"] = path
    with pytest.raises(ValueError, match="runner/helper changed"):
        replay.verify_harness_sources(before, paths)


@pytest.mark.parametrize("value", [1, "true", "false", None])
def test_baseline_parity_must_be_actual_boolean_true(value):
    document = proof()
    document["baseline_parity"] = value
    with pytest.raises(ValueError, match="baseline parity proof"):
        verify(document)


def test_helper_identity_is_captured_before_any_input_validator_runs(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(replay, "capture_harness_sources", lambda: calls.append("capture") or ({}, {}))
    monkeypatch.setattr(replay, "source_hashes", lambda: calls.append("core") or {})

    def load(*args):
        calls.append("validator")
        raise ValueError("stop before engine construction")

    monkeypatch.setattr(replay, "load_finished_input", load)
    with pytest.raises(ValueError, match="stop before engine"):
        replay.replay(tmp_path, "SESSION", tmp_path / "not-created")
    assert calls == ["capture", "core", "validator"]


def full_upload(tmp_path):
    import json

    run = tmp_path / "test7_run"
    run.mkdir()
    source = tmp_path / "source.mp4"
    source.write_bytes(b"source bytes; no decode")
    source_sha = replay.sha(source)
    media = {"n_frames": 3, "fps_num": 30, "fps_den": 1, "width": 16, "height": 8}
    proxy = run / "data/media" / source_sha / "proxy.mp4"
    proxy.parent.mkdir(parents=True)
    proxy.write_bytes(b"proxy bytes; no decode")
    session = {
        "session_id": "REALTEST7",
        "status": "analysed",
        "media": media,
        "frontier_frame": 2,
        "source": {"sha256": source_sha},
    }
    info = {
        "status": "completed",
        "cached_perception_used": False,
        "media": media,
        "profile": {},
        "frames_processed": 3,
        "frontier_frame": 2,
        "source_sha256": source_sha,
        "proxy_sha256": replay.sha(proxy),
    }
    plan = {
        "code_commit": "source-commit",
        "source_files_sha256": {},
        "cases": {"test7": {"frames": 3, "source": str(source), "source_sha256": source_sha}},
    }
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan))
    executor = {
        "status": "completed",
        "case": "test7",
        "worker_exit_code": 0,
        "frozen_source_inputs_unchanged": True,
        "command": ["worker", "--plan", str(plan_path)],
        "plan_sha256": replay.sha(plan_path),
        "output_proxy_sha256": replay.sha(proxy),
    }
    for path, value in [
        (run / "session.json", session),
        (run / "inference.json", info),
        (run.with_suffix(".executor.json"), executor),
    ]:
        path.write_text(json.dumps(value))
    (run / "events.jsonl").write_text("")
    caches = run / "data/sessions/REALTEST7/perception"
    caches.mkdir(parents=True)
    (caches / "seg_00000.msgpack").write_bytes(b"unreviewed observation bytes, not decoded by loader")
    return run, info, executor, session


def test_genuine_full_upload_paths_are_used_without_fabricated_harness_metadata(tmp_path):
    run, _, _, _ = full_upload(tmp_path)
    loaded = replay.load_finished_input(run, "REALTEST7")
    assert loaded.layout == "production-full-upload"
    assert loaded.events_path == run / "events.jsonl"
    assert loaded.session_path == run / "session.json"
    assert loaded.cache_directory == run / "data/sessions/REALTEST7/perception"
    assert loaded.media["n_frames"] == 3
    assert "after completion" in loaded.cache_digest_scope
    assert not (run / "run.json").exists()
    assert not (run / "benchmark_metadata.json").exists()


@pytest.mark.parametrize(
    "field,value",
    [("status", "running"), ("worker_exit_code", 1), ("frozen_source_inputs_unchanged", False), ("case", "unrelated")],
)
def test_failed_unfinished_or_other_full_upload_executor_is_rejected(tmp_path, field, value):
    import json

    run, _, executor, _ = full_upload(tmp_path)
    executor[field] = value
    run.with_suffix(".executor.json").write_text(json.dumps(executor))
    with pytest.raises(ValueError, match="finished source-guarded"):
        replay.load_finished_input(run, "REALTEST7")


def test_full_upload_cannot_shorten_both_session_and_info_relative_to_original_plan(tmp_path):
    import json

    run, info, _, session = full_upload(tmp_path)
    for document in (info, session):
        document["media"]["n_frames"] = 2
        document["frontier_frame"] = 1
    info["frames_processed"] = 2
    (run / "session.json").write_text(json.dumps(session))
    (run / "inference.json").write_text(json.dumps(info))
    with pytest.raises(ValueError, match="source/frontier mismatch"):
        replay.load_finished_input(run, "REALTEST7")


def test_full_upload_plan_cannot_change_after_worker_guard(tmp_path):
    run, _, _, _ = full_upload(tmp_path)
    (tmp_path / "plan.json").write_text("{}")
    with pytest.raises(ValueError, match="plan digest changed"):
        replay.load_finished_input(run, "REALTEST7")


def test_full_upload_proxy_actual_bytes_are_verified(tmp_path):
    run, _, _, _ = full_upload(tmp_path)
    next((run / "data/media").glob("*/proxy.mp4")).write_bytes(b"replacement")
    with pytest.raises(ValueError, match="canonical proxy bytes changed"):
        replay.load_finished_input(run, "REALTEST7")


def add_completion_catalogue(run, info):
    import json

    import msgpack

    from research.production_external_stress import write_perception_catalog

    media = info["media"]
    cache = run / "data/sessions/REALTEST7/perception/seg_00000.msgpack"
    cache.write_bytes(
        msgpack.packb(
            {
                "v": 20,
                "start": 0,
                "end": media["n_frames"] - 1,
                "cr": None,
                "ci": {"fps": media["fps_num"] / media["fps_den"], "frame_size": [media["width"], media["height"]]},
                "models": {},
                "frames": [{"f": index} for index in range(media["n_frames"])],
                "ocr": [],
            },
            use_bin_type=True,
        )
    )
    receipt = write_perception_catalog(
        run, session_id="REALTEST7", source_sha256=info["source_sha256"], proxy_sha256=info["proxy_sha256"], media=media
    )
    info["perception_cache_catalog"] = receipt
    (run / "inference.json").write_text(json.dumps(info))
    return cache


def test_present_completion_catalogue_is_used_as_original_cache_binding(tmp_path):
    run, info, _, _ = full_upload(tmp_path)
    cache = add_completion_catalogue(run, info)
    loaded = replay.load_finished_input(run, "REALTEST7")
    assert loaded.expected_caches == {cache.name: replay.sha(cache)}
    assert loaded.cache_catalogue_receipt == info["perception_cache_catalog"]
    assert "before worker completion" in loaded.cache_digest_scope
    assert run / "perception_completion_catalog.json" in loaded.input_paths


@pytest.mark.parametrize("change", ["bytes", "missing", "extra", "catalogue"])
def test_present_completion_catalogue_rejects_changed_missing_extra_before_engine(tmp_path, change, monkeypatch):
    run, info, _, _ = full_upload(tmp_path)
    cache = add_completion_catalogue(run, info)
    if change == "bytes":
        cache.write_bytes(cache.read_bytes() + b"tamper")
    elif change == "missing":
        cache.unlink()
    elif change == "extra":
        (cache.parent / "seg_00001.msgpack").write_bytes(cache.read_bytes())
    else:
        (run / "perception_completion_catalog.json").write_text("{}")
    constructed = []
    monkeypatch.setattr(replay, "BadmintonMatchEngine", lambda *a, **k: constructed.append(True))
    with pytest.raises(ValueError):
        replay.replay(run, "REALTEST7", tmp_path / "must-not-create-engine")
    assert constructed == []


def test_present_null_catalogue_is_not_legacy_absence(tmp_path):
    import json

    run, info, _, _ = full_upload(tmp_path)
    info["perception_cache_catalog"] = None
    (run / "inference.json").write_text(json.dumps(info))
    with pytest.raises(ValueError):
        replay.load_finished_input(run, "REALTEST7")


def test_catalogue_verifier_module_is_part_of_exact_harness_proof():
    assert "research/production_external_stress.py" in replay.harness_paths()
