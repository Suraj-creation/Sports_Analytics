"""Tiny deterministic source→actual proxy/HLS experiments; CPU only, new output.

Barcodes establish fixture frame identity. They are not a general-source mapping
algorithm. No original match media, labels, deployed server or GPU is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

import av
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bai_engine.decode import SegmentDecoder  # noqa: E402
from bai_engine.media import Tools, hls_status, plan_proxy, probe, transcode, validate  # noqa: E402
from bai_engine.store.sessions import MediaPaths  # noqa: E402


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, default=str, allow_nan=False) + "\n")


def pixels(index):
    image = np.full((180, 320, 3), 25, np.uint8)
    for bit in range(9):
        if index >> bit & 1:
            x = round(320 * (0.03 + 0.105 * bit))
            image[60:120, x : x + 20] = 230
    return image


def identity(image):
    return sum(
        (
            int(
                image[65:115, round(320 * (0.03 + 0.105 * bit)) + 3 : round(320 * (0.03 + 0.105 * bit)) + 17].mean()
                > 127
            )
            << bit
        )
        for bit in range(9)
    )


def make_source(path, fps, *, irregular=False, offset_s=0):
    count = round(float(fps) * 2) + 7
    with av.open(str(path), "w") as container:
        stream = container.add_stream("libx264", rate=fps)
        stream.width, stream.height, stream.pix_fmt = 320, 180, "yuv420p"
        stream.codec_context.thread_count = 1
        stream.options = {"bf": "0", "preset": "ultrafast", "crf": "10"}
        stream.time_base = stream.codec_context.time_base = Fraction(1, 90000)
        for frame in range(count):
            image = av.VideoFrame.from_ndarray(pixels(frame), format="bgr24")
            image.time_base = Fraction(1, 90000)
            # Alternating half/one-and-a-half nominal periods retains the
            # nominal mean but genuinely changes presentation cadence.
            time = Fraction(frame, 1) / fps
            if irregular and frame % 2:
                time -= Fraction(1, 2) / fps
            image.pts = round((time + offset_s) * 90000)
            for packet in stream.encode(image):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    return count


def inspect(path):
    with av.open(str(path)) as container:
        stream = container.streams.video[0]
        stream.codec_context.thread_count = 1
        return [
            {
                "index": i,
                "pts": frame.pts,
                "time_base": str(frame.time_base),
                "time": str(frame.pts * frame.time_base),
                "identity": identity(frame.to_ndarray(format="bgr24")),
            }
            for i, frame in enumerate(container.decode(stream))
        ]


def run(output, existing_inputs=None, fractional=False):
    output.mkdir(parents=True, exist_ok=False)
    sources = [
        ROOT / "engine/src/bai_engine/media/probe.py",
        ROOT / "engine/src/bai_engine/media/proxy.py",
        ROOT / "engine/src/bai_engine/decode.py",
        ROOT / "engine/src/bai_engine/timeline.py",
        Path(__file__),
    ]
    source_hashes = {}
    for source in sources:
        relative = source.relative_to(ROOT)
        snapshot = output / "executed_source" / relative
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(source.read_bytes())
        source_hashes[str(relative)] = hashlib.sha256(source.read_bytes()).hexdigest()
    tools = Tools.resolve()
    cases = [(f"cfr_{rate}", Fraction(rate), "mp4", False, 0) for rate in [24, 25, 30, 50, 60]]
    cases += [
        ("vfr_matroska", Fraction(30), "mkv", True, 0),
        ("vfr_mp4", Fraction(30), "mp4", True, 0),
        ("offset_cfr30", Fraction(30), "mp4", False, 2),
    ]
    if fractional:
        cases = [(f"cfr_{n}_1001", Fraction(n, 1001), "mp4", False, 0) for n in [30000, 60000]]
    results = []
    for name, rate, extension, irregular, offset in cases:
        folder = output / name
        folder.mkdir()
        if existing_inputs is None:
            original = folder / f"source.{extension}"
            expected = make_source(original, rate, irregular=irregular, offset_s=offset)
        else:
            original = existing_inputs / name / f"source.{extension}"
            expected = len(inspect(original))
            dump(folder / "source_reference.json", {"path": str(original), "generated": False})
        original_hash = hashlib.sha256(original.read_bytes()).hexdigest()
        source_frames = inspect(original)
        source_info = probe(original, tools)
        validate(source_info, max_duration_s=60)
        plan = plan_proxy(source_info, tools, max_height=180, prefer_gpu=False)
        media = MediaPaths(folder / "media")
        media.root.mkdir()
        job = transcode(str(original), media, plan, tools, source_info.duration_s)
        job.cmd[1:1] = ["-threads", "1", "-filter_threads", "1"]
        index = job.cmd.index("-f")
        job.cmd[index:index] = ["-threads", "1"]
        job.run()
        proxy_frames = inspect(media.proxy)
        status = hls_status(media)
        decoder = SegmentDecoder(media, plan.frames_per_segment, threads=1)
        hls_ids = [
            identity(frame) for segment in range(status.segments) for frame in decoder.decode_segment(segment).frames
        ]
        proxy_ids = [row["identity"] for row in proxy_frames]
        source_deltas = sorted(set(str(Fraction(b["time"]) - Fraction(a["time"])) for a, b in pairwise(source_frames)))
        result = {
            "case": name,
            "source": asdict(source_info),
            "expected_source_frames": expected,
            "probe_variable_frame_rate": source_info.variable_frame_rate,
            "source_pts_deltas": source_deltas,
            "plan": asdict(plan),
            "command": job.cmd,
            "source_sha256": original_hash,
            "source_unchanged": original_hash == hashlib.sha256(original.read_bytes()).hexdigest(),
            "source_frames": source_frames,
            "proxy_frames": proxy_frames,
            "hls_matches_proxy_fixture_identities": hls_ids == proxy_ids,
            "canonical_grid_exact": all(
                Fraction(row["time"]) == Fraction(i, 1) / plan.fps for i, row in enumerate(proxy_frames)
            ),
            "missing_source_identities": sorted(set(range(expected)) - set(proxy_ids)),
            "reused_source_identity_count": len(proxy_ids) - len(set(proxy_ids)),
            "hls": asdict(status),
        }
        dump(folder / "result.json", result)
        results.append(result)
        print(
            json.dumps(
                {
                    key: result[key]
                    for key in [
                        "case",
                        "source_pts_deltas",
                        "probe_variable_frame_rate",
                        "hls_matches_proxy_fixture_identities",
                        "canonical_grid_exact",
                        "reused_source_identity_count",
                    ]
                }
            ),
            flush=True,
        )
    unchanged = all(
        hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == sha for name, sha in source_hashes.items()
    )
    dump(
        output / "results.json",
        {
            "mode": "actual tiny CPU media transcodes; not neural inference or real sport accuracy",
            "source_sha256": source_hashes,
            "sources_unchanged": unchanged,
            "cases": results,
        },
    )
    if not unchanged:
        raise RuntimeError("owning media/harness source changed during experiment")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--existing-inputs", type=Path)
    parser.add_argument("--fractional", action="store_true")
    arguments = parser.parse_args()
    run(
        arguments.output.resolve(),
        arguments.existing_inputs.resolve() if arguments.existing_inputs else None,
        arguments.fractional,
    )
