"""Full-source causal scene-hypothesis screen on exact cached proxy pixels.

No model runs and no ground-truth interval is read. Prior boxes/scene admission
are recorded perception context; the observer never changes them or any event.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import cv2
import msgpack

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bai_badminton.perception.scene import CutDetector  # noqa: E402
from bai_badminton.perception.scene_change import ForegroundRegion, SceneContinuityDetector  # noqa: E402
from bai_engine.decode import SegmentDecoder  # noqa: E402
from bai_engine.store.sessions import MediaPaths  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run, out = args.run.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cv2.setNumThreads(1)
    metadata = json.loads((run / "benchmark_metadata.json").read_text())
    video_hash = metadata["source_video_sha256"]
    media = MediaPaths(run / "runtime/media" / video_hash)
    paths = sorted(run.glob("runtime/sessions/*/perception/*.msgpack"))
    if len({path.parent for path in paths}) != 1:
        raise ValueError("one source-bound perception cache is required")
    raw, chunks = {}, []
    for path in paths:
        record = msgpack.unpackb(path.read_bytes(), raw=False)
        raw.update({row["f"]: row for row in record["frames"]})
        chunks.append((record["start"], record["end"]))
    assert set(raw) == set(range(metadata["frame_count"]))
    decoder = SegmentDecoder(media, 60, threads=1)
    observer, histogram = SceneContinuityDetector(), CutDetector()
    source = [
        Path(__file__),
        ROOT / "sports/badminton/src/bai_badminton/perception/scene_change.py",
        ROOT / "sports/badminton/src/bai_badminton/perception/scene.py",
        ROOT / "engine/src/bai_engine/decode.py",
    ]
    hashes = {str(path.relative_to(ROOT)): sha(path) for path in source}
    archive = out / "executed_source"
    archive.mkdir()
    for path in source:
        target = archive / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    started = time.monotonic()
    statuses, reasons = Counter(), Counter()
    hypotheses, cuts = [], []
    count = 0
    with (out / "scene_hypotheses.jsonl").open("x") as stream:
        for segment, (start, end) in enumerate(chunks):
            decoded = decoder.decode_segment(segment)
            assert decoded.start == start and decoded.end == end
            for index, pixels in enumerate(decoded.frames):
                frame = start + index
                current, previous = raw[frame], raw.get(frame - 1, {})
                hard_cut = histogram.update(pixels)
                if hard_cut:
                    cuts.append(frame)
                regions = [
                    ForegroundRegion(
                        frame - 1,
                        f"track:{p['t']}:shot:{previous.get('sh')}",
                        tuple(p["b"]),
                        p.get("dm"),
                        previous.get("do"),
                    )
                    for p in previous.get("p", [])
                ]
                evidence = observer.observe(
                    frame,
                    pixels,
                    previous_regions=regions,
                    previous_view_valid=previous.get("v") == "main" and not previous.get("r"),
                    current_view_valid=current.get("v") == "main" and not current.get("r"),
                    hard_cut=hard_cut,
                )
                assert not evidence.authoritative
                statuses[evidence.status] += 1
                reasons.update(evidence.reasons)
                if evidence.hypothesis:
                    hypotheses.append(frame)
                row = {
                    "scene": asdict(evidence),
                    "legacy_histogram_cut": hard_cut,
                    "cached_shot": current.get("sh"),
                    "cached_calibration": current.get("cs"),
                    "cached_view": current.get("v"),
                    "cached_excluded": current.get("r"),
                }
                stream.write(json.dumps(row, allow_nan=False) + "\n")
                count += 1
            if segment % 30 == 0:
                print("screened", end, "hypotheses", len(hypotheses), flush=True)
    unchanged = all(sha(ROOT / name) == value for name, value in hashes.items())
    manifest = {
        "mode": "causal image-content hypothesis screen; no model inference or event/scene authority",
        "scope": "full original canonical HLS proxy decode + recorded prior-frame ROI/view context",
        "run": str(run),
        "source_video_sha256": video_hash,
        "proxy_sha256": sha(media.proxy),
        "metadata_sha256": sha(run / "benchmark_metadata.json"),
        "cache_sha256": {path.name: sha(path) for path in paths},
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_sha256": hashes,
        "source_unchanged": unchanged,
        "configuration": {
            "analysis_width": 480,
            "history_pairs": 2,
            "adaptive_ratio": 3,
            "minimum_discontinuity": 15,
            "background_consistency_min": 0.5,
            "flow_forward_backward_tolerance_px": 1.0,
        },
        "frames": count,
        "elapsed_seconds": time.monotonic() - started,
        "status_counts": dict(statuses),
        "reason_counts": dict(reasons),
        "hypothesis_frames": hypotheses,
        "legacy_histogram_cuts": cuts,
        "ground_truth_values_read": False,
        "authoritative_decisions": 0,
        "diagnostic_sha256": sha(out / "scene_hypotheses.jsonl"),
        "limits": [
            "ROI boxes are model observations, not independently reviewed person labels",
            "No scene/cut accuracy denominator without reviewed labels",
            "Raw adaptive patch scores are not calibrated scene probabilities",
            "Multiregion occlusion can remain indistinguishable from a same-view edit",
        ],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if not unchanged:
        raise RuntimeError("executing scene probe source changed")
    print(
        json.dumps({key: manifest[key] for key in ("frames", "elapsed_seconds", "status_counts", "hypothesis_frames")})
    )


if __name__ == "__main__":
    main()
