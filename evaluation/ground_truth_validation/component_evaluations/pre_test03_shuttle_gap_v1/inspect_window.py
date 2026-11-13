"""CPU-only source/cache inspection; no pipeline/model imports or inference."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import av
import cv2
import msgpack
import numpy as np

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent.parent
RUN_ROOT = Path(
    "/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/improved_v1"
)
RUN = RUN_ROOT / "run"
SOURCE_SHA = "4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a"
PROXY_SHA = "2841ee54fb0b6d28c2a57e89293ba4530173980635c21aa8d08f60f52931b6cd"
START, END = 27312, 27375
SELECTED = [27312, 27320, 27324, 27325, 27326, 27335, 27347, 27348, 27353, 27354, 27355, 27360, 27375]


def sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    with Path(path).open("x") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")


def save(path, image):
    assert not path.exists()
    assert cv2.imwrite(str(path), image)


def main():
    out = ROOT / "attempt_v1"
    out.mkdir(exist_ok=False)
    (out / "source").mkdir()
    (out / "overlays").mkdir()
    cv2.setNumThreads(1)
    inputs = {}

    def bind(path):
        path = Path(path).resolve()
        inputs[str(path)] = sha(path)
        return path

    bind(__file__)
    worker = read(bind(RUN / "inference.json"))
    parent = read(bind(RUN_ROOT / "run.executor.json"))
    catalogue = read(bind(RUN / "perception_completion_catalog.json"))
    plan = read(bind(RUN_ROOT / "protocol/plan.json"))
    completion = read(bind(RUN_ROOT / "improved_completion.json"))
    assert plan["cases"]["test2"]["source_sha256"] == SOURCE_SHA
    assert worker["status"] == parent["status"] == "completed"
    assert parent["worker_exit_code"] == 0 and parent["frozen_source_inputs_unchanged"] is True
    assert sha(RUN / "inference.json") == parent["worker_report_sha256"]
    assert sha(RUN_ROOT / "protocol/plan.json") == parent["plan_sha256"]
    assert worker["frames_processed"] == 29296 and worker["cached_perception_used"] is False
    assert completion["status"] == "completed_fresh_Test2_improved_and_diagnostics"
    assert completion["own_run_semantic_parity"] is True
    assert worker["source_sha256"] == catalogue["source_sha256"] == SOURCE_SHA
    assert worker["proxy_sha256"] == catalogue["proxy_sha256"] == PROXY_SHA
    replay_manifest = read(bind(RUN_ROOT / "diagnostic_replay/replay_manifest.json"))
    parity = read(bind(RUN_ROOT / "diagnostic_replay/parity_vs_fresh.json"))
    assert parity["differences"] == []
    assert replay_manifest["source_report_sha256"] == sha(RUN / "inference.json")
    proxy = bind(RUN / f"data/media/{SOURCE_SHA}/proxy.mp4")
    assert inputs[str(proxy)] == PROXY_SHA
    tracknet = worker["models"]["artifacts"]["tracknetv3"]
    checkpoint = bind(tracknet["staged_path"])
    assert inputs[str(checkpoint)] == tracknet["expected_sha256"] == tracknet["sha256"]
    assert worker["profile"]["components"]["rally"]["params"]["use_reconstruction"] is False

    cache_frames, consumed = {}, []
    for entry in catalogue["files"]:
        if entry["start"] <= END and entry["end"] >= START:
            path = bind(RUN / entry["path"])
            assert inputs[str(path)] == entry["sha256"]
            payload = msgpack.unpackb(path.read_bytes(), raw=False, strict_map_key=False)
            assert payload["start"] == entry["start"] and payload["end"] == entry["end"]
            assert [r["f"] for r in payload["frames"]] == list(range(entry["start"], entry["end"] + 1))
            for row in payload["frames"]:
                if START <= row["f"] <= END:
                    assert row["f"] not in cache_frames
                    cache_frames[row["f"]] = row
            consumed.append({**entry, "absolute_path": str(path), "ci": payload["ci"], "models": payload["models"]})
    assert sorted(cache_frames) == list(range(START, END + 1))
    historical = read(
        bind(BASE / "test_02/diagnostics/current_scene_and_ocr_review/g69_gap_extended/prefix_snapshot.json")
    )
    old_binding = read(bind(BASE / "test_02/diagnostics/current_scene_and_ocr_review/completed_snapshot_binding.json"))
    assert old_binding["strict_completed_guard"] is True
    old_rows = {r["f"]: r for r in historical["frames"]}
    for frame, row in cache_frames.items():
        assert row["s"] == old_rows[frame]["s"]
        assert row["sa"] == old_rows[frame]["sa"]

    trace_path = bind(RUN_ROOT / "diagnostic_replay/bounded_fsm_trace.jsonl")
    trace = []
    with trace_path.open() as stream:
        for line in stream:
            row = json.loads(line)
            if START <= row["frame"] <= END:
                trace.append(row)
    assert len({r["frame"] for r in trace if r["call"] == "step"}) == END - START + 1
    write(out / "fsm_window.json", trace)
    write(out / "cache_window.json", [cache_frames[f] for f in sorted(cache_frames)])
    write(out / "consumed_cache_headers.json", consumed)
    # Exact recorded source is read from the completed own-parity replay snapshot.
    source_dir = RUN_ROOT / "diagnostic_replay" / replay_manifest["core_source_snapshot"]["directory"]
    source_refs = {}
    for relative in [
        "sports/badminton/src/bai_badminton/perception/tracknet.py",
        "sports/badminton/src/bai_badminton/perception/isolation.py",
        "sports/badminton/src/bai_badminton/perception/association.py",
        "sports/badminton/src/bai_badminton/perception/pipeline.py",
        "sports/badminton/src/bai_badminton/events/rally_fsm.py",
        "sports/badminton/src/bai_badminton/events/rally_evidence.py",
    ]:
        path = bind(source_dir / relative)
        assert inputs[str(path)] == replay_manifest["core_source_snapshot"]["sha256"][relative]
        source_refs[relative] = {"path": str(path), "sha256": inputs[str(path)]}

    receipts, compact = [], []
    top_tiles, body_tiles, overall_tiles = [], [], []
    preroll = []
    with av.open(str(proxy)) as container:
        stream = container.streams.video[0]
        stream.codec_context.thread_count = 1
        assert stream.average_rate == 30
        assert (stream.width, stream.height) == (1280, 720)
        seek = Fraction(START, 30) / stream.time_base
        assert seek.denominator == 1
        container.seek(seek.numerator, stream=stream, backward=True, any_frame=False)
        for decoded in container.decode(stream):
            number = Fraction(decoded.pts) * decoded.time_base * 30
            assert number.denominator == 1
            frame = number.numerator
            if frame < START:
                preroll.append(frame)
                continue
            if frame > END:
                break
            image = decoded.to_ndarray(format="bgr24")
            row = cache_frames[frame]
            source_path = out / "source" / f"frame_{frame:05}.png"
            save(source_path, image)
            decoded_again = cv2.imread(str(source_path))
            assert np.array_equal(image, decoded_again)
            receipt = {
                "frame": frame,
                "pts": decoded.pts,
                "time_base": str(decoded.time_base),
                "canonical_seconds": str(Fraction(frame, 30)),
                "bgr_sha256": hashlib.sha256(image.tobytes()).hexdigest(),
                "source_png": str(source_path.relative_to(out)),
                "source_png_sha256": sha(source_path),
            }
            receipts.append(receipt)
            raw = row["sa"]
            compact.append(
                {
                    "frame": frame,
                    "raw_xy": row["s"],
                    "support": row["c"],
                    "status": raw["status"],
                    "association_status": raw["association_status"],
                    "association_reasons": raw["reasons"],
                    "candidates": raw["candidates"],
                    "view": row["v"],
                    "calibration_state": row["cs"],
                    "content_epoch": row["ce"],
                    "raw_scene": row["cc"],
                    "layout_scene": row["cd"],
                    "person_count": len(row["p"]),
                    "person_freshness": [
                        {"episode": p["t"], "detector_matched": p["dm"], "pose_frame": p["pf"]} for p in row["p"]
                    ],
                    "detailed_shuttle": None if row["dg"] is None else row["dg"].get("shuttle"),
                }
            )
            # Fixed crops expose source pixels before candidate overlays, avoiding
            # diagnostic-coordinate confirmation bias.
            top = image[0:180, 700:920].copy()
            body = image[340:560, 690:910].copy()
            for tile in [top, body]:
                cv2.rectangle(tile, (0, 0), (85, 19), (0, 0, 0), -1)
                cv2.putText(tile, str(frame), (3, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            top_tiles.append(cv2.resize(top, (220, 220)))
            body_tiles.append(body)
            if (frame - START) % 4 == 0:
                tile = cv2.resize(image, (640, 360))
                cv2.putText(tile, str(frame), (5, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
                overall_tiles.append(tile)
            if frame in SELECTED:
                overlay = image.copy()
                for person in row["p"]:
                    x0, y0, x1, y1 = map(round, person["b"])
                    cv2.rectangle(overlay, (x0, y0), (x1, y1), (255, 180, 0), 1)
                    for idx in [0, 9, 10]:
                        joint = person["k"][idx]
                        if joint[2] > 0:
                            cv2.circle(overlay, (round(joint[0]), round(joint[1])), 3, (255, 180, 0), 1)
                for candidate in raw["candidates"]:
                    point = tuple(map(round, candidate["peak_xy"]))
                    color = (0, 255, 0) if candidate["selected_peak"] else (0, 140, 255)
                    cv2.circle(overlay, point, 8, color, 1)
                    cv2.putText(
                        overlay,
                        f"r{candidate['rank']}:{candidate['peak_support']:.3f}",
                        (point[0] + 9, max(14, point[1] - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        color,
                        1,
                    )
                cv2.putText(
                    overlay,
                    f"{frame} raw={raw['status']} candidates=diagnostic, not GT",
                    (10, 700),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    1,
                )
                save(out / "overlays" / f"frame_{frame:05}.png", overlay)
            if frame == END:
                break
    assert [r["frame"] for r in receipts] == list(range(START, END + 1))
    assert len(receipts) == 64
    for name, tiles, columns in [
        ("top_source_montage.png", top_tiles, 8),
        ("body_source_montage.png", body_tiles, 8),
        ("overall_source_montage.png", overall_tiles, 4),
    ]:
        assert len(tiles) % columns == 0
        montage = np.vstack([np.hstack(tiles[i : i + columns]) for i in range(0, len(tiles), columns)])
        save(out / name, montage)
    write(out / "source_receipts.json", receipts)
    write(out / "frame_readout.json", compact)
    write(
        out / "input_binding.json",
        {
            "scope": (
                "64 retained/reviewable exact proxy frames; codec preroll separately counted, no NN or active database"
            ),
            "source_sha256": SOURCE_SHA,
            "proxy_sha256": PROXY_SHA,
            "window": [START, END],
            "retained_frames": len(receipts),
            "codec_preroll_frames": preroll,
            "recorded_source_commit": replay_manifest["recorded_source_commit"],
            "source_refs": source_refs,
            "inputs_sha256": inputs,
            "raw_and_association_match_old_completed_bound_snapshot": True,
            "original_raw_Test2_video_present": False,
            "new_NN": False,
            "physical_ground_truth": None,
        },
    )
    for path, digest in inputs.items():
        assert sha(path) == digest, path
    write(
        out / "extraction_completion.json",
        {
            "status": "completed_read_only_source_cache_extraction",
            "retained_source_frames": 64,
            "codec_preroll_count": len(preroll),
            "new_NN": False,
            "all_input_hashes_unchanged": True,
            "artifact_sha256": {str(p.relative_to(out)): sha(p) for p in out.rglob("*") if p.is_file()},
        },
    )
    print(json.dumps({"status": "completed", "frames": 64, "preroll": len(preroll), "inputs": len(inputs)}))


if __name__ == "__main__":
    main()
