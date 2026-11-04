"""Run real inference and a frozen published-reference evaluation in an isolated directory.

Example (repeat with a different --code-root and a NEW --output for the candidate):
  .venv/bin/python research/evaluation/run_pipeline_reference.py \
    --code-root data/audit-20261029/baseline-source --runtime-root . \
    --reference-dir data/audit-20261029/reference --recording-id 0044 \
    --output data/audit-20261029/evaluation/baseline-0044

No user session is touched. Source and annotation hashes are verified before inference.
The same evaluator and explicit GPU profile are used for baseline and candidate runs.
Published hit anchors measure reference agreement, not independently verified contacts.
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


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, default=str, allow_nan=False) + "\n")


def execution_backends(sport: object) -> dict:
    """Read the loaded sessions, not a profile's requested backend names."""
    perception = getattr(sport, "perception", None)
    players = getattr(perception, "players", None)
    result = {}
    for name, stage in (("player_detector", "detector"), ("pose", "pose")):
        wrapper = getattr(players, stage, None)
        session = getattr(getattr(wrapper, "tool", None), "session", None)
        result[name] = None if session is None else {"runtime": "onnxruntime", "providers": session.get_providers()}
    shuttle = getattr(perception, "shuttle", None)
    ort = getattr(shuttle, "_ort", None)
    torch_model = getattr(shuttle, "_torch", None)
    if ort is not None:
        result["shuttle"] = {"runtime": "onnxruntime", "providers": ort.get_providers()}
    elif torch_model is not None:
        parameter = next(torch_model.parameters())
        result["shuttle"] = {"runtime": "torch", "device": str(parameter.device), "dtype": str(parameter.dtype)}
    else:
        result["shuttle"] = None
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code-root", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--reference-dir", type=Path, required=True)
    parser.add_argument("--recording-id", choices=("0044", "0046"), required=True)
    parser.add_argument("--profile", default="gpu-rtx4000")
    parser.add_argument("--profile-file", type=Path, help="Explicit frozen profile; default: sibling baseline-source")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    code = args.code_root.resolve()
    runtime = args.runtime_root.resolve()
    reference = args.reference_dir.resolve()
    output = args.output.resolve()
    evaluator_root = Path(__file__).resolve().parents[2]
    # Import all pipeline packages from the explicitly selected source tree.
    roots = [code / part for part in ("engine/src", "sports/badminton/src", "agents/src", "apps/api/src")]
    sys.path[:0] = [str(root) for root in roots] + [str(evaluator_root)]

    import bai_badminton.plugin as plugin_module
    import bai_engine.runtime.runner as runner_module
    from bai_engine.bus import LocalBus
    from bai_engine.config import Settings
    from bai_engine.runtime.registry import ModelRegistry
    from bai_engine.runtime.runner import SessionRunner
    from bai_engine.schema import Session, SessionStatus, Source, SourceKind, TrackObject
    from bai_engine.store import SessionRepository
    from research.evaluation.benchmark_reference_session import benchmark_session
    from research.finebadminton_reference import convert_reference

    if not Path(runner_module.__file__).is_relative_to(code) or not Path(plugin_module.__file__).is_relative_to(code):
        raise RuntimeError("Selected source tree was not imported")
    binding = json.loads((reference / "provenance.json").read_text())
    recording = args.recording_id
    source = reference / f"{recording}.mp4"
    labels = reference / f"{recording}_updated.json"
    source_sha = digest(source)
    label_sha = digest(labels)
    if source_sha != binding["sha256"][f"videos/{recording}.mp4"]:
        raise ValueError("Source media digest differs from pinned release")
    if label_sha != binding["sha256"][f"finebadminton-20K/{recording}_updated.json"]:
        raise ValueError("Annotations digest differs from pinned release")
    output.mkdir(parents=True, exist_ok=False)
    profiles = output / "profiles"
    profiles.mkdir()
    # Always take the configuration from the frozen baseline tree, even for candidate.
    frozen = args.profile_file or reference.parent / "baseline-source/config/profiles" / f"{args.profile}.yaml"
    if not frozen.is_file():
        raise FileNotFoundError("Frozen baseline profile is required beside reference/")
    shutil.copy2(frozen, profiles / f"{args.profile}.yaml")
    source_files = sorted(path for root in roots for path in root.rglob("*.py"))
    source_hashes = {str(path.relative_to(code)): digest(path) for path in source_files}
    source_fingerprint = hashlib.sha256(json.dumps(source_hashes, sort_keys=True).encode()).hexdigest()
    data = output / "data"
    media = data / "media" / source_sha
    media.mkdir(parents=True)
    shutil.copy2(source, media / "source.mp4")
    session_id = f"Fine{recording}"
    repo = SessionRepository(data)
    repo.save(
        Session(
            session_id=session_id,
            title=f"Published reference {recording}",
            source=Source(
                kind=SourceKind.UPLOAD, uri=str(media / "source.mp4"), original_name=source.name, sha256=source_sha
            ),
            profile=args.profile,
        )
    )
    settings = Settings(
        _env_file=None,
        data_dir=data,
        models_dir=runtime / "models",
        profiles_dir=profiles,
        profile=args.profile,
        proxy_height=720,
    )
    registry = ModelRegistry(settings.models_dir)
    runner = SessionRunner(session_id, repo, LocalBus(), settings, registry)
    report = {
        "code_root": str(code),
        "source_sha256": source_sha,
        "annotations_sha256": label_sha,
        "profile_sha256": digest(frozen),
        "code_fingerprint": source_fingerprint,
        "source_files": source_hashes,
        "evaluator_files": {
            str(path.relative_to(evaluator_root)): digest(path)
            for path in (
                Path(__file__).resolve(),
                evaluator_root / "research/evaluation/benchmark_reference_session.py",
                evaluator_root / "research/finebadminton_reference.py",
            )
        },
        "models": registry.status(),
        "python": sys.version,
        "session_id": session_id,
        "reference_split": "held_out" if recording == "0046" else "development",
        "reference_reservation_scope": (
            "Reserved regression recording for this repair pass; prior project results exist, so not never-seen."
            if recording == "0046"
            else "Development recording used to diagnose these repairs."
        ),
        "scope_note": "Provider-refined anchors; not our independently reviewed racket contacts.",
    }
    dump(output / "run-manifest.json", report)
    started = time.monotonic()
    try:
        print(json.dumps({"stage": "inference", "recording": recording, "code_root": str(code)}), flush=True)
        runner._ensure_media()
        runner._analyse()
        if runner._transcode_thread is not None:
            runner._transcode_thread.join(timeout=60)
        state = repo.get(session_id)
        if state is None or state.status is not SessionStatus.ANALYSED:
            raise RuntimeError(f"Analysis did not complete: {state}")
        rows = (
            repo.tracks(session_id).read([TrackObject.PLAYER, TrackObject.SHUTTLE], 0, state.frontier_frame).to_pylist()
        )
        players = [row for row in rows if row["obj"] == "player"]
        shuttle = [row for row in rows if row["obj"] == "shuttle"]
        events = repo.events(session_id).query()
        inference = {
            "status": state.status.value,
            "elapsed_s": time.monotonic() - started,
            "media": state.media.model_dump(mode="json"),
            "frontier_frame": state.frontier_frame,
            "event_counts": dict(collections.Counter(e.type for e in events)),
            "degraded": runner.sport.degraded(),
            "execution_backends": execution_backends(runner.sport),
            "proxy_sha256": digest(media / "proxy.mp4"),
            "player_rows": len(players),
            "player_frames": len({r["frame_idx"] for r in players}),
            "pose_rows": sum(r["keypoints"] is not None for r in players),
            "anonymous_player_rows": sum(r["player_id"] is None for r in players),
            "shuttle_rows": len(shuttle),
            "shuttle_visible_rows": sum(r["visible"] for r in shuttle),
        }
        dump(output / "inference.json", inference)
        info = state.media
        manifests = convert_reference(
            labels.read_bytes(),
            session_id=session_id,
            video_name=source.name,
            media_sha256=source_sha,
            expected_media_sha256=source_sha,
            expected_source_sha256=label_sha,
            fps_num=info.fps_num,
            fps_den=info.fps_den,
            n_frames=info.n_frames,
            width=info.width,
            height=info.height,
            source_revision=binding["revision"],
            split=report["reference_split"],
            held_out_reserved_before_tuning=recording == "0046",
            accept_published_review=True,
        )
        annotations = output / "annotations"
        annotations.mkdir()
        for index, manifest in enumerate(manifests):
            dump(annotations / f"rally-{index:04d}.json", manifest)
        result = benchmark_session(data, session_id, annotations, tolerance_s=0.2)
        dump(output / "benchmark.json", result)
        changed = [name for name, sha in source_hashes.items() if digest(code / name) != sha]
        if changed:
            dump(output / "source-changed-during-run.json", changed)
            raise RuntimeError("Source changed during run; result must not be treated as a frozen candidate")
        print(
            json.dumps(
                {
                    "stage": "complete",
                    "recording": recording,
                    "elapsed_s": inference["elapsed_s"],
                    "benchmark": str(output / "benchmark.json"),
                }
            ),
            flush=True,
        )
    except BaseException as error:
        dump(
            output / "failure.json",
            {"error": str(error), "elapsed_s": time.monotonic() - started, "traceback": traceback.format_exc()},
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
            os.execve(sys.executable, [sys.executable, *sys.argv], environment)  # noqa: S606 - same trusted interpreter/script
    main()
