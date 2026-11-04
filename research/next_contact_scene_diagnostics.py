"""Read-only current-source contact and foreground-continuity diagnostics.

No predictions, annotations, historical artifacts or production modules are changed.
The contact alternatives are sensitivity experiments, not calibrated probabilities.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from dataclasses import asdict
from pathlib import Path

import av
import cv2
import msgpack
import numpy as np

from bai_badminton.events.contact import score_frame
from bai_badminton.observations import PlayerSeries, WindowObs
from bai_badminton.perception.scene import CutDetector
from bai_badminton.perception.shuttle_post import Track

ROOT = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def live_events(rows: list[dict]) -> list[dict]:
    superseded = {r["supersedes"] for r in rows if r.get("supersedes")}
    return [r for r in rows if r["event_id"] not in superseded and r["status"] != "retracted"]


def velocity_fit(xy: np.ndarray, indices: np.ndarray, spatial_sigma: float) -> dict | None:
    """LS velocity with a declared image-scale sensitivity floor, never calibrated covariance."""
    if len(indices) < 2:
        return None
    t = indices.astype(float)
    tc = t - t.mean()
    denominator = float(np.sum(tc * tc))
    values = xy[indices]
    velocity = np.sum(tc[:, None] * (values - values.mean(axis=0)), axis=0) / denominator
    residual = values - (values.mean(axis=0) + tc[:, None] * velocity)
    # Two-point fits cannot estimate a residual variance; the declared floor is retained.
    variance = float(np.sum(residual**2)) / max(1, 2 * (len(indices) - 2))
    sigma_v = math.sqrt((spatial_sigma**2 + variance) / denominator)
    return {
        "velocity": velocity.tolist(),
        "speed": float(np.linalg.norm(velocity)),
        "sample_count": len(indices),
        "span_frames": int(indices[-1] - indices[0]),
        "residual_rms_px": float(np.sqrt(np.mean(residual**2))),
        "slope_sigma_sensitivity_px_per_frame": sigma_v,
    }


def alternative_terms(before: dict, after: dict, scores: dict) -> dict:
    """Bounded absolute gain and direction reliability; there is no incoming-speed rejection."""
    nb, na = before["speed"], after["speed"]
    sb = before["slope_sigma_sensitivity_px_per_frame"]
    sa = after["slope_sigma_sensitivity_px_per_frame"]
    uncertainty = 3.0 * math.hypot(sb, sa)
    qb = max(0.0, 1.0 - 3.0 * sb / nb) if nb else 0.0
    qa = max(0.0, 1.0 - 3.0 * sa / na) if na else 0.0
    direction = scores["redirect"] * min(qb, qa)
    impulse = max(0.0, (na - nb - uncertainty) / (na + nb + uncertainty))
    z = (
        -4.2
        + 3.2 * direction
        + 1.4 * impulse
        + 3.4 * scores["proximity"]
        + 1.1 * scores["swing"]
        + 1.4 * scores["racket_overlap"]
    )
    return {
        "incoming_direction_reliability": qb,
        "outgoing_direction_reliability": qa,
        "absolute_speed_gain_px_per_frame": na - nb,
        "speed_gain_sensitivity_margin": uncertainty,
        "redirect": direction,
        "impulse": impulse,
        "heuristic_support": 1.0 / (1.0 + math.exp(-z)),
    }


def synthetic_controls(spatial_sigma: float) -> list[dict]:
    controls = []
    # Explicit controlled physical hypotheses, not sporting ground-truth labels.
    for name, vb, va in [
        ("small_static_jitter", (0.02, 0.0), (-0.6, 0.0)),
        ("zero_incoming_weak_launch", (0.0, 0.0), (2.0, 0.0)),
        ("zero_incoming_clear_launch", (0.0, 0.0), (10.0, 0.0)),
        ("slow_smooth_apex", (0.6, -0.2), (0.6, 0.2)),
        ("fast_smooth_flight", (20.0, 1.0), (20.0, 1.0)),
        ("fast_racket_redirect", (12.0, -2.0), (-14.0, 3.0)),
        ("slow_terminal_stop", (0.6, 0.0), (0.0, 0.0)),
    ]:
        indices = np.arange(9)
        xy = np.asarray([np.asarray(vb) * (i - 4) if i <= 4 else np.asarray(va) * (i - 4) for i in indices])
        player = PlayerSeries.empty(9)
        player.bbox[:] = [-10, -15, 10, 85]
        window = WindowObs(0, 30, Track.from_arrays(xy[:, 0], xy[:, 1], np.ones(9, bool)), {"anonymous": player})
        candidate = score_frame(window, 4)
        before = velocity_fit(xy, np.arange(1, 5), spatial_sigma)
        after = velocity_fit(xy, np.arange(4, 8), spatial_sigma)
        assert before is not None and after is not None
        controls.append(
            {
                "name": name,
                "span_px": np.ptp(xy, axis=0).tolist(),
                "baseline": asdict(candidate) if candidate else None,
                "before": before,
                "after": after,
                "alternative": alternative_terms(before, after, candidate.scores) if candidate else None,
            }
        )
    return controls


def contact_probe(run: Path, trace_path: Path, spatial_sigma: float) -> dict:
    events = live_events([json.loads(x) for x in (run / "events.jsonl").read_text().splitlines()])
    trace = [json.loads(x) for x in trace_path.read_text().splitlines()]
    steps = {x["frame"]: x for x in trace if x["call"] == "step"}
    rows = []
    for event in events:
        if event["type"] != "contact":
            continue
        frame = event["frame_start"]
        scores = next(e["scores"] for e in event["evidence"] if e["kind"] == "component_scores")
        center = steps.get(frame)
        if center is None:
            continue
        nearby = [steps.get(f) for f in range(frame - 3, frame + 4)]
        # Exact source-bound trace coordinates are already stabilized/processed by the real engine.
        valid = np.array([x is not None and x["visible"] and not x["interpolated"] and not x["replay"] for x in nearby])
        xy = np.array(
            [
                [x.get("x"), x.get("y")]
                if x and x.get("x") is not None and x.get("y") is not None
                else [np.nan, np.nan]
                for x in nearby
            ],
            dtype=float,
        )
        valid &= np.isfinite(xy).all(axis=1)
        before = velocity_fit(xy, np.flatnonzero(valid[:4]), spatial_sigma)
        after = velocity_fit(xy, np.flatnonzero(valid[3:]) + 3, spatial_sigma)
        rows.append(
            {
                "frame": frame,
                "baseline_heuristic_support": event["confidence"],
                "baseline_scores": scores,
                "before": before,
                "after": after,
                "velocity_parity_with_recorded_rounded_scores": bool(
                    before
                    and after
                    and abs(before["speed"] - scores["speed_before"]) < 1e-3
                    and abs(after["speed"] - scores["speed_after"]) < 1e-3
                ),
                "alternative": alternative_terms(before, after, scores) if before and after else None,
                "physical_contact_accuracy": "unknown; no independent reviewed timestamp labels",
            }
        )
    transitions = []
    for row in trace:
        if not 12735 <= row["frame"] <= 12790:
            continue
        if row["call"] == "contact" or row["before"]["state"] != row["after"]["state"]:
            transitions.append(row)
    return {
        "mode": "sensitivity on existing live accepted timestamps; not rerun NMS or semantic inference",
        "contact_count": len(rows),
        "spatial_sigma_sensitivity_px": spatial_sigma,
        "sigma_interpretation": (
            "2.5 px heatmap cell / sqrt(12); declared sensitivity scale, "
            "not calibrated physical localization uncertainty"
        ),
        "contacts": rows,
        "gt27_transitions": transitions,
        "controls": synthetic_controls(spatial_sigma),
    }


def observations(run: Path) -> dict[int, dict]:
    rows = {}
    for p in sorted((run / "runtime/sessions/Test1Experiment/perception").glob("*.msgpack")):
        payload = msgpack.unpackb(p.read_bytes(), raw=False, strict_map_key=False)
        frame_rows = payload["frames"] if "frames" in payload else payload.get("f", [])
        for row in frame_rows:
            rows[row["f"]] = row
    return rows


def decoded_window(video: Path, start: int, stop: int):
    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        target = int(start / 30 / stream.time_base)
        container.seek(target, stream=stream, backward=True)
        for frame in container.decode(stream):
            exact = float(frame.pts * stream.time_base * 30)
            index = int(round(exact))
            assert abs(exact - index) < 1e-6
            if index < start:
                continue
            if index > stop:
                break
            yield index, cv2.resize(frame.to_ndarray(format="bgr24"), (960, 540), interpolation=cv2.INTER_AREA)


def flow_metrics(previous: np.ndarray, current: np.ndarray, box: np.ndarray | None) -> dict:
    mask = np.zeros_like(previous, dtype=np.uint8)
    if box is None:
        mask[:] = 255
    else:
        x1, y1, x2, y2 = box.astype(int)
        x1, x2 = np.clip([x1, x2], 0, previous.shape[1])
        y1, y2 = np.clip([y1, y2], 0, previous.shape[0])
        mask[y1:y2, x1:x2] = 255
    points = cv2.goodFeaturesToTrack(previous, 100, 0.01, 3, mask=mask)
    if points is None:
        return {"feature_count": 0}
    forward, status, error = cv2.calcOpticalFlowPyrLK(previous, current, points, None, winSize=(21, 21), maxLevel=3)
    backward, back_status, _ = cv2.calcOpticalFlowPyrLK(current, previous, forward, None, winSize=(21, 21), maxLevel=3)
    fb_error = np.linalg.norm(backward[:, 0] - points[:, 0], axis=1)
    displacement = np.linalg.norm(forward[:, 0] - points[:, 0], axis=1)
    good = (status[:, 0] > 0) & (back_status[:, 0] > 0)
    reliable = good & (fb_error <= 1.0)
    changed = cv2.absdiff(previous, current)[mask > 0]
    return {
        "feature_count": len(points),
        "flow_status_count": int(good.sum()),
        "forward_backward_consistent_count": int(reliable.sum()),
        "consistent_fraction": float(reliable.mean()),
        "median_forward_backward_error_px": float(np.median(fb_error[good])) if good.any() else None,
        "median_displacement_px": float(np.median(displacement[reliable])) if reliable.any() else None,
        "median_flow_patch_error": float(np.median(error[good])) if good.any() else None,
        "foreground_gray_mae": float(changed.mean()) if len(changed) else None,
        "foreground_fraction_change_gt30": float(np.mean(changed > 30)) if len(changed) else None,
    }


def scene_probe(video: Path, raw: dict[int, dict], windows: dict[str, list[int]] | None = None) -> dict:
    all_rows = []
    # Control windows include fast continuous play, preparation and another scene transition.
    windows = windows or {
        "same_camera_edit": [10680, 11090],
        "fast_continuous_play": [12450, 12966],
        "mixed_visibility": [14390, 14710],
    }
    for label, (start, stop) in windows.items():
        previous = None
        previous_index = None
        cut = CutDetector()
        for index, frame in decoded_window(video, start, stop):
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            detected = cut.update(frame)
            if previous is not None:
                people = raw.get(previous_index, {}).get("p", [])
                person_rows = []
                for person in people:
                    box = np.asarray(person["b"]) * 0.75
                    person_rows.append(
                        {
                            "track_id": person["t"],
                            "detector_matched": person.get("dm"),
                            **flow_metrics(previous, gray, box),
                        }
                    )
                all_rows.append(
                    {
                        "window": label,
                        "previous_frame": previous_index,
                        "frame": index,
                        "histogram_cut": detected,
                        "whole_frame_gray_mae": float(cv2.absdiff(previous, gray).mean()),
                        "people": person_rows,
                    }
                )
            previous, previous_index = gray, index
    return {
        "mode": "source-frame foreground LK and raw difference diagnostics; no thresholds adopted",
        "frames": all_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=ROOT / "artifacts/benchmarking/experiments/fresh_image_exit_v1")
    parser.add_argument(
        "--trace",
        type=Path,
        default=ROOT / "artifacts/benchmarking/experiments/fresh_image_exit_semantic_check/fsm_trace.jsonl",
    )
    parser.add_argument("--video", type=Path, default=ROOT / "data/benchmarking/test1/Test1_Full_rev.mp4")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scene", action="store_true")
    parser.add_argument("--scene-ranges", type=json.loads, help="Diagnostic-only JSON mapping names to [first,last]")
    args = parser.parse_args()
    if args.scene_ranges is not None and (
        not isinstance(args.scene_ranges, dict)
        or not args.scene_ranges
        or any(
            not isinstance(span, list)
            or len(span) != 2
            or any(type(value) is not int or value < 0 for value in span)
            or span[0] >= span[1]
            for span in args.scene_ranges.values()
        )
    ):
        raise ValueError("scene ranges must map names to valid nonnegative [first,last] frame spans")
    args.output.mkdir(parents=True, exist_ok=False)
    snapshot = args.output / "executed_scripts"
    snapshot.mkdir()
    (snapshot / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    contact = contact_probe(args.run, args.trace, 2.5 / math.sqrt(12))
    (args.output / "contact_sensitivity.json").write_text(json.dumps(contact, indent=2, allow_nan=False) + "\n")
    if args.scene:
        raw = observations(args.run)
        scene = scene_probe(args.video, raw, args.scene_ranges)
        (args.output / "scene_foreground_metrics.json").write_text(json.dumps(scene, indent=2, allow_nan=False) + "\n")
    files = [
        Path(__file__),
        ROOT / "sports/badminton/src/bai_badminton/events/contact.py",
        ROOT / "sports/badminton/src/bai_badminton/perception/scene.py",
        args.trace,
        args.run / "events.jsonl",
    ]
    if args.scene:
        files.append(args.video)
    metadata = {
        "executor_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "mode": "CPU source/cached/synthetic diagnostic; no fresh neural inference",
        "scene_ranges": args.scene_ranges,
        "files": {str(p.relative_to(ROOT)): sha(p) for p in files},
        "limitations": [
            "No reviewed independent contact/cut/pixel labels",
            "Alternative scores at prior live timestamps do not reproduce peak selection",
            "Foreground continuity is measured before threshold/model adoption",
        ],
    }
    if args.scene:
        cache = args.run / "runtime/sessions/Test1Experiment/perception"
        metadata["scene_cache_sha256"] = {path.name: sha(path) for path in sorted(cache.glob("*.msgpack"))}
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(
        json.dumps(
            {
                "contacts": contact["contact_count"],
                "controls": {
                    c["name"]: [
                        c["baseline"]["p"] if c["baseline"] else None,
                        c["alternative"]["heuristic_support"] if c["alternative"] else None,
                    ]
                    for c in contact["controls"]
                },
            }
        )
    )


if __name__ == "__main__":
    main()
