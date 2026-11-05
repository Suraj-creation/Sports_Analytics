"""CPU-only checkpoint cost on typed synthetic analytics inputs, not sporting labels."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import statistics
import subprocess
import time
import tracemalloc
from pathlib import Path

from bai_badminton.analytics.match import RallyRecord
from bai_badminton.components import TransactionalAnalytics
from bai_engine.schema import Actors, Event, Provenance

ROOT = Path(__file__).resolve().parents[1]


def stroke(index):
    return Event(
        session_id="checkpoint-synthetic",
        type="stroke",
        frame_start=index,
        frame_end=index,
        pts_us=index * 33333,
        actors=Actors(player_id="P1"),
        provenance=Provenance(model="controlled-contract-fixture"),
        payload={
            "stroke": "clear",
            "hitter_court_xy": [0.0, 1.0],
            "context": {"scope": "synthetic", "frames": [index, index + 3]},
        },
    )


def rally(index):
    return RallyRecord(
        str(index),
        index,
        index,
        index + 10,
        None,
        None,
        "unknown",
        [{"frame": index, "stroke": "clear"}],
        {"P1": 0, "P2": 0},
        1,
        {},
        1 / 3,
    )


def populate(count):
    aggregate = TransactionalAnalytics(30)
    previous = None
    for index in range(count):
        kind = index % 4
        if kind == 0:
            previous = stroke(index)
            aggregate.on_stroke(previous)
        elif kind == 1:
            aggregate.on_presence("P1", [(0.0, 0.0), (0.0, 0.1)])
        elif kind == 2:
            aggregate.on_rally(rally(index))
        else:
            aggregate.on_stroke_retracted(previous)
    return aggregate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    component = ROOT / "sports/badminton/src/bai_badminton/components.py"
    source = component.read_bytes()
    measurements = []
    for count in (100, 1000, 5000):
        gc.collect()
        start = time.perf_counter()
        aggregate = populate(count)
        append_ms = (time.perf_counter() - start) * 1000
        public = aggregate.to_public()
        elapsed = []
        for _ in range(5):
            start = time.perf_counter()
            checkpoint = aggregate.checkpoint()
            elapsed.append((time.perf_counter() - start) * 1000)
            del checkpoint
        tracemalloc.start()
        checkpoint = aggregate.checkpoint()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        start = time.perf_counter()
        aggregate.reset()
        aggregate.restore(checkpoint)
        restore_ms = (time.perf_counter() - start) * 1000
        assert aggregate.to_public() == public
        measurements.append(
            {
                "operations": count,
                "append_ms": append_ms,
                "checkpoint_ms": elapsed,
                "checkpoint_median_ms": statistics.median(elapsed),
                "checkpoint_traced_live_bytes": current,
                "checkpoint_traced_peak_bytes": peak,
                "restore_ms": restore_ms,
                "restored_public_exact": True,
            }
        )
    assert component.read_bytes() == source
    result = {
        "mode": "small CPU-only typed synthetic input replay; no inference, labels or pipeline speed claim",
        "executor_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "component_sha256": hashlib.sha256(source).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_unchanged": True,
        "measurements": measurements,
        "limits": [
            "Five checkpoint samples and one separately traced allocation sample",
            "Tracer excluded from reported checkpoint walltimes",
            "Restore deliberately replays all typed inputs",
            "No sporting accuracy or full-pipeline performance claim",
        ],
    }
    (args.output / "measurements.json").write_text(json.dumps(result, indent=2) + "\n")
    (args.output / "components_executed.py").write_bytes(source)
    (args.output / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
