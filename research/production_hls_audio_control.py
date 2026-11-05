"""CPU-only AAC-delay isolation, no B frames; this does not verify NVENC."""

from __future__ import annotations

import argparse
import hashlib
import io
from dataclasses import asdict
from pathlib import Path

import av

from bai_engine.media import Tools, hls_status, plan_proxy, probe, transcode
from bai_engine.store.sessions import MediaPaths
from research.production_media_probe import ROOT, dump, inspect


def run(source: Path, output: Path):
    output.mkdir(parents=True, exist_ok=False)
    for path in [
        Path(__file__),
        ROOT / "engine/src/bai_engine/media/proxy.py",
        ROOT / "engine/src/bai_engine/media/probe.py",
    ]:
        destination = output / "executed_source" / path.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(path.read_bytes())
    tools = Tools.resolve()
    info = probe(source, tools)
    plan = plan_proxy(info, tools, max_height=180, prefer_gpu=False)
    assert info.has_audio
    results = []
    for name in ["legacy_mux", "corrected_mux"]:
        folder = output / name
        folder.mkdir()
        media = MediaPaths(folder / "media")
        media.root.mkdir()
        job = transcode(str(source), media, plan, tools, info.duration_s)
        job.cmd[1:1] = ["-threads", "1", "-filter_threads", "1"]
        index = job.cmd.index("-f")
        job.cmd[index:index] = ["-threads", "1"]
        job.cmd[job.cmd.index("-bf") + 1] = "0"
        if name == "legacy_mux":
            tee = job.cmd.index("tee") + 1
            job.cmd[tee] = job.cmd[tee].replace(":avoid_negative_ts=disabled", "")
        job.run()
        frames = inspect(media.proxy)
        pts = []
        for segment in range(hls_status(media).segments):
            with av.open(
                io.BytesIO((media.hls / "init.mp4").read_bytes() + (media.hls / f"seg_{segment:05d}.m4s").read_bytes())
            ) as container:
                stream = container.streams.video[0]
                stream.codec_context.thread_count = 1
                pts.extend(str(frame.pts * frame.time_base) for frame in container.decode(stream))
        result = {
            "case": name,
            "plan": asdict(plan),
            "command": job.cmd,
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "proxy_sha256": hashlib.sha256(media.proxy.read_bytes()).hexdigest(),
            "proxy_frames": frames,
            "hls_pts": pts,
        }
        dump(folder / "result.json", result)
        results.append(result)
    dump(
        output / "results.json",
        {
            "mode": "CPU x264 bf0 isolates AAC timestamp delay; NOT NVENC validation",
            "cases": results,
            "mp4_bytes_identical": results[0]["proxy_sha256"] == results[1]["proxy_sha256"],
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.source.resolve(), args.output.resolve())
