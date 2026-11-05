"""Migration is a new-root packet-preserving operation, never asset replacement."""

from fractions import Fraction

import pytest

from bai_engine.media import Tools, plan_proxy, probe, transcode
from bai_engine.store.sessions import MediaPaths
from research.production_hls_migration import migrate
from research.production_media_probe import inspect, make_source


def test_migration_preserves_all_inputs_and_canonical_packet_images(tmp_path):
    source = tmp_path / "source.mp4"
    make_source(source, Fraction(30))
    tools = Tools.resolve()
    info = probe(source, tools)
    plan = plan_proxy(info, tools, max_height=180, prefer_gpu=False)
    media = MediaPaths(tmp_path / "original")
    media.root.mkdir()
    job = transcode(str(source), media, plan, tools, info.duration_s)
    job.cmd[1:1] = ["-threads", "1", "-filter_threads", "1"]
    index = job.cmd.index("-f")
    job.cmd[index:index] = ["-threads", "1"]
    # Reproduce historical positive timestamp-shifting HLS without altering
    # encoded video. The migration reads MP4 and retains those old HLS bytes.
    tee = job.cmd.index("tee") + 1
    job.cmd[tee] = job.cmd[tee].replace(":avoid_negative_ts=disabled", "")
    job.run()
    before = {str(path.relative_to(media.root)): path.read_bytes() for path in media.root.rglob("*") if path.is_file()}
    destination = tmp_path / "candidate"
    result = migrate(media.root, destination)
    assert result["status"] == "completed_review_candidate"
    assert result["verification"]["video_packet_bytes_identical"]
    assert result["verification"]["video_presentation_pts_identical"]
    assert result["verification"]["video_packets"] == 67
    assert inspect(destination / "proxy.mp4") == inspect(media.proxy)
    assert {
        str(path.relative_to(media.root)): path.read_bytes() for path in media.root.rglob("*") if path.is_file()
    } == before
    with pytest.raises(FileExistsError):
        migrate(media.root, destination)
    with pytest.raises(ValueError, match="outside"):
        migrate(media.root, media.root / "nested")


def test_migration_rejects_missing_input_and_retains_existing_output(tmp_path):
    source = tmp_path / "input"
    source.mkdir()
    existing = tmp_path / "existing"
    existing.mkdir()
    marker = existing / "marker.txt"
    marker.write_text("unchanged")
    with pytest.raises(FileExistsError):
        migrate(source, existing)
    assert marker.read_text() == "unchanged"
    with pytest.raises(ValueError, match="canonical proxy"):
        migrate(source, tmp_path / "new")


def test_noncanonical_gop_is_rejected_with_failed_candidate_retained(tmp_path):
    root = tmp_path / "not_a_proxy"
    root.mkdir()
    # This otherwise valid CFR H.264 source has no keyframe at the two-second
    # canonical boundary. Merely copying its packets cannot create that IDR.
    make_source(root / "proxy.mp4", Fraction(30))
    original = (root / "proxy.mp4").read_bytes()
    output = tmp_path / "failed_candidate"
    with pytest.raises(ValueError, match="canonical segment frame counts"):
        migrate(root, output)
    import json

    assert json.loads((output / "migration_manifest.json").read_text())["status"] == "failed_retained"
    assert (root / "proxy.mp4").read_bytes() == original
    assert (output / "proxy.mp4").read_bytes() == original
