"""Independent read-only source/proxy/HLS alignment and boundary visual audit."""

from __future__ import annotations

import json
from pathlib import Path

import av
import cv2
import msgpack
import numpy as np

from bai_engine.decode import SegmentDecoder
from bai_engine.store.sessions import MediaPaths

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/benchmarking/investigation/audit_b"
BASE = ROOT / "outputs/benchmarking/test1"


def frame_at(container, index):
    stream = container.streams.video[0]
    target = index * 512
    container.seek(target, stream=stream, any_frame=False, backward=True)
    for frame in container.decode(stream):
        if frame.pts >= target:
            if frame.pts != target:
                raise RuntimeError(f"Missing presentation frame {index}: got PTS {frame.pts}")
            return frame.to_ndarray(format="bgr24")
    raise RuntimeError(f"Missing frame {index}")


def gray(image):
    return cv2.GaussianBlur(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), (5, 5), 0).astype(float)


def audit():
    source = ROOT / "data/benchmarking/test1/Test1_Full_rev.mp4"
    proxy = next((BASE / "runtime/media").glob("*/proxy.mp4"))
    indices = [
        0,
        7,
        8,
        59,
        60,
        119,
        120,
        243,
        887,
        891,
        1023,
        1024,
        1064,
        1066,
        8106,
        8110,
        8266,
        8308,
        9523,
        9525,
        9530,
        9543,
        9544,
        9967,
        12451,
        12748,
        12763,
        12768,
        12771,
        12966,
        17226,
        17267,
    ]
    decoder = SegmentDecoder(MediaPaths(proxy.parent), 60)
    samples = []
    with av.open(str(source)) as original, av.open(str(proxy)) as processed:
        for index in indices:
            original_frames = {
                j: cv2.resize(frame_at(original, j), (1280, 720), interpolation=cv2.INTER_AREA)
                for j in range(max(0, index - 2), min(17268, index + 3))
            }
            original_image = original_frames[index]
            original_gray = gray(original_image)
            proxy_frames = {j: frame_at(processed, j) for j in range(max(0, index - 2), min(17268, index + 3))}
            first, last = min(original_frames), max(original_frames)
            motion = np.abs(gray(original_frames[first]) - gray(original_frames[last])) > 8
            # Exclude scoreboard/logo overlays; use the actual court/player region.
            roi = np.zeros(motion.shape, bool)
            roi[110:700, 200:1120] = True
            motion &= roi
            sample = {
                "frame": index,
                "source_pts": index * 512,
                "proxy_pts": index * 512,
                "source_proxy_global_gray_mae": float(np.abs(gray(proxy_frames[index]) - original_gray).mean()),
                "motion_pixels": int(motion.sum()),
                "motion_region_offset_gray_mae": {},
                "hls_proxy_max_pixel_difference": int(
                    np.abs(decoder.decode_frame(index).astype(int) - proxy_frames[index]).max()
                ),
            }
            if motion.sum() >= 100:
                sample["motion_region_offset_gray_mae"] = {
                    str(j - index): float(np.abs(gray(image) - original_gray)[motion].mean())
                    for j, image in proxy_frames.items()
                }
                sample["best_tested_proxy_offset"] = int(
                    min(sample["motion_region_offset_gray_mae"], key=sample["motion_region_offset_gray_mae"].get)
                )
            else:
                sample["best_tested_proxy_offset"] = None
            samples.append(sample)
            print(index, "best", sample["best_tested_proxy_offset"], "motion", sample["motion_pixels"], flush=True)
    raw = {}
    for path in sorted((BASE / "runtime/sessions/BenchmarkTest1/perception").glob("*.msgpack")):
        frames = msgpack.unpackb(path.read_bytes(), raw=False)["frames"]
        raw.update({f["f"]: f for f in frames})
    groups = {
        "gt20_top_exit": [9523, 9525, 9530, 9540, 9543, 9544],
        "gt27_stationary_point": [12748, 12753, 12763, 12768, 12771, 12780],
        "gt2_gap": [891, 1023, 1030, 1040, 1064, 1066],
        "gt19_gap": [8110, 8266, 8275, 8285, 8305, 8308],
        "missed_boundaries": [2210, 2309, 11568, 11634, 13054, 13176, 13679, 13843, 14404, 14646],
    }
    with av.open(str(source)) as original:
        for name, frames in groups.items():
            tiles = []
            for index in frames:
                image = frame_at(original, index)
                obs = raw[index]
                if obs["s"] is not None:
                    x, y = (round(v * 1.5) for v in obs["s"])
                    cv2.circle(image, (x, y), 15, (0, 255, 255), 3)
                image = cv2.resize(image, (960, 540))
                cv2.rectangle(image, (0, 0), (960, 40), (0, 0, 0), -1)
                text = f"source {index} t={index / 30:.3f}s raw={obs['s']} conf={obs['c']:.3f}"
                cv2.putText(image, text, (8, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 1)
                tiles.append(image)
            rows = [np.hstack(tiles[i : i + 2]) for i in range(0, len(tiles), 2)]
            cv2.imwrite(str(OUT / f"{name}.jpg"), np.vstack(rows))
    result = {
        "method": "independent packet PTS audit plus exact-PyAV-PTS decoded samples; no timeline changes",
        "sample_count": len(samples),
        "samples": samples,
        "offset_selection_role": "diagnostic test only; never a correction to predictions/labels",
        "all_hls_samples_pixel_identical_to_mp4": all(r["hls_proxy_max_pixel_difference"] == 0 for r in samples),
    }
    (OUT / "decoded_alignment.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    audit()
