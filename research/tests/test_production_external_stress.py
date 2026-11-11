"""Input isolation, exact passive profile edits and source/lease failure controls."""

from __future__ import annotations

import copy
import json
import os
from contextlib import contextmanager
from fractions import Fraction
from pathlib import Path
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


def test_validated_detector_layout_profile_is_frozen_without_numerical_changes():
    raw = profile()
    raw["components"]["content_continuity"] = {
        "implementation": "foreground-content-continuity-v2",
        "params": {"mode": "barrier_detector_layout_v2"},
    }
    original = copy.deepcopy(raw)
    result = tool.passive_profile(raw)
    assert raw == original
    assert result["shuttle"]["params"]["diagnostics"]["ranges"] == []
    result["shuttle"]["params"]["diagnostics"]["ranges"] = original["shuttle"]["params"]["diagnostics"]["ranges"]
    assert result == original


@pytest.mark.parametrize(
    "mode", ["barrier_correspondence_v2", "barrier_hypothesis_cadence_v2", "barrier_hypothesis_v1"]
)
def test_rejected_or_mismatched_scene_experiment_is_not_accepted_as_primary(mode):
    raw = profile()
    raw["components"]["content_continuity"] = {
        "implementation": "foreground-content-continuity-v2",
        "params": {"mode": mode},
    }
    with pytest.raises(ValueError, match="scene profile"):
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


@pytest.mark.parametrize("count", [1, 17, 3600, 3601, 29280])
def test_upload_diagnostics_are_input_only_bounded_and_cover_both_ends(count):
    from bai_badminton.perception.diagnostics import DiagnosticSelection

    ranges = tool.diagnostic_ranges(count)
    selection = DiagnosticSelection.parse({"ranges": ranges})
    assert sum(end - start + 1 for start, end in selection.ranges) == min(count, 3600)
    assert ranges[0][0] == 0 and ranges[-1][1] == count - 1


def test_generic_full_upload_command_keeps_case_and_has_no_labels(tmp_path):
    plan = {"root": str(tmp_path / "protocol"), "cases": {"newmatch": {"kind": "production_upload"}}}
    command = tool.command_for(plan, "newmatch", tmp_path / "run")
    assert "upload-worker" in command
    assert command[command.index("--case") + 1] == "newmatch"
    assert not any("annotat" in value or "ground-truth" in value for value in command)


def test_upload_rejects_unsupported_timestamps_before_writing_output(tmp_path, monkeypatch):
    import importlib

    media_probe = importlib.import_module("bai_engine.media.probe")
    proxy = importlib.import_module("bai_engine.media.proxy")
    video, profile_path, output = tmp_path / "video.mp4", tmp_path / "profile.yaml", tmp_path / "new"
    video.write_bytes(b"source")
    profile_path.write_text("unused")
    monkeypatch.setattr(
        media_probe,
        "probe",
        lambda *a, **k: SimpleNamespace(packet_cadence_complete=True, variable_frame_rate=True, fps=Fraction(30)),
    )
    monkeypatch.setattr(proxy, "plan_proxy", lambda *a, **k: SimpleNamespace(fps=Fraction(30)))
    with pytest.raises(ValueError, match="explicit PTS mapping"):
        tool.prepare_upload(video, profile_path, output, "newmatch")
    assert not output.exists()


def test_upload_preparation_freezes_input_only_session_and_checks_decoded_count(tmp_path, monkeypatch):
    import importlib

    import yaml

    media_probe = importlib.import_module("bai_engine.media.probe")
    proxy = importlib.import_module("bai_engine.media.proxy")
    ffmpeg = importlib.import_module("bai_engine.media.ffmpeg")
    repo = tmp_path / "repo"
    (repo / "models/cache").mkdir(parents=True)
    (repo / "models/manifest.yaml").write_text("models: {}")
    (repo / "models/cache/lock.json").write_text("{}")
    implementation = repo / "executor.py"
    implementation.write_text("frozen source")
    video, profile_path = tmp_path / "video.mp4", tmp_path / "profile.yaml"
    video.write_bytes(b"original video")
    profile_path.write_text(yaml.safe_dump(profile()))
    monkeypatch.setattr(tool, "ROOT", repo)
    monkeypatch.setattr(tool, "source_files", lambda: [implementation])
    monkeypatch.setattr(tool.subprocess, "check_output", lambda *a, **k: "recorded git\n")
    monkeypatch.setattr(
        media_probe,
        "probe",
        lambda *a, **k: SimpleNamespace(
            packet_cadence_complete=True, variable_frame_rate=False, fps=Fraction(30), video_stream_index=0, n_frames=17
        ),
    )
    monkeypatch.setattr(proxy, "plan_proxy", lambda *a, **k: SimpleNamespace(fps=Fraction(30)))
    header = {"streams": [{"codec_type": "video", "nb_read_frames": "17"}]}
    monkeypatch.setattr(ffmpeg, "run_json", lambda *a, **k: header)
    destination = tmp_path / "protocol"
    plan = tool.prepare_upload(video, profile_path, destination, "newmatch")
    item = plan["cases"]["newmatch"]
    assert item["frames"] == 17 and item["kind"] == "production_upload"
    session = json.loads(Path(item["session"]).read_text())
    assert session["source"]["uri"] == str(video)
    assert session["meta"] == {} and session["players"] == [] and session["media"] is None
    assert session["session_id"] == "UPLOADNEWMATCH"
    assert not {"ground_truth", "annotations", "reference"}.intersection(plan)
    assert (destination / "executed_source/executor.py").read_bytes() == implementation.read_bytes()
    header["streams"][0]["nb_read_frames"] = "16"
    with pytest.raises(ValueError, match="decoded frame count"):
        tool.prepare_upload(video, profile_path, tmp_path / "invalid", "newmatch")
    assert not (tmp_path / "invalid").exists()


@pytest.mark.parametrize("case", ["../escape", "UPPER", "a/b", "", "a" * 33])
def test_upload_rejects_unsafe_case_before_any_media_access(tmp_path, case):
    with pytest.raises(ValueError, match="alphanumeric"):
        tool.prepare_upload(tmp_path / "absent", tmp_path / "absent", tmp_path / "new", case)


def test_worker_process_resource_sample_observes_real_process():
    row = tool.process_resources(os.getpid())
    assert row["worker_tree_processes"] >= 1
    assert row["worker_tree_rss_bytes"] > 0
    assert row["worker_tree_cpu_seconds"] >= 0


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
