"""Run an isolated, real doubles pipeline and source-bound draft box agreement.

Labels must be prepared before inference. This is a diagnostic, not an independent
human benchmark or proof of durable identity/pose/contact accuracy. Code is frozen
into the output so edits to the working checkout cannot contaminate the run.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import shutil
import site
import sys
import time
import traceback
from pathlib import Path


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, default=str, allow_nan=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--provenance", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, default=Path())
    args = parser.parse_args()
    runtime = args.runtime_root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    code = output / "source"
    roots = ("engine/src", "sports/badminton/src", "agents/src", "apps/api/src")
    for part in roots:
        shutil.copytree(runtime / part, code / part, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    sys.path[:0] = [str(code / root) for root in roots] + [str(runtime)]
    from bai_badminton.analytics.automatic_individual import build_estimated_individual_analytics
    from bai_badminton.analytics.episode_movement import build_episode_movement
    from bai_engine.bus import LocalBus
    from bai_engine.config import Settings
    from bai_engine.runtime.registry import ModelRegistry
    from bai_engine.runtime.runner import SessionRunner
    from bai_engine.schema import Session, SessionStatus, Source, SourceKind, TrackObject
    from bai_engine.schema.events import current_view
    from bai_engine.schema.session import ParticipantRoster
    from bai_engine.store import SessionRepository
    from research.tracking_benchmark import evaluate_tracking, predictions_from_session

    labels = json.loads(args.labels.read_bytes())
    source_sha = digest(args.source)
    if source_sha != labels["media_sha256"]:
        raise ValueError("Media differs from labels prepared before inference")
    provenance = json.loads(args.provenance.read_bytes())
    if provenance.get("downloaded_clip_sha256") != source_sha:
        raise ValueError("Media differs from the provided source provenance")
    shutil.copy2(args.labels, output / "labels-before-inference.json")
    session_id = labels["session_id"]
    profiles = output / "profiles"
    profiles.mkdir()
    profile = runtime / "config/profiles/gpu-rtx4000.yaml"
    shutil.copy2(profile, profiles / profile.name)
    data = output / "data"
    media = data / "media" / source_sha
    media.mkdir(parents=True)
    shutil.copy2(args.source, media / "source.mp4")
    repo = SessionRepository(data)
    repo.save(
        Session(
            session_id=session_id,
            title="Public doubles diagnostic",
            source=Source(
                kind=SourceKind.UPLOAD, uri=str(media / "source.mp4"), sha256=source_sha, original_name=args.source.name
            ),
            roster=ParticipantRoster(match_format="doubles"),
            profile="gpu-rtx4000",
        )
    )
    settings = Settings(
        _env_file=None,
        data_dir=data,
        models_dir=runtime / "models",
        profiles_dir=profiles,
        profile="gpu-rtx4000",
        proxy_height=720,
    )
    registry = ModelRegistry(settings.models_dir)
    runner = SessionRunner(session_id, repo, LocalBus(), settings, registry)
    manifest = {
        "source_sha256": source_sha,
        "labels_before_inference_sha256": digest(args.labels),
        "source_files": {str(p.relative_to(code)): digest(p) for p in sorted(code.rglob("*.py"))},
        "profile_sha256": digest(profile),
        "models": registry.status(),
        "python": sys.version,
        "review_status": "AI-draft pre-inference boxes; not human independent accuracy",
        "source_provenance": provenance,
        "harness_sha256": digest(Path(__file__)),
    }
    dump(output / "run-manifest.json", manifest)
    started = time.monotonic()
    try:
        print("Running real doubles inference in isolated session", flush=True)
        runner._ensure_media()
        runner._analyse()
        if runner._transcode_thread is not None:
            runner._transcode_thread.join(timeout=60)
        state = repo.get(session_id)
        if state is None or state.status is not SessionStatus.ANALYSED:
            raise RuntimeError(f"Analysis did not complete: {state}")
        for key in ("fps_num", "fps_den", "width", "height"):
            if labels[key] != getattr(state.media, key):
                raise ValueError(f"Proxy timebase/dimensions changed: {key}")
        labels["proxy_sha256"] = digest(media / "proxy.mp4")
        dump(output / "labels-bound.json", labels)
        predictions = predictions_from_session(data, session_id, labels)
        dump(output / "predictions.json", predictions)
        agreement = evaluate_tracking(labels, predictions, allow_draft=True)
        dump(output / "draft-localization-agreement.json", agreement)
        rows = (
            repo.tracks(session_id).read([TrackObject.PLAYER, TrackObject.SHUTTLE], 0, state.frontier_frame).to_pylist()
        )
        players = [r for r in rows if r["obj"] == "player"]
        shuttle = [r for r in rows if r["obj"] == "shuttle"]
        count = collections.Counter(r["frame_idx"] for r in players if r["visible"])
        events = current_view(repo.events(session_id).query())
        report = {
            "status": state.status.value,
            "elapsed_s": time.monotonic() - started,
            "frontier_frame": state.frontier_frame,
            "media": state.media.model_dump(mode="json"),
            "degraded": runner.sport.degraded(),
            "event_counts": dict(collections.Counter(e.type for e in events)),
            "player_rows": len(players),
            "player_frames": len(count),
            "visible_player_count_histogram": dict(collections.Counter(count.values())),
            "pose_rows": sum(r.get("keypoints") is not None for r in players),
            "named_player_rows": sum(r.get("player_id") is not None for r in players),
            "shuttle_rows": len(shuttle),
            "shuttle_visible_rows": sum(r["visible"] for r in shuttle),
            "note": (
                "Coverage counts are not detection/pose recall. Sparse draft boxes do not establish identity accuracy."
            ),
        }
        dump(output / "inference.json", report)
        dump(output / "analytics.json", runner.sport.analytics())
        spatial_args = {
            "max_frame": state.frontier_frame,
            "fps": float(state.media.fps),
            "frame_width": state.media.width,
            "frame_height": state.media.height,
        }
        dump(
            output / "episode-movement.json",
            build_episode_movement(
                repo.events(session_id),
                repo.tracks(session_id),
                start_frame=0,
                end_frame=state.frontier_frame,
                **spatial_args,
            ),
        )
        dump(
            output / "estimated-individual.json",
            build_estimated_individual_analytics(
                repo.events(session_id), repo.tracks(session_id), state.roster, **spatial_args
            ),
        )
        print(json.dumps(report, default=str), flush=True)
    except BaseException as exc:
        dump(
            output / "failure.json",
            {"error": str(exc), "elapsed_s": time.monotonic() - started, "traceback": traceback.format_exc()},
        )
        raise
    finally:
        runner.stop()
        repo.close()


if __name__ == "__main__":
    if sys.platform == "linux":
        library_dirs = []
        for packages in map(Path, site.getsitepackages()):
            library_dirs.extend(sorted(packages.glob("nvidia/*/lib")))
            if (packages / "torch/lib").is_dir():
                library_dirs.append(packages / "torch/lib")
        existing = os.environ.get("LD_LIBRARY_PATH", "").split(":")
        missing = [str(path) for path in library_dirs if str(path) not in existing]
        if missing:
            environment = dict(os.environ)
            environment["LD_LIBRARY_PATH"] = ":".join(missing + [path for path in existing if path])
            os.execve(sys.executable, [sys.executable, *sys.argv], environment)  # noqa: S606 - same interpreter/script
    main()
