"""Exact-PTS source/proxy review of completed Test2 player-point disagreements.

No inference, live database, label repair, threshold tuning or production edit.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import av
import cv2
import msgpack

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BASE = ROOT / "evaluation/ground_truth_validation/test_02/baseline_v1"
RUN = BASE / "run"
SELECTED = {300, 355, 6492, 6493, 6494, 25521}
SOURCE_SHA = "4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, data):
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Existing evidence differs: " + str(path))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(data)


def dump(path, value):
    save(path, (json.dumps(value, indent=2) + "\n").encode())


def png(path, image):
    ok, data = cv2.imencode(".png", image)
    if not ok:
        raise ValueError("PNG encoding failed")
    save(path, data.tobytes())


def exact_frame(path, index):
    wanted = Fraction(index, 30)
    with av.open(str(path)) as container:
        stream = container.streams.video[0]
        stream.codec_context.thread_count = 2
        offset = wanted / stream.time_base
        if offset.denominator != 1:
            raise ValueError("Requested canonical frame has no exact source PTS")
        container.seek(int(offset), stream=stream, backward=True, any_frame=False)
        for frame in container.decode(stream):
            timestamp = frame.pts * frame.time_base
            if timestamp < wanted:
                continue
            if timestamp != wanted:
                raise ValueError("Seek did not decode the exact requested PTS")
            image = frame.to_ndarray(format="bgr24")
            return image, {
                "frame": index,
                "pts": frame.pts,
                "time_base_num": frame.time_base.numerator,
                "time_base_den": frame.time_base.denominator,
                "seconds": float(timestamp),
                "shape": list(image.shape),
                "pixels_sha256": hashlib.sha256(image.tobytes()).hexdigest(),
            }
    raise ValueError("Exact frame missing")


def label(image, text, xy, color):
    cv2.putText(image, text, xy, cv2.FONT_HERSHEY_SIMPLEX, 0.43, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(image, text, xy, cv2.FONT_HERSHEY_SIMPLEX, 0.43, color, 1, cv2.LINE_AA)


def point(xy):
    return tuple(round(v) for v in xy)


def overlay(image, row, title):
    result = cv2.copyMakeBorder(image, 0, 110, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    legacy = {p["slot"]: p for p in row["reference_players"]}
    current = {p["index"]: p for p in row["current_players"]}
    for p in current.values():
        color = (0, 255, 0) if p["detector_matched"] else (0, 165, 255)
        b = p["bbox"]
        cv2.rectangle(result, point(b[:2]), point(b[2:]), color, 2)
        cv2.circle(result, point(p["xy"]), 6, color, 2)
        label(
            result,
            f"CURRENT idx{p['index']} track{p['track_id']} fresh={p['detector_matched']}",
            (round(b[0]), max(15, round(b[1]) - 8)),
            color,
        )
    for p in legacy.values():
        cv2.drawMarker(result, point(p["xy"]), (255, 0, 255), cv2.MARKER_DIAMOND, 17, 2)
        label(result, f"LEGACY slot{p['slot']}", (round(p["xy"][0]) + 7, round(p["xy"][1]) + 15), (255, 0, 255))
    for pair in row.get("all_current_rows_assignments", []):
        a = legacy[pair["reference_slot"]]["xy"]
        b = current[pair["current_index"]]["xy"]
        cv2.line(result, point(a), point(b), (0, 0, 255), 1, cv2.LINE_AA)
    lines = [
        f"{title}: frame{row['frame']} / {row['time_s']:.6f}s; current view={row['current_view']}, "
        f"calibration={row['current_calibration_state']}",
        "Green=current detector-matched box; orange=propagated box; "
        "magenta=LEGACY GENERATED point; red=forced anonymous match",
        "Distances are prediction disagreement, NOT reviewed AP/IoU/identity/localization accuracy.",
        "Matches: " + str(row.get("all_current_rows_assignments")),
    ]
    for i, line in enumerate(lines):
        label(result, line[:190], (8, 741 + 23 * i), (255, 255, 255))
    return result


def main():
    info = json.loads((RUN / "inference.json").read_text())
    if (
        info["status"] != "completed"
        or info["cached_perception_used"] is not False
        or info["source_sha256"] != SOURCE_SHA
        or info["frames_processed"] != 29296
        or info["frontier_frame"] != 29295
    ):
        raise ValueError("Exact completed fresh Test2 required")
    catalogue_path = RUN / info["perception_cache_catalog"]["path"]
    if sha(catalogue_path) != info["perception_cache_catalog"]["sha256"]:
        raise ValueError("Original completion cache catalogue changed")
    catalogue = json.loads(catalogue_path.read_text())
    session = json.loads((RUN / "session.json").read_text())
    source = Path(session["source"]["uri"])
    proxy = RUN / "data/media" / SOURCE_SHA / "proxy.mp4"
    if sha(source) != SOURCE_SHA or sha(proxy) != info["proxy_sha256"]:
        raise ValueError("Original source/proxy bytes changed")
    candidates = BASE / "bound_reference_diagnostics/frame_point_candidates.jsonl"
    ranked, selected = [], {}
    for line in candidates.open():
        row = json.loads(line)
        pairs = row.get("all_current_rows_assignments", [])
        if pairs:
            maximum = max(p["distance_px"] for p in pairs)
            ranked.append(
                {
                    "frame": row["frame"],
                    "seconds": row["time_s"],
                    "max_assignment_disagreement_px": maximum,
                    "fresh_current_rows": sum(p["detector_matched"] is True for p in row["current_players"]),
                    "reference_population": len(row["reference_players"]),
                    "current_population": len(row["current_players"]),
                }
            )
        if row["frame"] in SELECTED:
            selected[row["frame"]] = row
    ranked.sort(key=lambda row: (-row["max_assignment_disagreement_px"], row["frame"]))
    dump(
        HERE / "ranked_outliers.json",
        {
            "candidate_file_sha256": sha(candidates),
            "ranking": "Maximum supplied all-current anonymous assignment distance per distinct frame; no new cutoff",
            "top_30_distinct_frames": ranked[:30],
            "selected_frames": sorted(SELECTED),
            "selection": "Absolute top3 frames6492-6494; ordinary control300; distinct episodes355 and25521",
            "independent_physical_accuracy": False,
        },
    )
    evidence = []
    for frame in sorted(SELECTED):
        row = selected[frame]
        item = next(item for item in catalogue["files"] if item["start"] <= frame <= item["end"])
        cache = RUN / item["path"]
        blob = cache.read_bytes()
        if hashlib.sha256(blob).hexdigest() != item["sha256"]:
            raise ValueError("Selected closed cache bytes changed")
        copy = HERE / "cache_snapshots" / f"{item['sha256']}_{cache.name}"
        save(copy, blob)
        chunk = msgpack.unpackb(blob, raw=False)
        current = next(f for f in chunk["frames"] if f["f"] == frame)
        out = HERE / f"frame_{frame:05d}"
        dump(out / "comparison_row.json", row)
        dump(out / "current_cache_frame.json", current)
        original, source_meta = exact_frame(source, frame)
        canonical, proxy_meta = exact_frame(proxy, frame)
        if original.shape != (1080, 1920, 3) or canonical.shape != (720, 1280, 3):
            raise ValueError("Source/proxy shape differs from established coordinate binding")
        resized = cv2.resize(original, (1280, 720), interpolation=cv2.INTER_AREA)
        png(out / "source_resized.png", resized)
        png(out / "proxy.png", canonical)
        png(out / "source_overlay.png", overlay(resized, row, "Exact source resized"))
        png(out / "proxy_overlay.png", overlay(canonical, row, "Exact current analysis proxy"))
        entry = {
            "frame": frame,
            "seconds": frame / 30,
            "source_decode": source_meta,
            "proxy_decode": proxy_meta,
            "source_sha256": SOURCE_SHA,
            "proxy_sha256": info["proxy_sha256"],
            "cache_original": str(cache.resolve()),
            "cache_snapshot": str(copy),
            "cache_sha256": item["sha256"],
            "cache_range": [item["start"], item["end"]],
            "models": chunk["models"],
            "comparison_row_file": str(out / "comparison_row.json"),
            "evidence_files_sha256": {p.name: sha(p) for p in out.iterdir() if p.is_file()},
            "scope": "Source-bound prediction comparison only; no new labels/inference or physical accuracy claims",
        }
        dump(out / "evidence.json", entry)
        evidence.append(entry)
    dump(
        HERE / "extraction_manifest.json",
        {
            "source_sha256": SOURCE_SHA,
            "proxy_sha256": info["proxy_sha256"],
            "completed_inference_sha256": sha(RUN / "inference.json"),
            "candidate_file_sha256": sha(candidates),
            "cache_catalogue_sha256": sha(catalogue_path),
            "helper_sha256": sha(Path(__file__)),
            "frames": evidence,
            "new_neural_inference": False,
            "annotations_modified": False,
        },
    )
    print(json.dumps({"selected_frames": sorted(SELECTED), "largest": ranked[0]}))


if __name__ == "__main__":
    main()
