"""Isolated real production worker. No label path, count, or evaluation input.

Writes only final current-view rally_end intervals, including non-official
exchanges. Point acceptance and shot/outcome payloads never filter predictions.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.benchmarking.evaluate_rallies import write_predictions  # noqa: E402


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False, default=str) + "\n")


def run(video, output, profile):
    from bai_engine.bus import LocalBus
    from bai_engine.config import Settings
    from bai_engine.runtime.registry import ModelRegistry
    from bai_engine.runtime.runner import SessionRunner
    from bai_engine.schema import Session, SessionStatus, Source, SourceKind
    from bai_engine.store import SessionRepository

    # This store is fresh and private to the benchmark. Original bytes are used
    # directly; only the normal production proxy is generated beside them.
    data = output / "runtime"
    data.mkdir(exist_ok=False)
    source_sha = digest(video)
    repo = SessionRepository(data)
    session_id = "BenchmarkTest1"
    repo.save(
        Session(
            session_id=session_id,
            title="Test 1 rally boundary baseline",
            source=Source(kind=SourceKind.UPLOAD, uri=str(video), original_name=video.name, sha256=source_sha),
            profile=profile,
        )
    )
    settings = Settings(
        _env_file=None,
        data_dir=data,
        models_dir=ROOT / "models",
        profiles_dir=output / "profiles",
        profile=profile,
        proxy_height=720,
    )
    registry = ModelRegistry(settings.models_dir)
    dump(output / "model_registry_before.json", registry.status())
    runner = SessionRunner(session_id, repo, LocalBus(), settings, registry)
    started = time.monotonic()
    try:
        runner._ensure_media()
        runner._analyse()
        if runner._transcode_thread is not None:
            runner._transcode_thread.join(timeout=60)
            if runner._transcode_thread.is_alive():
                raise RuntimeError("production transcode did not finish")
        state = repo.get(session_id)
        if state is None or state.status is not SessionStatus.ANALYSED:
            raise RuntimeError("production session did not finish analysis")
        events = repo.events(session_id).query()
        ends = sorted((e for e in events if e.type == "rally_end"), key=lambda e: (e.frame_start, e.frame_end, e.seq))
        with (output / "raw_events.jsonl").open("x") as stream:
            # Preserve the full append-only log, including superseded/retracted evidence.
            for event in repo.events(session_id).query(live_only=False):
                stream.write(event.model_dump_json() + "\n")
        fps = float(state.media.fps)
        proxy = repo.media_paths(source_sha).proxy
        dump(
            output / "inference.json",
            {
                "status": state.status.value,
                "elapsed_seconds": time.monotonic() - started,
                "source_sha256": source_sha,
                "media": state.media.model_dump(mode="json"),
                "proxy_sha256": digest(proxy),
                "frontier_frame": state.frontier_frame,
                "event_counts": dict(collections.Counter(e.type for e in events)),
                "rally_events": [
                    {
                        "event_id": e.event_id,
                        "start": e.frame_start,
                        "end": e.frame_end,
                        "end_reason": e.payload.get("end_reason"),
                    }
                    for e in ends
                ],
                "degraded": runner.sport.degraded(),
                "execution_backends": {
                    kind: runner.sport.perception.runtimes.get(kind) for kind in ("shuttle", "player_detector", "pose")
                },
                "pipeline": runner.sport.describe_pipeline(),
                "model_registry_after": registry.status(),
                "effective_profile": runner.sport.perception.profile.model_dump(mode="json"),
                "perception_models": runner.sport.perception.models,
                "perception_runtimes": runner.sport.perception.runtimes,
            },
        )
        write_predictions(output / "predicted_rallies.csv", [(e.frame_start, e.frame_end) for e in ends], fps)
        print(f"INFERENCE_COMPLETE: {len(ends)} production rally_end events", flush=True)
    finally:
        if runner.sport is not None:
            runner.sport.close()
        repo.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--profile", required=True)
    args = parser.parse_args()
    run(args.video.resolve(), args.output.resolve(), args.profile)


if __name__ == "__main__":
    main()
