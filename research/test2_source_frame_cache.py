"""Label-free exact-PTS source JPEG preparation for later diagnostic rendering."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.test2_failure_package import sha, verified_pts, write  # noqa: E402


def prepare(source: Path, pts_csv: Path, output: Path, n_frames: int, rate: Fraction) -> dict:
    import av
    import cv2

    started = datetime.now(UTC).isoformat()
    timer = time.monotonic()
    source_hash, pts_hash = sha(source), sha(pts_csv)
    mapping = verified_pts(pts_csv, n_frames, rate)
    output.mkdir(parents=True, exist_ok=False)
    (output / "frames").mkdir()
    container = av.open(str(source))
    stream = container.streams.video[0]
    stream.codec_context.thread_count = 2
    previous_threads = cv2.getNumThreads()
    cv2.setNumThreads(1)
    records = []
    try:
        if stream.average_rate != rate or any(base != stream.time_base for _, base in mapping.values()):
            raise ValueError("source stream differs from audited exact PTS grid")
        width, height = 960, round(stream.height * 960 / stream.width)
        source_size = [stream.width, stream.height]
        for index, frame in enumerate(container.decode(stream)):
            if index >= n_frames or mapping[index] != (frame.pts, stream.time_base):
                raise ValueError("decoded source frame differs from ordered PTS map")
            target = output / "frames" / f"{index}.jpg"
            pixels = cv2.resize(frame.to_ndarray(format="bgr24"), (width, height), interpolation=cv2.INTER_AREA)
            if not cv2.imwrite(str(target), pixels, [cv2.IMWRITE_JPEG_QUALITY, 88]):
                raise ValueError("source JPEG write failed")
            records.append(
                {
                    "frame": index,
                    "path": f"frames/{index}.jpg",
                    "sha256": sha(target),
                    "pts": frame.pts,
                    "time_base": str(stream.time_base),
                    "size": [width, height],
                }
            )
            if index and index % 1000 == 0:
                print(
                    json.dumps({"source_frames_written": index + 1, "elapsed_seconds": time.monotonic() - timer}),
                    flush=True,
                )
        if len(records) != n_frames:
            raise ValueError("source decode incomplete")
    finally:
        container.close()
        cv2.setNumThreads(previous_threads)
    if sha(source) != source_hash or sha(pts_csv) != pts_hash:
        raise ValueError("source or PTS audit changed during source-frame preparation")
    (output / "executed_source.py").write_bytes(Path(__file__).read_bytes())
    manifest = {
        "schema": "exact-source-frame-cache-v1",
        "source_only": True,
        "labels_or_predictions_accessed": False,
        "source": str(source.resolve()),
        "source_sha256": source_hash,
        "source_pts_csv": str(pts_csv.resolve()),
        "source_pts_sha256": pts_hash,
        "source_sha256_before_after_equal": True,
        "n_frames": n_frames,
        "fps": str(rate),
        "source_size": source_size,
        "display_size": [width, height],
        "transform": {"decode": "PyAV BGR24", "resize": "cv2.INTER_AREA", "jpeg_quality": 88},
        "bounded_threads": {"decoder": 2, "opencv": 1},
        "versions": {"pyav": av.__version__, "opencv": cv2.__version__},
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "elapsed_seconds": time.monotonic() - timer,
        "script_sha256": sha(Path(__file__)),
        "helper_sha256": sha(ROOT / "research/test2_failure_package.py"),
        "command": sys.argv,
        "frames": records,
    }
    write(output / "manifest.json", manifest)
    return manifest


def verified_cache(
    cache: Path,
    *,
    source_sha256: str,
    pts_csv: Path,
    n_frames: int,
    rate: Fraction,
    source_size: list[int],
    mapping: dict,
    selected: list[int],
) -> tuple[dict, dict[int, Path]]:
    """Verify complete provenance and EVERY selected regular image before copying."""
    import cv2

    manifest_path = cache / "manifest.json"
    if cache.resolve() != cache.absolute() or (cache / "frames").is_symlink() or manifest_path.is_symlink():
        raise ValueError("source-frame cache must use regular non-symlink paths")
    manifest = json.loads(manifest_path.read_text())
    if (
        manifest.get("schema") != "exact-source-frame-cache-v1"
        or manifest.get("source_only") is not True
        or manifest.get("labels_or_predictions_accessed") is not False
        or manifest.get("source_sha256_before_after_equal") is not True
        or manifest.get("source_sha256") != source_sha256
        or manifest.get("source_pts_sha256") != sha(pts_csv)
        or manifest.get("n_frames") != n_frames
        or manifest.get("fps") != str(rate)
        or manifest.get("source_size") != source_size
        or manifest.get("transform") != {"decode": "PyAV BGR24", "resize": "cv2.INTER_AREA", "jpeg_quality": 88}
    ):
        raise ValueError("source-frame cache provenance differs from genuine source/PTS grid")
    records = manifest.get("frames", [])
    expected_size = [960, round(source_size[1] * 960 / source_size[0])]
    if manifest.get("display_size") != expected_size or len(records) != n_frames:
        raise ValueError("source-frame cache dimensions or population differs")
    for index, row in enumerate(records):
        if (
            row.get("frame") != index
            or row.get("path") != f"frames/{index}.jpg"
            or (row.get("pts"), Fraction(row.get("time_base", "0"))) != mapping[index]
            or row.get("size") != expected_size
        ):
            raise ValueError("source-frame cache row/PTS/dimensions differ")
    selected_paths = {}
    for frame in selected:
        path = cache / records[frame]["path"]
        if path.is_symlink() or not path.is_file() or sha(path) != records[frame]["sha256"]:
            raise ValueError("selected source-frame cache image bytes changed or are symlinked")
        decoded = cv2.imread(str(path))
        if decoded is None or [decoded.shape[1], decoded.shape[0]] != expected_size:
            raise ValueError("selected source-frame cache JPEG has invalid dimensions")
        selected_paths[frame] = path
    return manifest, selected_paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "source-pts", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--frame-count", type=int, required=True)
    parser.add_argument("--fps", type=Fraction, required=True)
    a = parser.parse_args()
    result = prepare(a.source.resolve(), a.source_pts.resolve(), a.output.absolute(), a.frame_count, a.fps)
    print(json.dumps({key: result[key] for key in ("n_frames", "source_sha256", "elapsed_seconds")}))


if __name__ == "__main__":
    main()
