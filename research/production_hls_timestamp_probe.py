"""One-variable HLS timestamp arms using immutable tiny generated originals.

No match labels/inference/GPU. CPU encoder, GOP, FPS and MP4 output unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import asdict
from pathlib import Path

import av

from bai_engine.decode import SegmentDecoder
from bai_engine.media import Tools, hls_status, plan_proxy, probe, transcode
from bai_engine.store.sessions import MediaPaths
from research.production_media_probe import ROOT, dump, identity, inspect


def run(inputs: Path, output: Path, fix: bool):
    output.mkdir(parents=True, exist_ok=False)
    snapshots = {}
    for path in [
        Path(__file__),
        ROOT / "research/production_media_probe.py",
        ROOT / "engine/src/bai_engine/media/proxy.py",
        ROOT / "engine/src/bai_engine/media/probe.py",
    ]:
        relative = path.relative_to(ROOT)
        destination = output / "executed_source" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(path.read_bytes())
        snapshots[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    tools = Tools.resolve()
    cases = []
    for source_result in json.loads((inputs / "results.json").read_text())["cases"] + [{"case": "audio_cfr30"}]:
        name = source_result["case"]
        folder = output / name
        folder.mkdir()
        if name == "audio_cfr30":
            original = folder / "source.mp4"
            command = [
                tools.ffmpeg,
                "-v",
                "error",
                "-nostdin",
                "-i",
                str(inputs / "cfr_30/source.mp4"),
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=48000:cl=stereo",
                "-map",
                "0:v",
                "-map",
                "1:a",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-threads",
                "1",
                "-shortest",
                str(original),
            ]
            subprocess.run(command, check=True)
            dump(folder / "audio_generation.json", {"command": command})
        else:
            original = next((inputs / name).glob("source.*"))
        sha = hashlib.sha256(original.read_bytes()).hexdigest()
        info = probe(original, tools)
        plan = plan_proxy(info, tools, max_height=180, prefer_gpu=False)
        media = MediaPaths(folder / "media")
        media.root.mkdir()
        job = transcode(str(original), media, plan, tools, info.duration_s)
        job.cmd[1:1] = ["-threads", "1", "-filter_threads", "1"]
        index = job.cmd.index("-f")
        job.cmd[index:index] = ["-threads", "1"]
        if fix:
            tee = job.cmd.index("tee") + 1
            job.cmd[tee] = job.cmd[tee].replace(":hls_flags=", ":avoid_negative_ts=disabled:hls_flags=")
        with (folder / "execution.log").open("wb") as log:
            log.write((json.dumps(job.cmd) + "\n").encode())
            log.flush()
            # FFmpegJob already owns safe subprocess lifecycle; its stderr is
            # recorded in an exception if failed, commands pinned above.
            job.run()
        frames = inspect(media.proxy)
        ids = [row["identity"] for row in frames]
        status = hls_status(media)
        decoder = SegmentDecoder(media, plan.frames_per_segment, threads=1)
        decoded = [
            identity(image) for segment in range(status.segments) for image in decoder.decode_segment(segment).frames
        ]
        hls_pts = []
        for segment in range(status.segments):
            import io

            payload = (media.hls / "init.mp4").read_bytes() + (media.hls / f"seg_{segment:05d}.m4s").read_bytes()
            with av.open(io.BytesIO(payload)) as container:
                stream = container.streams.video[0]
                stream.codec_context.thread_count = 1
                hls_pts += [str(frame.pts * frame.time_base) for frame in container.decode(stream)]
        expected = [str(index / plan.fps) for index in range(len(frames))]
        result = {
            "case": name,
            "plan": asdict(plan),
            "source": asdict(info),
            "source_sha256": sha,
            "source_unchanged": sha == hashlib.sha256(original.read_bytes()).hexdigest(),
            "proxy_sha256": hashlib.sha256(media.proxy.read_bytes()).hexdigest(),
            "proxy_frames": frames,
            "command": job.cmd,
            "hls_pts": hls_pts,
            "hls_pts_canonical_exact": hls_pts == expected,
            "hls_matches_proxy_fixture_identities": decoded == ids,
            "hls": asdict(status),
        }
        dump(folder / "result.json", result)
        cases.append(result)
        print(
            json.dumps(
                {
                    key: result[key]
                    for key in [
                        "case",
                        "hls_pts_canonical_exact",
                        "hls_matches_proxy_fixture_identities",
                        "proxy_sha256",
                    ]
                }
            ),
            flush=True,
        )
    unchanged = all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha for name, sha in snapshots.items())
    dump(
        output / "results.json",
        {
            "mode": "fresh CPU media timestamp component; not neural inference",
            "fix": fix,
            "source_sha256": snapshots,
            "sources_unchanged": unchanged,
            "cases": cases,
        },
    )
    if not unchanged:
        raise RuntimeError("frozen media component source changed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fix", action="store_true")
    args = parser.parse_args()
    run(args.inputs.resolve(), args.output.resolve(), args.fix)
