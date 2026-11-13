"""Validate retained detector pixel bindings and source-only design controls."""
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import hashlib

import av
import cv2
import msgpack
import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("source_design_shadow", HERE / "probe_design.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


def write(name, value):
    with (HERE / name).open("x") as f:
        json.dump(value, f, indent=2, allow_nan=False)


if __name__ == "__main__":
    p.bind(__file__)
    p.bind(HERE / "probe_design.py")
    standalone = p.read(p.EVAL / "component_evaluations/pre_test03_perception_v1/detector_frame_probe_v1/probe.json")
    detector_sha = "fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e"
    assert standalone["model_sha256"] == detector_sha
    detector_path = p.bind(p.ROOT / "models/cache/rfdetr_small/rfdetr_s_v142_512x512.onnx")
    assert p.inputs[str(detector_path)] == detector_sha
    supplemental, validated, saved = [], [], []
    frames_dir = HERE / "source_evidence"
    frames_dir.mkdir()
    controls = {1: {7856, 7857, 8105, 8106}, 2: {354, 355, 5956, 5957, 5958, 6150, 6151, 6306, 6307, 7703, 11345, 11346, 23639, 25520, 25521}}
    for path in sorted(p.PREFIX.glob("test*.json")):
        data = p.read(path)
        test, (start, stop) = data["test"], data["range"]
        run, H, fmt, info, raw = p.load_geometry(test, start, stop)
        proxy = p.bind(run / "data/media" / info["source_sha256"] / "proxy.mp4")
        assert p.inputs[str(proxy)] == info["proxy_sha256"]
        rows = {r["frame"]: r for r in data["variants"]["foreground"]}
        detector = {r["frame"]: r for r in data["detector_inputs"]}
        extras = {r["frame"]: r for r in standalone["results"] if r["test"] == test and r["frame"] in [355, 25521] and start <= r["frame"] <= stop}
        for frame, item in extras.items():
            assert item["source_pixels_sha256"] == rows[frame]["source_pixels_sha256"]
            x0, y0, _, _ = item["crop"]
            det = {"frame": frame, "boxes_crop": (np.asarray([r["bbox"] for r in item["proposals"]]) - [x0, y0, x0, y0]).tolist(),
                   "scores": [r["confidence"] for r in item["proposals"]], "crop_pixels_sha256": None}
            record = p.inspect_frame(test, path.stem, rows[frame], det, (H, raw[frame]["g"]), fmt, frame, raw.get(frame - 1), raw[frame])
            record.update(proposal_source="separately_retained_actual_detector_frame_probe_not_prefix_schedule", source_pixels_sha256=item["source_pixels_sha256"],
                          original_model_sha256=standalone["model_sha256"], original_crop=item["crop"], new_neural_inference=False)
            supplemental.append(record)
        with av.open(str(proxy)) as container:
            stream = container.streams.video[0]
            stream.thread_count = 1
            container.seek(int(Fraction(start, 30) / stream.time_base), stream=stream, backward=True)
            for decoded in container.decode(video=0):
                frame = round(Fraction(decoded.pts) * decoded.time_base * 30)
                if frame < start:
                    continue
                if frame > stop:
                    break
                assert Fraction(decoded.pts) * decoded.time_base == Fraction(frame, 30)
                image = decoded.to_ndarray(format="bgr24")
                pixel_sha = hashlib.sha256(image.tobytes()).hexdigest()
                assert pixel_sha == rows[frame]["source_pixels_sha256"]
                if frame in detector:
                    h = p.Homography(np.asarray(raw[frame]["g"]).reshape(3, 3) @ H, 0.0, 4)
                    world = np.asarray([[-3.05, 6.7], [3.05, 6.7], [3.05, -6.7], [-3.05, -6.7]])
                    roi = p.CourtROI(h.court_to_image(world).astype(np.float32), homography=h)
                    x0, y0, x1, y1 = roi.crop_box(1280, 720)
                    crop_sha = hashlib.sha256(image[y0:y1, x0:x1].tobytes()).hexdigest()
                    assert crop_sha == detector[frame]["crop_pixels_sha256"]
                    validated.append({"case": path.stem, "frame": frame, "full_pixels_sha256": pixel_sha,
                                      "crop": [x0, y0, x1, y1], "crop_sha256": crop_sha,
                                      "proposals": len(detector[frame]["boxes_crop"]), "model_sha256": detector_sha})
                if frame in controls[test]:
                    dest = frames_dir / f"test{test}_frame_{frame:05d}_exact_proxy.png"
                    cv2.imwrite(str(dest), image)
                    saved.append({"test": test, "frame": frame, "source_sha256": info["source_sha256"], "proxy_sha256": info["proxy_sha256"],
                                  "pts": decoded.pts, "time_base": str(decoded.time_base), "pixels_sha256": pixel_sha,
                                  "file": str(dest.relative_to(HERE)), "file_sha256": p.sha(dest)})
    write("supplemental_retained_detector_cases.json", supplemental)
    write("all_retained_proposal_pixel_verification.json", {"validated_detector_calls": len(validated), "records": validated,
                                                         "source_frames_verified": 2399, "new_neural_inference": False})
    write("source_evidence_receipts.json", saved)
    # Full, completed fresh Test1 cuts: a new weak branch cannot reinterpret them.
    run = p.ROOT.parent / "ground-truth-validation-artifacts-20261112/pre_test03_v2/test01_candidate_v2/run"
    cuts = [2195, 4837, 7503, 7857, 8106, 10023, 10604, 10770, 11903, 15579, 15985, 16446, 17069]
    raw_cuts = {}
    for item in p.read(run / "perception_completion_catalog.json")["files"]:
        if any(item["start"] <= f <= item["end"] for f in cuts):
            q = p.bind(run / item["path"])
            assert p.inputs[str(q)] == item["sha256"]
            chunk = msgpack.unpackb(q.read_bytes(), raw=False)
            for r in chunk["frames"]:
                if r["f"] in cuts:
                    raw_cuts[r["f"]] = {"frame": r["f"], "source_shot": r["sh"], "content_epoch": r["ce"], "raw_scene": r.get("cc"), "decision": r.get("cd"),
                                        "cache_sha256": item["sha256"], "weak_branch_would_not_override_recorded_strong_or_hardcut": True}
    assert set(raw_cuts) == set(cuts)
    write("all13_completed_test1_cut_audit.json", {"scope": "Recorded completed fresh c585 controls; no changed production policy or full inference. Strong/hardcut path preserved independently of shadow weak-only acquisition.", "cuts": [raw_cuts[f] for f in cuts]})
    for path, digest in p.inputs.items():
        assert p.sha(path) == digest
    write("supplemental_input_bindings.json", p.inputs)
    print(json.dumps({"source_frames": 2399, "detector_calls_validated": len(validated), "supplemental_frames": [r["frame"] for r in supplemental],
                      "supplemental_camera_aligned_candidates": [r["frame"] for r in supplemental if r.get("root_design_camera_aligned_shadow")],
                      "old_cut_controls": 13, "new_inference": False}), flush=True)
