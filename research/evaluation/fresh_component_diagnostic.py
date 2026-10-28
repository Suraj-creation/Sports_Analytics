"""Bounded fresh-inference diagnostic, not a match analysis or accuracy benchmark.

Read-only inputs; JSON on stdout. Set CUDA_VISIBLE_DEVICES before launch. Does not
fetch models, write sessions, infer a match or assert track identities.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import cv2
import numpy as np
import torch

from bai_badminton.events.contact import ATTRIBUTION_POLICY, detect_contacts
from bai_badminton.events.stroke import RuleStrokeClassifier, StrokeContext
from bai_badminton.observations import PlayerSeries, WindowObs
from bai_badminton.perception.players import PlayerDetector, PlayerPerception, PoseEstimator
from bai_badminton.perception.shuttle_post import Track, process
from bai_badminton.perception.tracknet import TrackNetV3
from bai_engine.runtime.device import ort_providers


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--tracknet", required=True, type=Path)
    parser.add_argument("--detector", required=True, type=Path)
    parser.add_argument("--pose", required=True, type=Path)
    parser.add_argument("--start", required=True, type=int)
    parser.add_argument("--count", required=True, type=int)
    parser.add_argument("--fps", required=True, type=float)
    args = parser.parse_args()
    if args.start < 0 or not 8 <= args.count <= 300 or not np.isfinite(args.fps) or args.fps <= 0:
        parser.error("start must be nonnegative, count 8–300 and fps positive")
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or not torch.cuda.is_available():
        parser.error("explicit CUDA_VISIBLE_DEVICES and CUDA availability required")
    cap = cv2.VideoCapture(str(args.video))
    cap.set(cv2.CAP_PROP_POS_FRAMES, args.start)
    frames = []
    try:
        for _ in range(args.count):
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError("could not decode all requested source frames")
            frames.append(cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA))
    finally:
        cap.release()
    torch.set_num_threads(2)
    peak = []
    stop = threading.Event()

    def monitor() -> None:
        while not stop.is_set():
            try:
                text = subprocess.check_output(
                    ["nvidia-smi", "--query-compute-apps=pid,used_gpu_memory", "--format=csv,noheader,nounits"],
                    text=True,
                )
                for line in text.splitlines():
                    pid, used = line.split(",")
                    if int(pid.strip()) == os.getpid():
                        peak.append(int(used.strip()))
            except (OSError, ValueError, subprocess.SubprocessError):
                pass
            stop.wait(0.3)

    worker = threading.Thread(target=monitor, daemon=True)
    worker.start()
    try:
        t0 = time.perf_counter()
        with contextlib.redirect_stdout(sys.stderr):
            shuttle = TrackNetV3(args.tracknet, backend="torch-cuda", threshold=0.5, batch=2)
            providers = ort_providers("onnx-cuda")
            detector = PlayerDetector(args.detector, (512, 512), providers, score_thr=0.35)
            pose = PoseEstimator(args.pose, (192, 256), providers)
        players = PlayerPerception(detector, pose, args.fps, det_stride=2, pose_stride=2, max_players=4)
        loaded = time.perf_counter()
        detections = shuttle.detect(frames, step=8)
        shuttle_done = time.perf_counter()
        people = [players.process(i, frame) for i, frame in enumerate(frames)]
        people_done = time.perf_counter()
        track = process(
            Track.from_arrays(
                np.array([d.x if d else np.nan for d in detections]),
                np.array([d.y if d else np.nan for d in detections]),
                np.array([d is not None for d in detections]),
                np.array([d.conf if d else 0 for d in detections]),
            )
        )
        series = {}
        for i, person_list in enumerate(people):
            for person in person_list:
                name = f"track-{person.track_id}"
                if name not in series:
                    series[name] = PlayerSeries.empty(len(frames))
                series[name].bbox[i] = person.bbox
                if person.kps is not None:
                    series[name].kps[i] = person.kps
        candidates = detect_contacts(WindowObs(frame0=args.start, fps=args.fps, shuttle=track, players=series))
        classifier = RuleStrokeClassifier()
        hypotheses = []
        for candidate in candidates:
            prediction = classifier.predict(
                StrokeContext(
                    frame=candidate.frame,
                    player_id=None,
                    is_serve=False,
                    hitter_court_xy=None,
                    speed_after_px_s=None,
                    frame_height_px=720,
                    flight_time_s=None,
                    vy_after_px_s=None,
                    hitter_side=None,
                    contact_above_head=None,
                )
            )
            hypotheses.append(
                {
                    "frame": candidate.frame,
                    "t_s": candidate.frame / args.fps,
                    "contact_fusion_score": round(candidate.p, 4),
                    "temporary_nearest_track_hypothesis": candidate.player_id,
                    "attribution_reason": candidate.attribution_reason,
                    "attribution_policy": ATTRIBUTION_POLICY,
                    "components": candidate.components,
                    "shot_family": prediction.top[0],
                    "classification_abstention_reason": prediction.abstention_reason,
                }
            )
        elapsed = time.perf_counter() - t0
    finally:
        stop.set()
        worker.join(timeout=2)
    print(
        json.dumps(
            {
                "source_frames": [args.start, args.start + args.count - 1],
                "fps": args.fps,
                "resize": "1280x720",
                "visible_cuda_device": os.environ["CUDA_VISIBLE_DEVICES"],
                "gpu": torch.cuda.get_device_name(0),
                "models": [
                    "TrackNetV3 fp16",
                    "RF-DETR small",
                    "RTMPose M body7",
                    "contact_fusion_v0",
                    "stroke_rules_v0",
                ],
                "onnx_providers": detector.tool.session.get_providers(),
                "elapsed_load_s": round(loaded - t0, 2),
                "elapsed_shuttle_s": round(shuttle_done - loaded, 2),
                "elapsed_player_pose_s": round(people_done - shuttle_done, 2),
                "elapsed_total_s": round(elapsed, 2),
                "sampled_peak_process_gpu_memory_mib": max(peak) if peak else None,
                "torch_peak_reserved_mib": round(torch.cuda.max_memory_reserved() / 1048576, 1),
                "shuttle_detections": sum(d is not None for d in detections),
                "person_count_min_max": [min(map(len, people)), max(map(len, people))],
                "track_ids": sorted(series),
                "contact_candidates": hypotheses,
                "limitations": (
                    "Uncalibrated full frame, no court mask, scene or rally segmentation; cold single-shot background; "
                    "pose/detection stride 2. Temporary tracks are not verified identities; contact scores are not "
                    "calibrated hitter confidence. Shot classifier receives no court/flight evidence and must abstain. "
                    "Not the full application pipeline; no labelled accuracy."
                ),
            },
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
