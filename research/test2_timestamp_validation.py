"""Verify the complete source/proxy rational timestamp mapping for a CFR upload."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from fractions import Fraction
from itertools import pairwise
from pathlib import Path


def compare_timestamps(source_times, proxy_times):
    if not source_times or len(source_times) != len(proxy_times):
        raise ValueError("source/proxy frame population mismatch")
    if any(b <= a for a, b in pairwise(source_times)):
        raise ValueError("nonmonotonic source PTS")
    if source_times != proxy_times:
        raise ValueError("source/proxy presentation timestamps differ")
    return {
        "frame_count": len(source_times),
        "every_source_proxy_timestamp_equal": True,
        "first_time": str(source_times[0]),
        "last_time": str(source_times[-1]),
        "source_proxy_frame_mapping": "identity; exact rational presentation timestamps",
    }


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify(source_pts: Path, proxy: Path, inference_path: Path, output: Path):
    inference = json.loads(inference_path.read_text())
    if inference.get("status") != "completed" or sha(proxy) != inference["proxy_sha256"]:
        raise ValueError("completed source-bound proxy required")
    with source_pts.open() as stream:
        rows = list(csv.DictReader(stream))
    if [int(row["source_frame"]) for row in rows] != list(range(inference["frames_processed"])):
        raise ValueError("source timestamp map must cover every processed frame")
    source_times = [Fraction(int(row["pts"]) * int(row["time_base_num"]), int(row["time_base_den"])) for row in rows]
    header_cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_streams", "-of", "json", str(proxy)]
    header = json.loads(subprocess.check_output(header_cmd))["streams"][0]
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_frames",
        "-show_entries",
        "frame=pts",
        "-of",
        "json",
        str(proxy),
    ]
    process = subprocess.run(command, check=True, capture_output=True, text=True)
    pts = [frame["pts"] for frame in json.loads(process.stdout)["frames"]]
    times = [pts_value * Fraction(header["time_base"]) for pts_value in pts]
    result = compare_timestamps(source_times, times)
    result.update(
        {
            "source_pts_sha256": sha(source_pts),
            "inference_sha256": sha(inference_path),
            "proxy_sha256": sha(proxy),
            "proxy_metadata": header,
            "ffprobe_commands": [header_cmd, command],
            "proxy_decode_stderr": process.stderr,
            "scope": "full timestamp/count equality; spatial rescaling/compression are separate",
            "source_sha256": inference["source_sha256"],
        }
    )
    output.mkdir(parents=True, exist_ok=False)
    with (output / "proxy_frame_pts.csv").open("x") as stream:
        writer = csv.writer(stream)
        writer.writerow(["proxy_frame", "pts", "time_base", "timestamp_rational"])
        writer.writerows([i, p, header["time_base"], str(t)] for i, (p, t) in enumerate(zip(pts, times, strict=True)))
    (output / "timestamp_validation.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pts", required=True, type=Path)
    parser.add_argument("--proxy", required=True, type=Path)
    parser.add_argument("--inference-json", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.source_pts, args.proxy, args.inference_json, args.output), indent=2))
