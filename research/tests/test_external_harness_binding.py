"""Exercise actual current plugin/runner binding without neural models or GPU."""

import json
from fractions import Fraction
from types import SimpleNamespace

import pytest
import yaml

from bai_engine.config import Profile
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import MediaInfo, Session, SessionStatus, Source, SourceKind
from research import production_external_stress as external
from research import validate_real_video_runtime as harness
from research.production_media_probe import make_source


@pytest.fixture
def no_cuda(monkeypatch):
    import torch

    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    monkeypatch.setattr(torch.cuda, "device_count", lambda: 0)


def test_real_weightless_continuous_harness_uses_staged_registry_root(tmp_path, no_cuda):
    video = tmp_path / "tiny.mp4"
    count = make_source(video, Fraction(30))
    output = tmp_path / "run"
    models = output / "models"
    models.mkdir(parents=True)
    (models / "manifest.yaml").write_text("models: {}\n")
    registry = ModelRegistry(models)
    media = MediaInfo(fps_num=30, fps_den=1, n_frames=count, width=320, height=180, duration_us=round(count / 30 * 1e6))
    session = Session(
        session_id="WeightlessBinding",
        title="No neural smoke",
        source=Source(kind=SourceKind.UPLOAD, uri=str(video), sha256=harness.sha256(video)),
        media=media,
    )
    args = SimpleNamespace(
        window_end_frame=None,
        window_start_frame=0,
        retain_perception=True,
        proxy_path=video,
        ffmpeg="ffmpeg",
        ffprobe="ffprobe",
        data_dir=tmp_path / "empty_catalogue",
        calibration_json=None,
        roster_json=None,
        seed_frames=1,
        samples=1,
    )
    report = harness.run_session(session.model_dump(mode="json"), Profile(name="weightless"), registry, args, output)
    assert report["status"] == "partial", report.get("error")
    assert report["frames_processed"] == count
    assert report["prefix_truncated"] is False
    assert report["required_stages_not_exercised"] == ["shuttle_forward", "player_detector", "pose"]
    assert all(value.get("completed", 0) == 0 for value in report["model_calls"].values())
    assert report["perception_retention"]["enabled"] is True
    assert (output / "results" / session.session_id / "events.jsonl").is_file()


@pytest.mark.parametrize("emit_cache", [True, False])
def test_upload_worker_reaches_real_runner_plugin_with_injected_registry(tmp_path, monkeypatch, no_cuda, emit_cache):
    from bai_engine.runtime.runner import SessionRunner

    source = tmp_path / "source-input"
    source.write_bytes(b"controlled input; media boundary is isolated")
    protocol = tmp_path / "protocol"
    protocol.mkdir()
    (protocol / "profiles").mkdir()
    (protocol / "profiles/experiment.yaml").write_text(yaml.safe_dump({"device": "cpu"}))
    count = 17
    session = external.clean_session(
        "test7",
        source,
        external.digest(source),
        width=320,
        height=180,
        count=count,
        fps_num=30,
        fps_den=1,
        has_audio=False,
        match_format="singles",
    )
    session_path = protocol / "test7_session.json"
    session_path.write_text(json.dumps(session))
    plan = {
        "root": str(protocol),
        "source_files_sha256": {},
        "input_files_sha256": {},
        "cases": {
            "test7": {
                "session": str(session_path),
                "source": str(source),
                "source_sha256": external.digest(source),
                "frames": count,
            }
        },
    }
    plan_path = protocol / "plan.json"
    plan_path.write_text(json.dumps(plan))
    observed = {}
    from bai_badminton import plugin as plugin_module

    actual_perception = plugin_module.BadmintonPerception

    def capture_perception(*args, **kwargs):
        observed["constructed_registry"] = args[1]
        observed["constructed_model_root"] = args[3]
        return actual_perception(*args, **kwargs)

    monkeypatch.setattr(plugin_module, "BadmintonPerception", capture_perception)

    def stage(source_root, destination, profiles):
        destination.mkdir()
        (destination / "manifest.yaml").write_text("models: {}\n")
        observed["registry"] = ModelRegistry(destination)
        return observed["registry"], {"artifacts": {}}

    monkeypatch.setattr(harness, "prepare_models", stage)

    def media(runner):
        runner.repo.update(
            runner.session_id,
            media=MediaInfo(
                fps_num=30, fps_den=1, n_frames=count, width=320, height=180, duration_us=round(count / 30 * 1e6)
            ),
        )
        target = runner.repo.media_paths(runner.session.source.sha256).proxy
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"controlled proxy; no encoder invoked")

    def analyse(runner):
        runner.sport = runner._create_sport()
        assert observed["constructed_registry"] is observed["registry"]
        observed["actual_perception"] = runner.sport.perception
        runner.repo.update(
            runner.session_id, status=SessionStatus.ANALYSED, frontier_frame=count - 1, analysed_frames=count
        )
        if emit_cache:
            import msgpack

            # Controlled cache/header fixture, not real perception or accuracy evidence.
            cache = runner.repo.paths(runner.session_id).root / "perception"
            cache.mkdir()
            (cache / "seg_00000.msgpack").write_bytes(
                msgpack.packb(
                    {
                        "v": 20,
                        "start": 0,
                        "end": count - 1,
                        "ci": {"fps": 30.0, "frame_size": [320, 180]},
                        "models": {},
                        "frames": [{"f": i} for i in range(count)],
                    },
                    use_bin_type=True,
                )
            )

    monkeypatch.setattr(SessionRunner, "_ensure_media", media)
    monkeypatch.setattr(SessionRunner, "_analyse", analyse)
    output = tmp_path / "new-run"
    if not emit_cache:
        with pytest.raises(ValueError, match="missing cache directory"):
            external.test7_worker(plan_path, output)
        assert not (output / "inference.json").exists()
        return
    external.test7_worker(plan_path, output)
    assert observed["actual_perception"].profile.name == "experiment"
    assert observed["registry"].models_dir == observed["constructed_model_root"] == output / "models"
    result = json.loads((output / "inference.json").read_text())
    assert result["frames_processed"] == count
    assert result["visible_torch_devices"] == []
    assert result["models"] == {"artifacts": {}}
    assert result["perception_cache_catalog"]["file_count"] == 1
    assert result["perception_cache_catalog"]["frame_count"] == count


def test_validation_constructor_rejects_registry_outside_staged_root(tmp_path):
    with pytest.raises(ValueError, match="isolated staged model root"):
        harness.create_validation_sport(
            None, None, None, SimpleNamespace(models_dir=tmp_path / "other"), tmp_path / "staged"
        )
