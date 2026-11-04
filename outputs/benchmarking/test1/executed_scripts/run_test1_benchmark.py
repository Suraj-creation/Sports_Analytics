"""Frozen Test 1 baseline: source audit -> production subprocess -> evaluation.

Run from the repository root after `source ../gpu-env.sh`:
  python scripts/benchmarking/run_test1_benchmark.py
Use a NEW --output directory for every repeat; existing results are never erased.
No dependency installation or threshold tuning is performed here.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.benchmarking.evaluate_rallies import POLICY, read_csv, save_evaluation  # noqa: E402
from scripts.benchmarking.production_inference import digest, dump  # noqa: E402


def command(args):
    return subprocess.check_output(args, cwd=ROOT, text=True)


def source_fingerprint():
    return {str(p.relative_to(ROOT)): digest(p)
            for root in ("engine/src", "sports/badminton/src") for p in sorted((ROOT / root).rglob("*.py"))}


def audit_source(video, output):
    entries = "stream=codec_name,width,height,r_frame_rate,avg_frame_rate,time_base,start_time,duration,nb_frames,nb_read_frames:format=duration,size"
    probe = json.loads(command(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
                                "-show_entries", entries, "-of", "json", str(video)]))
    dump(output / "source_probe.json", probe)
    stream = probe["streams"][0]
    fps = float(Fraction(stream["avg_frame_rate"]))
    packets = json.loads(command(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_packets",
                                  "-show_entries", "packet=pts_time", "-of", "json", str(video)]))
    pts = sorted(float(p["pts_time"]) for p in packets["packets"])
    count = int(stream["nb_read_frames"])
    deviation = max(abs(t - i / fps) for i, t in enumerate(pts))
    audit = {"fps": fps, "decoded_frame_count": count, "packet_count": len(pts),
             "first_pts_seconds": pts[0], "last_pts_seconds": pts[-1],
             "maximum_pts_deviation_from_zero_based_cfr_seconds": deviation,
             "verified_zero_origin_cfr": len(pts) == count and deviation <= 1e-6}
    dump(output / "source_timeline_audit.json", audit)
    if not audit["verified_zero_origin_cfr"]:
        raise ValueError("source is not a verified zero-origin CFR timeline; investigate mapping before evaluation")
    return probe, audit


def audit_annotations(annotations, output, fps, count):
    gt = read_csv(annotations, fps)
    if len(gt) != 36 or max(r.end_frame for r in gt) >= count:
        raise ValueError("Test 1 requires exactly 36 valid original-video intervals")
    with annotations.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    audit = {"rally_count": len(gt), "frame_base": 0, "fps": fps,
             "max_frame_time_residual_seconds": max(abs(float(r[k]) - int(r[f]) / fps)
                  for r in rows for k, f in (("Start_Time_sec", "Start_Frame"), ("End_Time_sec", "End_Frame"))),
             "max_duration_residual_seconds": max(abs(float(r["Duration_sec"]) -
                       (float(r["End_Time_sec"]) - float(r["Start_Time_sec"]))) for r in rows),
             "human_timestamps": "MM:SS, floor to whole seconds",
             "span": "end boundary timestamp minus start boundary timestamp; no inclusive-frame addition",
             "evidence": "Every supplied timestamp equals frame/actual FPS; related Part2 shuttle table enumerates 0..17267, matching source decode count.",
             "ambiguity": "Original annotation tool/reviewer history is unavailable. Arithmetic supports zero-based indexing but cannot independently exclude a one-frame human annotation offset; no offset is fitted or corrected.",
             "provenance_limit": "User identifies these 36 rows as manual annotations. Related *_T.csv is not ground truth; legacy exporter uses the same schema. Independent manual-review provenance is not in the repository."}
    dump(output / "annotation_audit.json", audit)
    return gt, audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, default=ROOT / "data/benchmarking/test1/Test1_Full_rev.mp4")
    parser.add_argument("--annotations", type=Path, default=ROOT / "Part2/dataset/Test1_Full/Test1_Full_rally.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/benchmarking/test1")
    parser.add_argument("--profile", default="gpu-rtx4000")
    args = parser.parse_args()
    branch = command(["git", "branch", "--show-current"]).strip()
    if branch != "Benchmarking":
        raise RuntimeError("benchmark writes require branch Benchmarking")
    output, video, annotations = args.output.resolve(), args.video.resolve(), args.annotations.resolve()
    output.mkdir(parents=True, exist_ok=True)
    # Allow existing download/probe evidence, but never overwrite any run.
    if (output / "benchmark_metadata.json").exists() or (output / "runtime").exists():
        raise FileExistsError("use a new --output to preserve the existing baseline")
    sha = command(["git", "rev-parse", "HEAD"]).strip()
    fingerprint = source_fingerprint()
    metadata = {
        "status": "preflight", "benchmark_execution_date": datetime.now(UTC).isoformat(),
        "source_video_filename": video.name, "source_video_sha256": digest(video),
        "source_drive_folder": "https://drive.google.com/drive/folders/1_2QWSYd_X_BojdRwbu-AMKdx74cIQvGp",
        "source_drive_subfolder_id": "1XxAJXTE0cfKZRDSVPfKp9cB0QPcq9fsr",
        "source_drive_file_id": "1vR71QTkUYEGWy4PjXa5vfMdJEXt_OwLn",
        "ground_truth_path": str(annotations.relative_to(ROOT)) if annotations.is_relative_to(ROOT) else str(annotations),
        "ground_truth_sha256": digest(annotations), "ground_truth_rally_count": 36,
        "git_commit_sha": sha, "active_branch": branch, "main_base_sha": command(["git", "rev-parse", "main"]).strip(),
        "working_tree_status": command(["git", "status", "--short"]),
        "production_source_hashes": fingerprint,
        "benchmark_script_hashes": {p.name: digest(p) for p in Path(__file__).parent.glob("*.py")},
        "pipeline_entry_point": "bai_engine.runtime.runner.SessionRunner._ensure_media + _analyse",
        "pipeline_mode": "VOD upload / badminton plugin / rally-fsm-v1; all current finalized rally_end events",
        "matching_policy": POLICY, "python": sys.version, "platform": platform.platform(),
        "frame_conventions": "zero-based original and CFR proxy indices; preserve inclusive end observation index, measure boundary span as (end-start)/fps",
        "leakage_control": "Worker subprocess receives video, frozen profile, output directory only; no annotations, count target, or Part2 predictions.",
    }
    dump(output / "benchmark_metadata.json", metadata)
    try:
        probe, timeline = audit_source(video, output)
        stream = probe["streams"][0]
        fps = timeline["fps"]
        gt, annotation_audit = audit_annotations(annotations, output, fps, timeline["decoded_frame_count"])
        metadata.update(video_fps=fps, frame_count=timeline["decoded_frame_count"],
                        duration_seconds=float(stream["duration"]), resolution=[stream["width"], stream["height"]],
                        annotation_audit=annotation_audit, source_timeline_audit=timeline)
        profiles = output / "profiles"
        profiles.mkdir()
        profile_path = ROOT / "config/profiles" / f"{args.profile}.yaml"
        shutil.copy2(profile_path, profiles / profile_path.name)
        metadata["pipeline_configuration"] = {"profile": args.profile, "profile_sha256": digest(profile_path),
                                               "profile_yaml": profile_path.read_text(), "proxy_height": 720}
        metadata["status"] = "running"
        dump(output / "benchmark_metadata.json", metadata)
        worker = [sys.executable, str(Path(__file__).with_name("production_inference.py")),
                  "--video", str(video), "--output", str(output), "--profile", args.profile]
        with (output / "execution.log").open("x") as log:
            log.write("Command: " + json.dumps(worker) + "\n")
            log.flush()
            subprocess.run(worker, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        if source_fingerprint() != fingerprint or digest(annotations) != metadata["ground_truth_sha256"]:
            raise RuntimeError("source/annotations changed during inference; refusing baseline evaluation")
        inference = json.loads((output / "inference.json").read_text())
        if float(Fraction(inference["media"]["fps_num"], inference["media"]["fps_den"])) != fps:
            raise RuntimeError("proxy rate differs from source; explicit mapping required")
        if inference["media"]["n_frames"] != timeline["decoded_frame_count"]:
            raise RuntimeError("proxy/source frame count mismatch; investigate alignment before evaluating")
        pred = read_csv(output / "predicted_rallies.csv", fps)
        metrics = save_evaluation(output, gt, pred, fps)
        metadata.update(status="completed", pipeline=inference["pipeline"], models=inference["model_registry_after"],
                        execution_backends=inference["execution_backends"], degraded=inference["degraded"],
                        elapsed_seconds=inference["elapsed_seconds"], proxy_sha256=inference["proxy_sha256"],
                        prediction_sha256=digest(output / "predicted_rallies.csv"),
                        completed_at=datetime.now(UTC).isoformat())
        print(json.dumps(metrics["detection"], indent=2))
    except Exception as exc:
        metadata.update(status="blocked_or_failed", error=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        dump(output / "benchmark_metadata.json", metadata)


if __name__ == "__main__":
    main()
