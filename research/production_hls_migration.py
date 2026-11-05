"""Remux an existing canonical proxy into a NEW media root; never replace assets.

This creates a reviewable migration candidate, not a deployment or URL change.
Video packet bytes and physical PTS are checked end to end. Historical media is
hashed before/after and remains untouched; failed candidates are retained.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import itertools
import json
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path

import av

from bai_engine.media import Tools, probe

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def tree_hashes(root: Path) -> dict[str, str]:
    return {str(path.relative_to(root)): sha256(path) for path in sorted(root.rglob("*")) if path.is_file()}


def verify_video_packets(original: Path, playlist: Path, fps: Fraction) -> dict:
    """No decode/inference. Reordered packet PTS and payload must both match."""
    count = 0
    with av.open(str(original)) as before, av.open(str(playlist)) as after:
        selected = before.streams.video[0]
        generated = after.streams.video[0]
        left = (packet for packet in before.demux(selected) if packet.size)
        right = (packet for packet in after.demux(generated) if packet.size)
        minimum = None
        for previous, following in itertools.zip_longest(left, right):
            if previous is None or following is None:
                raise ValueError("video packet count changed during remux")
            if bytes(previous) != bytes(following):
                raise ValueError(f"video packet payload changed at decode-order packet {count}")
            old_pts = previous.pts * previous.time_base
            new_pts = following.pts * following.time_base
            if old_pts != new_pts or (new_pts * fps).denominator != 1:
                raise ValueError(f"video presentation changed at decode-order packet {count}")
            minimum = new_pts if minimum is None else min(minimum, new_pts)
            count += 1
    if minimum != 0:
        raise ValueError("canonical video presentation does not begin at zero")
    # SegmentDecoder assigns k*F to each segment. Retain that contract when
    # stream-copying: a differently keyed input must fail rather than acquire
    # fabricated canonical segment boundaries.
    segment_frames = max(1, round(float(fps) * 2))
    emitted = 0
    init = playlist.parent / "init.mp4"
    for index, path in enumerate(sorted(playlist.parent.glob("seg_*.m4s"))):
        with av.open(io.BytesIO(init.read_bytes() + path.read_bytes())) as container:
            stream = container.streams.video[0]
            points = [packet.pts * packet.time_base for packet in container.demux(stream) if packet.size]
        if not points or min(points) != Fraction(index * segment_frames) / fps:
            raise ValueError("source GOP cannot preserve canonical segment boundaries")
        if index * segment_frames != emitted or len(points) > segment_frames:
            raise ValueError("source GOP cannot preserve canonical segment frame counts")
        emitted += len(points)
    if emitted != count:
        raise ValueError("segment frame count does not cover the canonical proxy")
    return {
        "video_packets": count,
        "video_packet_bytes_identical": True,
        "video_presentation_pts_identical": True,
        "minimum_video_pts": str(minimum),
    }


def migrate(source: Path, output: Path) -> dict:
    source, output = source.resolve(), output.resolve()
    if output == source or source in output.parents:
        raise ValueError("output must be outside the immutable input media root")
    if output.exists():
        raise FileExistsError(output)
    original = source / "proxy.mp4"
    if not original.is_file():
        raise ValueError("input root must contain the canonical proxy.mp4")
    tools = Tools.resolve()
    info = probe(original, tools)
    if info.codec != "h264" or not info.packet_cadence_complete or info.packet_pts_variable is not False:
        raise ValueError("migration requires a fully inspected constant-cadence H.264 proxy")
    before = tree_hashes(source)
    output.mkdir(parents=True, exist_ok=False)
    (output / "hls").mkdir()
    snapshots = {}
    for path in [
        Path(__file__),
        ROOT / "engine/src/bai_engine/media/probe.py",
        ROOT / "engine/src/bai_engine/media/proxy.py",
    ]:
        relative = path.relative_to(ROOT)
        destination = output / "executed_source" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(path.read_bytes())
        snapshots[str(relative)] = sha256(path)
    shutil.copy2(original, output / "proxy.mp4")
    frames_per_segment = max(1, round(float(info.fps) * 2))
    command = [
        tools.ffmpeg,
        "-hide_banner",
        "-nostdin",
        "-n",
        "-loglevel",
        "error",
        "-i",
        str(original),
        "-map",
        f"0:{info.video_stream_index}",
    ]
    if info.has_audio:
        command += ["-map", "0:a:0?"]
    command += [
        "-c",
        "copy",
        "-f",
        "hls",
        "-hls_time",
        f"{frames_per_segment / float(info.fps) * 0.999:.4f}",
        "-hls_playlist_type",
        "event",
        "-hls_segment_type",
        "fmp4",
        "-hls_fmp4_init_filename",
        "init.mp4",
        "-hls_segment_filename",
        "hls/seg_%05d.m4s",
        "-hls_flags",
        "independent_segments+temp_file",
        "-avoid_negative_ts",
        "disabled",
        "hls/index.m3u8",
    ]
    manifest = {
        "schema_version": 1,
        "status": "running",
        "operation": "new-root copy/remux; no deployment",
        "input_root": str(source),
        "output_root": str(output),
        "input_hashes": before,
        "executed_source_sha256": snapshots,
        "command": command,
        "fps": str(info.fps),
        "frames_per_segment": frames_per_segment,
        "limitations": [
            "Audio packets are copied; audible synchronization is not human reviewed.",
            "No API URL/cache pointer is changed; release requires explicit routing review.",
        ],
    }
    try:
        with (output / "remux.log").open("wb") as log:
            subprocess.run(command, cwd=output, stdout=log, stderr=subprocess.STDOUT, timeout=600, check=True)
        manifest["verification"] = verify_video_packets(original, output / "hls/index.m3u8", info.fps)
        manifest["input_hashes_after"] = tree_hashes(source)
        if before != manifest["input_hashes_after"]:
            raise ValueError("input media changed during migration")
        if sha256(original) != sha256(output / "proxy.mp4"):
            raise ValueError("canonical MP4 copy changed")
        manifest["status"] = "completed_review_candidate"
        manifest["output_hashes"] = {
            str(path.relative_to(output)): sha256(path)
            for path in sorted((output / "hls").rglob("*"))
            if path.is_file()
        }
        manifest["output_hashes"]["proxy.mp4"] = sha256(output / "proxy.mp4")
    except Exception as error:
        manifest["status"] = "failed_retained"
        manifest["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        (output / "migration_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--media-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(migrate(args.media_root, args.output), indent=2))
