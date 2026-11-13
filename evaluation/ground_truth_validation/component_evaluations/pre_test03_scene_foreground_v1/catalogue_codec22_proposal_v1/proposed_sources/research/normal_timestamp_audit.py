"""Read-only full canonical-input/proxy PTS and probe-pixel audit; no inference/GT."""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from research.pipeline_repair_completion import decode_source_pts, validate_completed_cache, verify_proxy  # noqa: E402
from research.production_external_semantic_replay import load_finished_input, sha  # noqa: E402


def audit(run, output):
    session = json.loads((run / "session.json").read_text())
    bound = load_finished_input(run, session["session_id"])
    if bound.layout != "production-full-upload" or output.exists() or run in output.parents:
        raise ValueError("new external audit output and original successful upload required")
    info = json.loads(bound.report_path.read_text())
    plan = json.loads(bound.manifest_path.read_text())
    parent = json.loads(run.with_suffix(".executor.json").read_text())
    item = plan["cases"][parent["case"]]
    source = Path(item["source"])
    proxy = run / "data/media" / info["source_sha256"] / "proxy.mp4"
    inputs = {str(p): sha(p) for p in {*bound.input_paths, source, proxy, Path(__file__)}}
    decisions = {}
    for name, expected in bound.expected_caches.items():
        path = bound.cache_directory / name
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError("actual completed cache changed")
        _, decoded = validate_completed_cache(data, bound.profile, bound.media)
        inputs[str(path)] = expected
        for frame in decoded.frames:
            decision = frame.content_decision
            if decision is not None and decision.detector_frame is not None:
                decisions[decision.detector_frame] = (
                    decision.detector_image_sha256, decision.detector_image_shape)
    times, rows = decode_source_pts(source, bound.media)
    result = verify_proxy(proxy, bound.media, decisions, times)
    if any(sha(Path(p)) != expected for p, expected in inputs.items()):
        raise ValueError("input changed during read-only audit")
    output.mkdir(exist_ok=False)
    with (output / "source_frame_pts.csv").open("x", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["source_frame", "pts", "time_base_num", "time_base_den", "source_time_sec"])
        writer.writerows([*row, repr(float(time))] for row, time in zip(rows, times, strict=True))
    result.update(
        original_input=str(source), source_sha256=info["source_sha256"],
        proxy_sha256=info["proxy_sha256"], input_sha256=inputs,
        scope="Full input supplied to THIS run, not older long-match clip derivation or native VFR mapping",
        source_pts_csv_sha256=sha(output / "source_frame_pts.csv"), no_neural_or_gt_access=True)
    (output / "timestamp_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["frames_decoded", "exact_pts_frames", "scene_image_hashes_verified"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit(args.run.resolve(strict=True), args.output.resolve())
