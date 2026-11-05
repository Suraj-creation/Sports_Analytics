"""Input isolation, exact passive profile edits and source/lease failure controls."""

from __future__ import annotations

import copy
import json
from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from bai_engine.schema import SessionStatus
from research import production_external_stress as tool


def profile():
    return {
        "shuttle": {
            "precision": "fp16",
            "params": {"threshold": 0.5, "step": 8, "diagnostics": {"ranges": [[100, 200]], "top_k": 5}},
        },
        "components": {
            "shuttle_association": {"implementation": "coobserved-static-hypotheses-v1"},
            "content_continuity": {
                "implementation": "foreground-content-continuity-v1",
                "params": {"mode": "barrier_hypothesis_v1"},
            },
        },
    }


def test_profile_clears_only_passive_ranges_without_mutating_original():
    original = profile()
    before = copy.deepcopy(original)
    changed = tool.passive_profile(original)
    assert original == before
    assert changed["shuttle"]["params"]["diagnostics"]["ranges"] == []
    changed["shuttle"]["params"]["diagnostics"]["ranges"] = [[100, 200]]
    assert changed == before


@pytest.mark.parametrize("component", ["content_continuity", "shuttle_association"])
def test_wrong_primary_provider_is_rejected(component):
    raw = profile()
    raw["components"][component]["implementation"] = "another-provider"
    with pytest.raises(ValueError, match="frozen primary"):
        tool.passive_profile(raw)


def test_clean_session_does_not_copy_names_windows_calibration_or_reviews(tmp_path):
    raw = tool.clean_session(
        "doubles",
        tmp_path / "clip.mp4",
        "a" * 64,
        width=1280,
        height=720,
        count=3600,
        fps_num=30,
        fps_den=1,
        has_audio=False,
        match_format="doubles",
    )
    assert raw["source"]["sha256"] == "a" * 64
    assert raw["meta"] == {} and raw["players"] == []
    assert raw["roster"] == {"match_format": "doubles", "teams": [], "participants": []}
    assert raw["media"]["n_frames"] == 3600
    assert raw["session_id"] != "DSDOUBLES20261104"


@pytest.mark.parametrize("count", [17, 10725])
def test_complete_upload_uses_actual_source_count_not_test1_constant(count):
    final = SimpleNamespace(
        status=SessionStatus.ANALYSED, media=SimpleNamespace(n_frames=count), frontier_frame=count - 1
    )
    tool.require_complete(final, count)
    final.frontier_frame -= 1
    with pytest.raises(RuntimeError, match="dynamic source"):
        tool.require_complete(final, count)


def test_source_and_profile_content_hash_tamper_is_detected(tmp_path):
    source = tmp_path / "input"
    source.write_bytes(b"original")
    config = tmp_path / "profile"
    config.write_bytes(b"frozen")
    plan = {
        "source_files_sha256": {str(source): tool.digest(source)},
        "input_files_sha256": {str(config): tool.digest(config)},
    }
    tool.verify_inputs(plan)
    config.write_bytes(b"threshold changed")
    with pytest.raises(ValueError, match="frozen source/input changed"):
        tool.verify_inputs(plan)


def test_clip_command_has_no_reference_window_or_calibration_argument(tmp_path):
    plan = {
        "root": str(tmp_path / "protocol"),
        "cases": {
            "india": {
                "kind": "prepared_clip",
                "session": str(tmp_path / "clean_session.json"),
                "source": str(tmp_path / "clip.mp4"),
            }
        },
    }
    command = tool.command_for(plan, "india", tmp_path / "run")
    assert command[command.index("--proxy-path") + 1] == str(tmp_path / "clip.mp4")
    assert "--retain-perception" in command
    assert command[command.index("--samples") + 1] == "1"
    assert not any("annotat" in arg or "calibration-json" in arg or "window-" in arg for arg in command)


def test_guard_rejects_output_in_repository_before_gpu_access(tmp_path, monkeypatch):
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps({"root": str(tmp_path / "protocol")}))
    monkeypatch.setattr(tool, "gpu_uuid", lambda *_: pytest.fail("GPU must not be queried"))
    with pytest.raises(ValueError, match="outside"):
        tool.run(plan_path, "india", tool.ROOT / "should_not_exist", 0)


def test_busy_gpu_lease_never_spawns_worker(tmp_path, monkeypatch):
    protocol = tmp_path / "protocol"
    protocol.mkdir()
    plan = {
        "root": str(protocol),
        "source_files_sha256": {},
        "input_files_sha256": {},
        "cases": {"india": {"kind": "prepared_clip", "session": "unused", "source": "unused"}},
    }
    plan_path = protocol / "plan.json"
    plan_path.write_text(json.dumps(plan))
    monkeypatch.setattr(tool, "gpu_uuid", lambda *_: "GPU-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

    @contextmanager
    def busy(*_):
        raise RuntimeError("busy lease")
        yield

    monkeypatch.setattr(tool, "gpu_lease", busy)
    monkeypatch.setattr(tool.subprocess, "Popen", lambda *a, **k: pytest.fail("must not start a worker"))
    with pytest.raises(RuntimeError, match="busy"):
        tool.run(plan_path, "india", tmp_path / "run", 0)
    assert not (tmp_path / "run").exists()


def test_actual_verified_model_bytes_are_rechecked(tmp_path):
    weights = tmp_path / "weights"
    weights.write_bytes(b"verified")
    report = {
        "artifacts": {
            "available": {"status": "verified_copy", "source_path": str(weights), "sha256": tool.digest(weights)},
            "optional": {"status": "missing_artifact_or_existing_pin"},
        }
    }
    assert tool.verify_models(report) == {str(weights): tool.digest(weights)}
    weights.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="model artifact changed"):
        tool.verify_models(report)


def test_worker_cancellation_reaps_only_owned_process_group(monkeypatch):
    signals = []
    process = SimpleNamespace(pid=12345, returncode=None)
    process.poll = lambda: process.returncode

    def wait(timeout=None):
        process.returncode = -15
        return -15

    process.wait = wait

    def start(*args, **kwargs):
        assert kwargs["start_new_session"] is True
        return process

    monkeypatch.setattr(tool.subprocess, "Popen", start)
    monkeypatch.setattr(tool.os, "killpg", lambda pid, sig: signals.append((pid, sig)))
    with pytest.raises(KeyboardInterrupt), tool.managed_process(["owned-worker"]):
        raise KeyboardInterrupt
    assert signals == [(12345, tool.signal.SIGTERM)]
    assert process.returncode == -15
