"""Read-only entry points of the fresh real-video validation command."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from bai_engine.schema import MediaInfo, Session, Source, SourceKind
from bai_engine.store import SessionRepository

SCRIPT = Path(__file__).resolve().parents[1] / "validate_real_video_runtime.py"


def test_cropped_validation_preserves_only_verified_media_transform_metadata():
    from research.validate_real_video_runtime import validation_input_metadata

    media = MediaInfo(fps_num=30, fps_den=1, n_frames=120, width=1280, height=720, duration_us=4_000_000)
    mapping = {
        "source_decode_frames": [12000, 12120], "source_decode_start": 12000,
        "proxy_frames": [0, 120], "proxy_fps_num": 30, "proxy_fps_den": 1,
        "proxy_sha256": "a" * 64,
        "source_frame_for_proxy_frame": "source_decode_start + proxy_frame",
        "source_timestamps_preserved": False,
        "source_pts_mapping": "decode-index translation only",
        "annotation_labels": [{"winner": "P1"}],
    }
    meta = {"source_window": mapping, "reviewed_intervals": [[0, 120]], "accepted_points": ["P1"],
            "annotation_alignment": "human_verified", "roster_binding": {"near": "P1"}}
    result = validation_input_metadata(meta, media=media, proxy_sha256="a" * 64)
    assert set(result) == {"source_window"}
    assert "annotation_labels" not in result["source_window"]
    assert result["source_window"]["source_decode_start"] == 12000
    result["source_window"]["source_decode_frames"][0] = 1
    assert mapping["source_decode_frames"] == [12000, 12120]


@pytest.mark.parametrize(("key", "value"), [
    ("source_decode_frames", [12000, 12119]),
    ("source_decode_start", True),
    ("proxy_frames", [1, 120]),
    ("proxy_fps_den", 2),
    ("proxy_sha256", "b" * 64),
])
def test_cropped_validation_rejects_inconsistent_media_transform_metadata(key, value):
    from research.validate_real_video_runtime import validation_input_metadata

    media = MediaInfo(fps_num=30, fps_den=1, n_frames=120, width=1280, height=720, duration_us=4_000_000)
    mapping = {"source_decode_frames": [12000, 12120], "source_decode_start": 12000,
               "proxy_frames": [0, 120], "proxy_fps_num": 30, "proxy_fps_den": 1, "proxy_sha256": "a" * 64}
    mapping[key] = value
    with pytest.raises(ValueError, match="source.window|transform"):
        validation_input_metadata({"source_window": mapping}, media=media, proxy_sha256="a" * 64)


def test_full_video_validation_does_not_copy_source_review_metadata():
    from research.validate_real_video_runtime import validation_input_metadata

    assert validation_input_metadata({"reviewed_intervals": [[0, 12]]}, media=None, proxy_sha256="a" * 64) == {}


def test_catalogue_listing_requires_no_inference_or_durable_source_mutation(tmp_path):
    source = tmp_path / "source"
    repo = SessionRepository(source)
    session = repo.save(Session(
        title="Controlled SampleRally",
        source=Source(kind=SourceKind.UPLOAD, uri="missing-video-is-not-opened", sha256="a" * 64),
        media=MediaInfo(fps_num=30, fps_den=1, n_frames=480, width=640, height=360, duration_us=16_000_000),
    ))
    repo.close()
    before = {path.relative_to(source): path.read_bytes() for path in source.rglob("*") if path.is_file()}
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--data-dir", str(source), "--list"],
        capture_output=True, text=True, check=False, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    listing = json.loads(result.stdout)
    assert [(row["session_id"], row["title"], row["n_frames"]) for row in listing] == [
        (session.session_id, "Controlled SampleRally", 480),
    ]
    after = {path.relative_to(source): path.read_bytes() for path in source.rglob("*") if path.is_file()}
    assert {path: after[path] for path in before} == before
    # A mode=ro reader can create these SQLite-owned files even after the last
    # writer closed its WAL catalogue. Do not use immutable mode here: an active
    # source catalogue can have committed rows that exist only in its WAL.
    assert set(after) - set(before) <= {Path("sessions.sqlite-wal"), Path("sessions.sqlite-shm")}
    if Path("sessions.sqlite-wal") not in before and Path("sessions.sqlite-wal") in after:
        assert after[Path("sessions.sqlite-wal")] == b"", "Read-only listing appended WAL records"


def test_catalogue_listing_includes_committed_rows_in_an_active_wal(tmp_path):
    source = tmp_path / "source"
    repo = SessionRepository(source)
    try:
        session = repo.save(Session(title="Initial", source=Source(kind=SourceKind.UPLOAD, uri="fixture")))
        repo.update(session.session_id, title="Committed in active WAL")
        assert (source / "sessions.sqlite-wal").stat().st_size > 0
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--data-dir", str(source), "--list"],
            capture_output=True, text=True, check=False, timeout=30,
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)[0]["title"] == "Committed in active WAL"
    finally:
        repo.close()


def test_validation_refuses_output_inside_source_data_before_loading_models(tmp_path):
    source = tmp_path / "source"
    repo = SessionRepository(source)
    session = repo.save(Session(title="Controlled", source=Source(kind=SourceKind.UPLOAD, uri="fixture")))
    repo.close()
    destination = source / "new-results"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--data-dir", str(source), "--session", session.session_id,
         "--output-dir", str(destination)],
        capture_output=True, text=True, check=False, timeout=30,
    )
    assert result.returncode != 0
    assert "outside" in result.stderr.lower() and "source" in result.stderr.lower()
    assert not destination.exists()


def test_model_staging_uses_existing_pins_and_leaves_source_untouched(tmp_path):
    from research.validate_real_video_runtime import prepare_models

    source = tmp_path / "models"
    artifact = source / "cache" / "controlled" / "weights.pt"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"preexisting controlled artifact, not an executable checkpoint")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    (source / "manifest.yaml").write_text(
        "models:\n  controlled:\n    task: shuttle\n    format: torch\n"
        "    source: {file: weights.pt}\n    sha256: pin-on-first-fetch\n    license: test\n",
        encoding="utf-8",
    )
    (source / "cache/lock.json").write_text(json.dumps({"controlled": digest}), encoding="utf-8")
    before = {path.relative_to(source): path.read_bytes() for path in source.rglob("*") if path.is_file()}
    profile = SimpleNamespace(shuttle=SimpleNamespace(model="controlled", backend="torch-cpu"))
    registry, report = prepare_models(source, tmp_path / "isolated", [profile])
    with registry.open_verified("controlled") as verified:
        assert verified.sha256 == digest
        assert verified.stream.read() == artifact.read_bytes()
    assert report["artifacts"]["controlled"]["status"] == "verified_copy"
    assert {path.relative_to(source): path.read_bytes() for path in source.rglob("*") if path.is_file()} == before


def test_missing_pins_are_not_trusted_or_downloaded(tmp_path):
    from bai_engine.runtime.registry import ModelError
    from research.validate_real_video_runtime import prepare_models

    source = tmp_path / "models"
    source.mkdir()
    (source / "manifest.yaml").write_text(
        "models:\n  controlled:\n    task: shuttle\n    format: torch\n"
        "    source: {url: 'https://invalid.example/weights.pt'}\n"
        "    sha256: pin-on-first-fetch\n    license: test\n", encoding="utf-8",
    )
    profile = SimpleNamespace(shuttle=SimpleNamespace(model="controlled", backend="torch-cpu"))
    registry, report = prepare_models(source, tmp_path / "isolated", [profile])
    with pytest.raises(ModelError, match="downloads disabled"):
        registry.path("controlled", fetch=True)
    assert report["artifacts"]["controlled"]["status"] == "missing_artifact_or_existing_pin"
    assert not (source / "cache").exists()
