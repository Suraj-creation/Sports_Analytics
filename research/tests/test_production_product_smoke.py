"""Small controls for the isolated real-server smoke harness, no neural work."""

import json
import subprocess
from pathlib import Path

import pytest

from research import production_product_smoke as smoke


def test_cpu_capability_adapter_never_advertises_gpu_encoder(tmp_path):
    tool = smoke.cpu_ffmpeg(tmp_path)
    listed = subprocess.run([str(tool), "-hide_banner", "-encoders"], capture_output=True, check=True)
    assert b"libx264" in listed.stdout
    assert b"h264_nvenc" not in listed.stdout
    rejected = subprocess.run([str(tool), "-c:v", "h264_nvenc"], capture_output=True, check=False)
    assert rejected.returncode == 64
    version = subprocess.run([str(tool), "-version"], capture_output=True, check=True)
    assert version.stdout.startswith(b"ffmpeg version")
    assert len((tmp_path / "ffmpeg_commands.jsonl").read_text().splitlines()) == 3


def test_prepare_refuses_existing_output_and_deployment_build(tmp_path):
    build = tmp_path / "build"
    build.mkdir()
    (build / "assets").mkdir()
    (build / "index.html").write_text("<div>isolated</div>")
    fixture = tmp_path / "fixture.mp4"
    fixture.write_bytes(b"own fixture")
    existing = tmp_path / "existing"
    existing.mkdir()
    with pytest.raises(FileExistsError):
        smoke.prepare(existing, build, fixture)
    with pytest.raises(ValueError, match="deployment"):
        smoke.prepare(tmp_path / "unused", smoke.ROOT / "apps/web/dist", fixture)
    assert not (tmp_path / "unused").exists()


def test_multipart_preserves_fixture_bytes_and_declares_video(tmp_path):
    fixture = tmp_path / "tiny.mp4"
    fixture.write_bytes(b"\x00\xffactualfixture\r\n")
    payload, kind = smoke.multipart(fixture)
    assert b'filename="tiny.mp4"' in payload
    assert fixture.read_bytes() in payload
    assert "multipart/form-data; boundary=" in kind


def test_empty_export_observation_does_not_invent_schema_or_events():
    measured = smoke.export_summary(
        {
            "rallies.csv": b"match_id\r\n",
            "legacy.csv": b"start_time,end_time\r\n",
            "events.jsonl": b"",
            "summary.json": json.dumps({"rallies": 0}).encode(),
        }
    )
    assert measured["rallies_columns"] == ["match_id"]
    assert measured["rally_rows"] == measured["events"] == 0
    assert measured["summary"] == {"rallies": 0}


def test_actual_smoke_results_require_matching_pixels_and_owned_exports():
    baseline = smoke.ARTIFACTS / "prod_20261105_product_smoke_v2/results.json"
    if not baseline.exists():
        pytest.skip("The retained local browser control is not packaged with unit tests")
    result = json.loads(baseline.read_text())
    smoke.validate_result(result)
    with pytest.raises(AssertionError, match="schema"):
        smoke.validate_result(result, expect_fixes=True)
    result["browser_seeks"][0]["identity"] = -1
    with pytest.raises(AssertionError, match="frame identity"):
        smoke.validate_result(result)


@pytest.fixture
def closed_completed_run(tmp_path):
    from bai_engine.schema import Event, MediaInfo, Provenance, Session, Source, SourceKind
    from bai_engine.store import SessionRepository

    run = tmp_path / "completed"
    repo = SessionRepository(run / "data")
    source_hash = "a" * 64
    session = repo.save(
        Session(
            session_id="CopiedClosedResult",
            title="Completed fixture",
            status="analysed",
            frontier_frame=0,
            analysed_frames=1,
            source=Source(kind=SourceKind.UPLOAD, uri="/private/never-open-source", sha256=source_hash),
            media=MediaInfo(fps_num=30, fps_den=1, n_frames=1, width=320, height=180, duration_us=33333),
        )
    )
    repo.events(session.session_id).append(
        Event(
            session_id=session.session_id,
            type="contact",
            frame_start=0,
            frame_end=0,
            pts_us=0,
            provenance=Provenance(model="copy-contract-control"),
        )
    )
    repo.close()
    (run / "session.json").write_text(session.model_dump_json())
    (run / "inference.json").write_text(
        json.dumps(
            {
                "status": "completed",
                "frames_processed": 1,
                "event_counts": {"contact": 1},
            }
        )
    )
    media = run / "data/media" / source_hash / "hls"
    media.mkdir(parents=True)
    (media / "index.m3u8").write_text("#EXTM3U\n#EXT-X-ENDLIST\n")
    (media / "init.mp4").write_bytes(b"asset copy control; not decoded in this contract test")
    return run


def test_completed_product_stages_independent_bytes_without_opening_original_sqlite(
    tmp_path,
    closed_completed_run,
    monkeypatch,
):
    import sqlite3

    run = closed_completed_run
    connect = sqlite3.connect

    def owned_connections_only(database, *args, **kwargs):
        if Path(database).resolve().is_relative_to(run):
            raise AssertionError("An original database must never receive a SQLite connection")
        return connect(database, *args, **kwargs)

    monkeypatch.setattr(sqlite3, "connect", owned_connections_only)
    before = {str(p): smoke.digest(p) for p in run.rglob("*") if p.is_file()}
    output = tmp_path / "isolated_product"
    output.mkdir()
    config = {"output": str(output)}
    record = smoke.stage_completed_run(run, config)
    assert record["original_sqlite_connection_opened"] is False
    assert config["start_engine"] is False
    assert record["expected"]["live_event_counts"] == {"contact": 1}
    assert record["expected"]["source_sha256"] == "a" * 64
    assert all(smoke.digest(Path(name)) == value for name, value in before.items())
    assert all(p["source"] != p["destination"] for p in record["physical_copies"])
    assert not list(run.rglob("*-wal")) and not list(run.rglob("*-shm"))


def test_completed_product_refuses_an_original_with_a_wal_sidecar(tmp_path, closed_completed_run):
    database = closed_completed_run / "data/sessions/CopiedClosedResult/events.sqlite"
    database.with_name(database.name + "-wal").write_bytes(b"active source sidecar must not be ignored")
    output = tmp_path / "refused"
    output.mkdir()
    with pytest.raises(ValueError, match="sidecars"):
        smoke.stage_completed_run(closed_completed_run, {"output": str(output)})
    assert not (output / "data").exists()


def test_completed_product_refuses_incomplete_frame_coverage(tmp_path, closed_completed_run):
    report = closed_completed_run / "inference.json"
    report.write_text(json.dumps({"status": "completed", "frames_processed": 0, "event_counts": {}}))
    output = tmp_path / "refused"
    output.mkdir()
    with pytest.raises(ValueError, match="frame extent"):
        smoke.stage_completed_run(closed_completed_run, {"output": str(output)})
