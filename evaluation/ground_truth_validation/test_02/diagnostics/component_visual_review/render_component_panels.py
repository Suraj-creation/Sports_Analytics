"""Render completed cache segments only; never open the running session database.

One invocation examines a stable cache prefix and reports unavailable frames.
It performs no inference, no polling and no source decoding. Exact raw source
panels and closed cache bytes are copied into this diagnostic directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import UTC, datetime
from pathlib import Path

import cv2
import msgpack

DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[4]
SOURCE_PANELS = DIRECTORY.parent / "annotation_visual_review"
DEFAULT_CACHE = ROOT / "evaluation/ground_truth_validation/test_02/baseline_v1/run/data/sessions/UPLOADTEST2/perception"
SKELETON = [
    (0, 1),
    (0, 2),
    (1, 3),
    (2, 4),
    (5, 6),
    (5, 7),
    (7, 9),
    (6, 8),
    (8, 10),
    (5, 11),
    (6, 12),
    (11, 12),
    (11, 13),
    (13, 15),
    (12, 14),
    (14, 16),
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def finite_xy(value):
    return value is not None and len(value) >= 2 and all(math.isfinite(float(v)) for v in value[:2])


def point(value):
    return tuple(round(float(v)) for v in value[:2])


def label(image, text, xy, color, scale=0.43):
    cv2.putText(image, text, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(image, text, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, color, 1, cv2.LINE_AA)


def preserve(path, data):
    """Never silently overwrite evidence from an earlier renderer invocation."""
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Existing evidence differs: {path}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(data)


def render(frame, original, output):
    image = cv2.imread(str(original))
    if image is None or image.shape != (720, 1280, 3):
        raise ValueError("Expected an exact 1280x720 source-resized panel")
    f = frame["f"]
    image = cv2.copyMakeBorder(image, 0, 245, 0, 0, cv2.BORDER_CONSTANT, value=(15, 15, 15))
    people = frame.get("p", [])
    lines = [
        f"CURRENT predictions | frame {f} / {f / 30:.6f}s | view={frame.get('v')} "
        f"calibration={frame.get('cs')} epoch={frame.get('ce')}",
        "GREEN boxes/track IDs; MAGENTA pose (all finite joints, no confidence filter); "
        "RED ellipse=racket MODEL ESTIMATE",
        "ORANGE cross=raw decoder shuttle; CYAN ring=association selected; "
        "WHITE points=legacy generated slots/filled shuttle",
        "All observations are estimates. No reviewed physical GT, contact confirmation, "
        "persistent named identity or complete-run metrics.",
    ]
    for p in people:
        b = p.get("b")
        if b is None or len(b) != 4:
            continue
        cv2.rectangle(image, point(b[:2]), point(b[2:]), (0, 255, 0), 2)
        title = f"track {p.get('t')} raw={p.get('rt')} det_match={p.get('dm')}"
        label(image, title, (round(b[0]), max(15, round(b[1]) - 10)), (0, 255, 0))
        k = p.get("k")
        if k is not None:
            for a, z in SKELETON:
                if max(a, z) < len(k) and finite_xy(k[a]) and finite_xy(k[z]):
                    cv2.line(image, point(k[a]), point(k[z]), (255, 0, 255), 1, cv2.LINE_AA)
            for j, joint in enumerate(k):
                if finite_xy(joint):
                    cv2.circle(image, point(joint), 3, (255, 0, 255), -1)
                    if j in (0, 9, 10):
                        label(image, str(j), (round(joint[0]) + 4, round(joint[1]) - 3), (255, 180, 255), 0.35)
        rk = p.get("rk")
        if rk and finite_xy(rk.get("center")):
            center = point(rk["center"])
            axes = tuple(max(1, round(float(v) / 2)) for v in rk["axes"])
            cv2.ellipse(image, center, axes, float(rk["angle"]), 0, 360, (0, 0, 255), 2)
            label(image, f"racket? t{p.get('t')}", (center[0] + 10, center[1] - 10), (0, 0, 255))
            wi = rk.get("wrist")
            if k is not None and type(wi) is int and 0 <= wi < len(k) and finite_xy(k[wi]):
                cv2.line(image, point(k[wi]), center, (0, 0, 255), 1, cv2.LINE_AA)
        lines.append(
            f"track{p.get('t')}: det_conf={p.get('c'):.3f}; pose_frame={p.get('pf')}; "
            f"racket_frame={p.get('rf')}; racket_estimate={json.dumps(rk, separators=(',', ':'))}"
        )
    assoc = frame.get("sa") or {}
    raw = assoc.get("raw_xy", frame.get("s"))
    selected = assoc.get("selected_xy")
    if finite_xy(raw):
        cv2.drawMarker(image, point(raw), (0, 165, 255), cv2.MARKER_CROSS, 19, 2)
        label(image, "raw shuttle", (round(raw[0]) + 12, round(raw[1]) + 15), (0, 165, 255))
    if finite_xy(selected):
        cv2.circle(image, point(selected), 12, (255, 255, 0), 2)
        label(image, "associated", (round(selected[0]) + 12, round(selected[1]) - 10), (255, 255, 0))
    lines.append(
        f"raw={raw}; selected={selected}; association={assoc.get('status')}/"
        f"{assoc.get('association_status')}; reasons={assoc.get('reasons')}"
    )
    return image, lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--frames", default="300,1594,16246,22924")
    args = parser.parse_args()
    requested = sorted(set(int(x) for x in args.frames.split(",")))
    metadata = json.loads((SOURCE_PANELS / "frame_metadata.json").read_text())
    source = {row["source_frame"]: row for row in metadata["frames"]}
    certificate = json.loads((SOURCE_PANELS / "diagnostic_coordinate_binding.json").read_text())
    manifest_path = DIRECTORY / "manifest.json"
    manifest = (
        json.loads(manifest_path.read_text())
        if manifest_path.exists()
        else {
            "source_sha256": certificate["source_sha256"],
            "run": str(args.cache.resolve().parents[4]),
            "scope": "Fresh baseline stable prefix only; no live DB, no inference, no full-run metrics",
            "independent_physical_accuracy": False,
            "frames": {},
        }
    )
    pending = set(requested)
    for path in sorted(args.cache.glob("seg_*.msgpack")):
        before = path.stat()
        blob = path.read_bytes()
        chunk = msgpack.unpackb(blob, raw=False)
        chosen = pending.intersection(range(chunk["start"], chunk["end"] + 1))
        if not chosen:
            continue
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or path.read_bytes() != blob:
            raise ValueError("Cache mutated during read; retry later without using it")
        frames = chunk["frames"]
        if [f["f"] for f in frames] != list(range(chunk["start"], chunk["end"] + 1)):
            raise ValueError("Cache segment does not contain its complete contiguous frame range")
        cache_sha = digest(blob)
        saved_cache = DIRECTORY / "cache_snapshots" / f"{cache_sha}_{path.name}"
        preserve(saved_cache, blob)
        byframe = {f["f"]: f for f in frames}
        for fi in sorted(chosen):
            if fi not in source:
                continue
            f = byframe[fi]
            output = DIRECTORY / f"frame_{fi:05d}"
            output.mkdir(exist_ok=True)
            raw = SOURCE_PANELS / source[fi]["raw_image"]
            original = output / "exact_source_resized.png"
            preserve(original, raw.read_bytes())
            preserve(output / "current_cache_frame.json", (json.dumps(f, indent=2) + "\n").encode())
            image, lines = render(f, original, output)
            legacy = source[fi]
            p = legacy.get("legacy_player_row") or {}
            for slot in (1, 2):
                if p.get(f"player_{slot}_x") and p.get(f"player_{slot}_y"):
                    xy = [float(p[f"player_{slot}_x"]), float(p[f"player_{slot}_y"])]
                    cv2.circle(image, point(xy), 6, (255, 255, 255), 2)
                    label(image, f"legacy slot{slot}", (round(xy[0]) + 8, round(xy[1]) + 12), (255, 255, 255))
            shuttle = legacy.get("legacy_shuttle_row") or {}
            if shuttle.get("Visibility") == "1":
                xy = [float(shuttle["X"]), float(shuttle["Y"])]
                if 0 <= xy[0] < 1280 and 0 <= xy[1] < 720:
                    cv2.drawMarker(image, point(xy), (255, 255, 255), cv2.MARKER_DIAMOND, 20, 1)
                lines.append(
                    f"legacy filled shuttle={xy}; confidence={shuttle.get('Confidence')}; "
                    f"inside_canvas={0 <= xy[0] < 1280 and 0 <= xy[1] < 720}"
                )
            else:
                lines.append("legacy shuttle Visibility=0 or unavailable")
            for i, line in enumerate(lines):
                label(image, line[:195], (8, 740 + i * 21), (230, 230, 230), 0.39)
            panel = output / "current_vs_legacy.png"
            ok, encoded = cv2.imencode(".png", image)
            if not ok:
                raise ValueError("PNG encode failed")
            preserve(panel, encoded.tobytes())
            evidence = {
                "frame": fi,
                "seconds": fi / 30,
                "cache_original": str(path.resolve()),
                "cache_snapshot": str(saved_cache),
                "cache_sha256": cache_sha,
                "cache_range": [chunk["start"], chunk["end"]],
                "source_metadata": source[fi],
                "source_panel_sha256": digest(raw.read_bytes()),
                "panel": str(panel),
                "panel_sha256": digest(panel.read_bytes()),
                "models": chunk.get("models"),
                "current_frame": f,
                "scope": "Closed segment prefix; not proof of completed run or physical GT accuracy",
            }
            preserve(output / "evidence.json", (json.dumps(evidence, indent=2) + "\n").encode())
            manifest["frames"][str(fi)] = {
                k: evidence[k] for k in ("frame", "seconds", "cache_sha256", "cache_range", "panel", "panel_sha256")
            }
            pending.remove(fi)
    manifest["requested_frames"] = requested
    manifest["pending_frames"] = sorted(pending)
    manifest["updated_utc"] = datetime.now(UTC).isoformat()
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"rendered": sorted(map(int, manifest["frames"])), "pending": sorted(pending)}))


if __name__ == "__main__":
    main()
