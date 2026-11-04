"""Label-free diagnostic replay of production semantics from frozen perception.

This is NOT fresh video inference. The actual production decoder, engine, ports,
calibration and format changes are used. Baseline interval parity is mandatory
before its traces can support causal explanations. Ground truth is never read.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bai_badminton.components import _Rally  # noqa: E402
from bai_badminton.court import Homography  # noqa: E402
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig  # noqa: E402
from bai_badminton.events.rally_fsm import RallyParams  # noqa: E402
from bai_badminton.plugin import BadmintonSession  # noqa: E402
from bai_engine.schema import Provenance  # noqa: E402
from bai_engine.store import EventStore  # noqa: E402
from scripts.benchmarking.evaluate_rallies import write_predictions  # noqa: E402
from scripts.benchmarking.production_inference import digest, dump  # noqa: E402


def finite(value):
    return float(value) if value is not None and math.isfinite(value) else None


def replay(baseline: Path, output: Path, overrides: dict):
    import msgpack

    output.mkdir(parents=True, exist_ok=False)
    metadata = json.loads((baseline / "benchmark_metadata.json").read_text())
    inference = json.loads((baseline / "inference.json").read_text())
    original_events = [json.loads(line) for line in (baseline / "raw_events.jsonl").open()]
    calibration = next(e for e in original_events if e["type"] == "calibration")["payload"]
    format_changes = {e["frame_start"]: e["payload"] for e in original_events if e["type"] == "format_decision"}
    trace = []
    engine = None

    def state(fsm):
        return {
            "state": fsm.state.value,
            "start": fsm.start,
            "tentative_end": fsm.tentative_end,
            "end_reason": fsm.end_reason,
            "closed": asdict(fsm.closed) if fsm.closed else None,
            "moving_run": fsm._run_visible,
            "moving_run_start": fsm._run_start,
            "invisible_run": fsm._invisible,
            "last_contact": fsm._last_contact_frame,
        }

    class TracedRally(_Rally):
        def step(self, frame, visible, speed, replay=False):
            before = state(self)
            result = super().step(frame, visible, speed, replay)
            idx = frame - engine._proc0
            processed = engine._proc
            trace.append(
                {
                    "call": "step",
                    "frame": frame,
                    "visible": visible,
                    "speed": finite(speed),
                    "replay": replay,
                    "x": finite(processed.x[idx]),
                    "y": finite(processed.y[idx]),
                    "interpolated": bool(processed.interp[idx]),
                    "before": before,
                    "after": state(self),
                    "update": asdict(result),
                }
            )
            return result

        def on_contact(self, frame):
            before = state(self)
            result = super().on_contact(frame)
            trace.append(
                {"call": "contact", "frame": frame, "before": before, "after": state(self), "update": asdict(result)}
            )
            return result

        def on_discontinuity(self, frame):
            before = state(self)
            result = super().on_discontinuity(frame)
            trace.append(
                {
                    "call": "discontinuity",
                    "frame": frame,
                    "before": before,
                    "after": state(self),
                    "update": asdict(result),
                }
            )
            return result

        def flush(self, frame):
            before = state(self)
            result = super().flush(frame)
            trace.append(
                {"call": "flush", "frame": frame, "before": before, "after": state(self), "update": asdict(result)}
            )
            return result

    params = RallyParams(fps=metadata["video_fps"], **overrides)
    store = EventStore(output / "events.sqlite", "DiagnosticReplay")
    engine = BadmintonMatchEngine(
        "DiagnosticReplay",
        EngineConfig(
            fps=params.fps, frame_width=1280, frame_height=720, profile="gpu-rtx4000", match_format_known=False
        ),
        store,
        rally_segmenter=TracedRally(params),
    )
    net = calibration["net_top"]
    engine.set_calibration(
        0,
        Homography.from_json(calibration),
        tuple(net[0]),
        tuple(net[1]),
        cam_ref=calibration["cam_ref"],
        extra=calibration,
    )
    started = time.monotonic()
    cache_paths = sorted((baseline / "runtime/sessions/BenchmarkTest1/perception").glob("*.msgpack"))
    for path in cache_paths:
        data = path.read_bytes()
        recorded = msgpack.unpackb(data, raw=False)
        # Diagnostic-only receiver supplies the RECORDED contract to the existing
        # structural decoder; it never restores live tracker/perception state.
        receiver = SimpleNamespace(
            perception=SimpleNamespace(ref_id=recorded["cr"]), _isolation_id=lambda record=recorded: record["ci"]
        )
        chunk = BadmintonSession.decode_perception(receiver, data, diagnostic=True)
        cursor = chunk.start
        boundaries = [frame for frame in format_changes if chunk.start <= frame <= chunk.end]
        for frame in sorted(boundaries):
            if cursor < frame:
                engine.ingest(BadmintonSession._slice_perception(chunk, cursor, frame - 1))
            decision = format_changes[frame]
            engine.set_match_format(
                decision["match_format"],
                frame,
                Provenance(model="diagnostic:recorded-format"),
                decision=decision["decision"],
            )
            cursor = frame
        engine.ingest(BadmintonSession._slice_perception(chunk, cursor, chunk.end))
        engine.drain_tracks()
        if chunk.end % 1800 < 60:
            print(f"replay frame {chunk.end}", flush=True)
    engine.flush()
    events = store.query()
    ends = sorted((e.frame_start, e.frame_end) for e in events if e.type == "rally_end")
    reference = sorted((e["start"], e["end"]) for e in inference["rally_events"])
    parity = ends == reference
    write_predictions(output / "predicted_rallies.csv", ends, params.fps)
    with (output / "fsm_trace.jsonl").open("w") as stream:
        for row in trace:
            stream.write(json.dumps(row, allow_nan=False) + "\n")
    with (output / "events.jsonl").open("w") as stream:
        for event in store.query(live_only=False):
            stream.write(event.model_dump_json() + "\n")
    dump(
        output / "replay_metadata.json",
        {
            "mode": "recorded-perception diagnostic semantic replay; NOT fresh inference",
            "baseline_interval_parity": parity,
            "baseline_interval_count": len(reference),
            "interval_count": len(ends),
            "parameters": asdict(params),
            "overrides": overrides,
            "elapsed_seconds": time.monotonic() - started,
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "video_sha256": metadata["source_video_sha256"],
            "ground_truth_sha256": metadata["ground_truth_sha256"],
            "ground_truth_usage": "hash copied as provenance; no label file read by replay",
            "cache_sha256": {path.name: digest(path) for path in cache_paths},
            "source_sha256": {
                str(p.relative_to(ROOT)): digest(p)
                for root in ("engine/src", "sports/badminton/src")
                for p in sorted((ROOT / root).rglob("*.py"))
            },
            "checkpoint_identifiers": metadata["models"],
            "runtime_versions": metadata["runtime_dependencies"],
            "profile": inference["effective_profile"],
            "trace_sha256": digest(output / "fsm_trace.jsonl"),
        },
    )
    engine.close()
    store.close()
    print(json.dumps({"parity": parity, "intervals": len(ends)}), flush=True)
    if not overrides and not parity:
        raise RuntimeError("baseline replay is not interval-exact; do not use its traces as causal evidence")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=ROOT / "outputs/benchmarking/test1")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rally-params", type=json.loads, default={})
    args = parser.parse_args()
    replay(args.baseline.resolve(), args.output.resolve(), args.rally_params)
