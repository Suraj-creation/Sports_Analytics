"""Frozen exposed-data stress orchestration using existing production executors.

prepare writes new input-only sessions/profile/plan. run leases one physical GPU
and delegates three clips to validate_real_video_runtime, or executes an ordinary
SessionRunner for the full Test7 upload. No annotation value enters a worker.
"""

from __future__ import annotations

import argparse
import collections
import contextlib
import copy
import hashlib
import json
import math
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.production_resource_guard import gpu_lease, gpu_uuid  # noqa: E402
from research.validate_real_video_runtime import validate_output  # noqa: E402

PERCEPTION_CATALOG_SCHEMA = "production-perception-completion-catalog:v1"
PERCEPTION_CATALOG_NAME = "perception_completion_catalog.json"
PERCEPTION_CATALOG_LIMITS = {
    "max_files": 10_000,
    "max_source_frames": 2_000_000,
    "max_frames_per_cache": 4096,
    "max_cache_bytes": 16 * 1024 * 1024,
    "max_total_cache_bytes": 8 * 1024**3,
    "max_catalog_bytes": 8 * 1024 * 1024,
    "accepted_codec_versions": [20],
}


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump_new(path: Path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def perception_catalog(output: Path, *, session_id: str, source_sha256: str, proxy_sha256: str, media: dict) -> dict:
    """Bound one completed worker's exact diagnostic files, not model accuracy.

    Cache header ends are inclusive canonical proxy frames. Source/proxy identity
    is bound by the worker receipt; codec20 itself has no source-hash field. This
    checks header/extent integrity, not the complete sport observation schema.
    """
    import msgpack

    if not isinstance(session_id, str) or not session_id.isalnum() or len(session_id) > 96:
        raise ValueError("cache catalog requires a canonical session ID")
    for value in [source_sha256, proxy_sha256]:
        if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise ValueError("cache catalog requires source/proxy SHA256 bindings")
    keys = ["n_frames", "width", "height", "fps_num", "fps_den"]
    if not isinstance(media, dict) or any(type(media.get(key)) is not int or media[key] <= 0 for key in keys):
        raise ValueError("cache catalog requires positive integer canonical media fields")
    bound_media = {key: media[key] for key in keys}
    if media["n_frames"] > PERCEPTION_CATALOG_LIMITS["max_source_frames"]:
        raise ValueError("cache catalog source frame limit exceeded")
    output = output.absolute()
    if output.is_symlink() or not output.is_dir():
        raise ValueError("cache catalog output must be an owned directory, not a symlink")
    cache_dir = output
    for part in ["data", "sessions", session_id, "perception"]:
        cache_dir = cache_dir / part
        if cache_dir.is_symlink() or not cache_dir.is_dir():
            raise ValueError("missing cache directory or symlink escape")
    paths = []
    for path in cache_dir.iterdir():
        if path.is_symlink() or not path.is_file() or path.suffix != ".msgpack":
            raise ValueError("foreign cache entry or symlink escape")
        paths.append(path)
        if len(paths) > PERCEPTION_CATALOG_LIMITS["max_files"]:
            raise ValueError("cache catalog file limit exceeded")
    if not paths:
        raise ValueError("completed full worker has zero perception caches")
    files, next_frame, total_bytes = [], 0, 0
    for index, path in enumerate(sorted(paths)):
        if path.name != f"seg_{index:05d}.msgpack":
            raise ValueError("cache population has missing or foreign segment names")
        size = path.stat().st_size
        if not 0 < size <= PERCEPTION_CATALOG_LIMITS["max_cache_bytes"]:
            raise ValueError("cache file byte limit exceeded")
        total_bytes += size
        if total_bytes > PERCEPTION_CATALOG_LIMITS["max_total_cache_bytes"]:
            raise ValueError("cache catalog total byte limit exceeded")
        with path.open("rb") as stream:
            data = stream.read(PERCEPTION_CATALOG_LIMITS["max_cache_bytes"] + 1)
        if len(data) != size:
            raise ValueError("cache changed during its completion snapshot")
        try:
            value = msgpack.unpackb(
                data,
                raw=False,
                max_array_len=4096,
                max_map_len=4096,
                max_str_len=1024 * 1024,
                max_bin_len=PERCEPTION_CATALOG_LIMITS["max_cache_bytes"],
            )
            if not isinstance(value, dict) or type(value.get("v")) is not int:
                raise ValueError("invalid cache header")
            if value["v"] not in PERCEPTION_CATALOG_LIMITS["accepted_codec_versions"]:
                raise ValueError("unsupported cache codec version")
            start, end, frames, identity = value["start"], value["end"], value["frames"], value["ci"]
            if (
                type(start) is not int
                or type(end) is not int
                or start != next_frame
                or not start <= end < media["n_frames"]
            ):
                raise ValueError("cache frame bounds are not contiguous canonical source coverage")
            if not isinstance(frames, list) or not 0 < len(frames) <= PERCEPTION_CATALOG_LIMITS["max_frames_per_cache"]:
                raise ValueError("cache frame population exceeds its bound")
            if len(frames) != end - start + 1 or any(
                not isinstance(frame, dict) or type(frame.get("f")) is not int or frame["f"] != start + offset
                for offset, frame in enumerate(frames)
            ):
                raise ValueError("cache frame IDs do not match its complete header extent")
            if not isinstance(identity, dict) or identity.get("frame_size") != [media["width"], media["height"]]:
                raise ValueError("cache image dimensions do not match canonical media")
            fps = identity.get("fps")
            if (
                type(fps) not in {int, float}
                or not math.isfinite(fps)
                or not math.isclose(fps, media["fps_num"] / media["fps_den"], rel_tol=0, abs_tol=1e-9)
            ):
                raise ValueError("cache timebase does not match canonical media")
            header = {key: value.get(key) for key in ["v", "start", "end", "cr", "ci", "models"]}
            header_sha = hashlib.sha256(json.dumps(header, sort_keys=True, allow_nan=False).encode()).hexdigest()
        except (KeyError, TypeError, ValueError, msgpack.exceptions.UnpackException) as error:
            raise ValueError(f"invalid bounded cache header/frames: {path.name}: {error}") from error
        files.append(
            {
                "path": path.relative_to(output).as_posix(),
                "bytes": size,
                "sha256": hashlib.sha256(data).hexdigest(),
                "codec_version": value["v"],
                "start": start,
                "end": end,
                "frame_count": len(frames),
                "header_sha256": header_sha,
            }
        )
        next_frame = end + 1
    if next_frame != media["n_frames"]:
        raise ValueError("completed cache population does not cover every canonical source frame")
    return {
        "schema": PERCEPTION_CATALOG_SCHEMA,
        "snapshot_stage": "after_analysis_before_worker_completion_receipt",
        "session_id": session_id,
        "source_sha256": source_sha256,
        "proxy_sha256": proxy_sha256,
        "media": bound_media,
        "limits": copy.deepcopy(PERCEPTION_CATALOG_LIMITS),
        "cache_frame_semantics": "zero-origin canonical CFR frames; cache header end inclusive",
        "scope": "worker completion file/header/extent identity; no physical accuracy or model-origin attestation",
        "file_count": len(files),
        "frame_count": next_frame,
        "total_bytes": total_bytes,
        "files": files,
    }


def _perception_receipt(catalog: dict, sha256: str) -> dict:
    return {
        "schema": PERCEPTION_CATALOG_SCHEMA,
        "path": PERCEPTION_CATALOG_NAME,
        "sha256": sha256,
        "file_count": catalog["file_count"],
        "frame_count": catalog["frame_count"],
        "snapshot_stage": catalog["snapshot_stage"],
    }


def write_perception_catalog(output: Path, **bindings) -> dict:
    """Future worker only: exclusive-create before publishing inference.json."""
    catalog = perception_catalog(output, **bindings)
    path = output / PERCEPTION_CATALOG_NAME
    dump_new(path, catalog)
    return _perception_receipt(catalog, digest(path))


def verify_perception_catalog(output: Path, receipt: dict, **bindings) -> dict:
    """Parent/replay: exact hash, binding, population and bytes; never backfill."""
    if output.is_symlink() or not output.is_dir():
        raise ValueError("cache catalog output must be an owned directory, not a symlink")
    if not isinstance(receipt, dict) or receipt.get("path") != PERCEPTION_CATALOG_NAME:
        raise ValueError("missing or foreign perception cache catalog receipt")
    path = output / PERCEPTION_CATALOG_NAME
    if path.is_symlink() or not path.is_file() or path.stat().st_size > PERCEPTION_CATALOG_LIMITS["max_catalog_bytes"]:
        raise ValueError("missing, symlinked or oversized perception cache catalog")
    with path.open("rb") as stream:
        data = stream.read(PERCEPTION_CATALOG_LIMITS["max_catalog_bytes"] + 1)
    if len(data) > PERCEPTION_CATALOG_LIMITS["max_catalog_bytes"]:
        raise ValueError("perception cache catalog byte limit exceeded")
    sha256 = hashlib.sha256(data).hexdigest()
    if receipt.get("sha256") != sha256:
        raise ValueError("perception cache catalog SHA256 mismatch")
    recorded = json.loads(data)
    observed = perception_catalog(output, **bindings)
    if recorded != observed or receipt != _perception_receipt(observed, sha256):
        raise ValueError("perception cache catalog population/bytes/header/source binding mismatch")
    return recorded


def source_files():
    paths = [
        Path(__file__),
        ROOT / "research/production_resource_guard.py",
        ROOT / "research/validate_real_video_runtime.py",
    ]
    for name in ["engine/src", "sports/badminton/src", "agents/src", "apps/api/src", "apps/web/src"]:
        paths.extend(p for p in (ROOT / name).rglob("*") if p.suffix in {".py", ".ts", ".tsx"})
    return sorted(set(paths))


def passive_profile(raw):
    """Only recorded diagnostic ranges change; numerical profile settings are exact."""
    result = copy.deepcopy(raw)
    if raw["components"]["shuttle_association"]["implementation"] != "coobserved-static-hypotheses-v1":
        raise ValueError("expected the frozen primary association profile")
    content = raw["components"]["content_continuity"]
    if (
        content["implementation"] != "foreground-content-continuity-v1"
        or content["params"]["mode"] != "barrier_hypothesis_v1"
    ):
        raise ValueError("expected the frozen primary scene profile")
    result["shuttle"]["params"]["diagnostics"]["ranges"] = []
    expected = copy.deepcopy(result)
    expected["shuttle"]["params"]["diagnostics"]["ranges"] = raw["shuttle"]["params"]["diagnostics"]["ranges"]
    if expected != raw:
        raise ValueError("unexpected profile mutation")
    return result


def clean_session(case, source, sha, *, width, height, count, fps_num, fps_den, has_audio, match_format):
    from bai_engine.schema import MediaInfo, Session, Source, SourceKind
    from bai_engine.schema.session import ParticipantRoster

    sid = {
        "india": "PRODINDIA20261105",
        "denmark": "PRODDENMARK20261105",
        "doubles": "PRODDOUBLES20261105",
        "test7": "PRODTEST720261105",
    }[case]
    return Session(
        session_id=sid,
        title=f"Frozen exposed-data stress: {case}",
        profile="experiment",
        source=Source(kind=SourceKind.UPLOAD, uri=str(source), original_name=source.name, sha256=sha),
        media=MediaInfo(
            fps_num=fps_num,
            fps_den=fps_den,
            n_frames=count,
            width=width,
            height=height,
            duration_us=round(count * fps_den / fps_num * 1e6),
            has_audio=has_audio,
        ),
        players=[],
        roster=ParticipantRoster(match_format=match_format),
        meta={},
    ).model_dump(mode="json")


def verify_inputs(plan):
    for path, expected in {**plan["source_files_sha256"], **plan["input_files_sha256"]}.items():
        if digest(Path(path)) != expected:
            raise ValueError(f"frozen source/input changed: {path}")


def prepare(materials: Path, profile_source: Path, output: Path):
    output = validate_output(output, [ROOT])
    evidence = json.loads(materials.read_text())
    profile = passive_profile(yaml.safe_load(profile_source.read_text()))
    output.mkdir(parents=True, exist_ok=False)
    (output / "profiles").mkdir()
    (output / "empty_catalogue").mkdir()
    profile_path = output / "profiles/experiment.yaml"
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=False))
    inputs = {str(profile_path): digest(profile_path)}
    for model_metadata in [ROOT / "models/manifest.yaml", ROOT / "models/cache/lock.json"]:
        inputs[str(model_metadata)] = digest(model_metadata)
    cases = {}
    for entry in evidence["additional_available_materials"]:
        name = entry["recording"]
        source = ROOT / entry["proxy"]["path"]
        if digest(source) != entry["proxy"]["sha256"]:
            raise ValueError("prepared proxy hash mismatch")
        header = entry["proxy_header_probe"]["streams"][0]
        fps_num, fps_den = map(int, header["avg_frame_rate"].split("/"))
        count = int(header["nb_frames"])
        raw = clean_session(
            name,
            source.resolve(),
            entry["proxy"]["sha256"],
            width=1280,
            height=720,
            count=count,
            fps_num=fps_num,
            fps_den=fps_den,
            has_audio=False,
            match_format="doubles" if name == "doubles" else "singles",
        )
        path = output / f"{name}_session.json"
        dump_new(path, raw)
        inputs.update({str(source.resolve()): digest(source), str(path): digest(path)})
        cases[name] = {
            "kind": "prepared_clip",
            "session": str(path),
            "source": str(source.resolve()),
            "source_sha256": entry["proxy"]["sha256"],
            "frames": count,
        }
    test7 = evidence["test7"]["source"]
    video = ROOT / test7["path"]
    if digest(video) != test7["sha256"]:
        raise ValueError("Test7 source hash mismatch")
    stream = next(s for s in test7["probe"]["streams"] if s["codec_type"] == "video")
    numerator, denominator = map(int, stream["avg_frame_rate"].split("/"))
    raw = clean_session(
        "test7",
        video.resolve(),
        test7["sha256"],
        width=stream["width"],
        height=stream["height"],
        count=int(stream["nb_frames"]),
        fps_num=numerator,
        fps_den=denominator,
        has_audio=any(s["codec_type"] == "audio" for s in test7["probe"]["streams"]),
        match_format="singles",
    )
    path = output / "test7_session.json"
    dump_new(path, raw)
    inputs.update({str(video.resolve()): digest(video), str(path): digest(path)})
    cases["test7"] = {
        "kind": "production_upload",
        "session": str(path),
        "source": str(video.resolve()),
        "source_sha256": test7["sha256"],
        "frames": int(stream["nb_frames"]),
    }
    snapshots = {}
    for source in source_files():
        destination = output / "executed_source" / source.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
        snapshots[str(source)] = digest(source)
    plan = {
        "schema": "production-external-input-plan:v1",
        "root": str(output),
        "cases": cases,
        "source_files_sha256": snapshots,
        "input_files_sha256": inputs,
        "profile_source_sha256": digest(profile_source),
        "profile_source": str(profile_source),
        "profile_mutation": "diagnostics.ranges=[] only; passive telemetry range, no threshold/precision change",
        "warm_start_scope": "each uploaded clip only; Test7 full upload; no prior calibration/identity/reviews",
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "accuracy_claim_eligible": False,
    }
    dump_new(output / "plan.json", plan)
    dump_new(
        output / "outer_provenance.json",
        {
            "materials_path": str(materials),
            "materials_sha256": digest(materials),
            "profile_source": str(profile_source),
            "original_source_crop_and_reference_metadata": evidence,
            "note": "evaluation-only provenance; worker plan and session contain no label paths/values",
        },
    )
    verify_inputs(plan)
    return plan


def command_for(plan, case, output):
    item, prepared = plan["cases"][case], Path(plan["root"])
    if item["kind"] == "production_upload":
        return [
            sys.executable,
            str(Path(__file__).resolve()),
            "test7-worker",
            "--plan",
            str(prepared / "plan.json"),
            "--output",
            str(output),
        ]
    return [
        sys.executable,
        str(ROOT / "research/validate_real_video_runtime.py"),
        "--data-dir",
        str(prepared / "empty_catalogue"),
        "--session-json",
        item["session"],
        "--proxy-path",
        item["source"],
        "--models-dir",
        str(ROOT / "models"),
        "--profiles-dir",
        str(prepared / "profiles"),
        "--profile",
        "experiment",
        "--samples",
        "1",
        "--retain-perception",
        "--output-dir",
        str(output),
    ]


def verify_models(report):
    checked = {}
    for record in report.get("artifacts", {}).values():
        if record.get("status") == "verified_copy":
            path = Path(record["source_path"])
            actual = digest(path)
            if actual != record["sha256"]:
                raise ValueError(f"source model artifact changed: {path}")
            checked[str(path)] = actual
    return checked


@contextlib.contextmanager
def managed_process(command, **kwargs):
    """Cancellation terminates only this worker's new process group, then reaps."""
    process = subprocess.Popen(command, start_new_session=True, **kwargs)
    previous = signal.getsignal(signal.SIGTERM)

    def stop(_signal, _frame):
        raise KeyboardInterrupt("requested stress worker termination")

    signal.signal(signal.SIGTERM, stop)
    try:
        yield process
    finally:
        signal.signal(signal.SIGTERM, previous)
        if process.poll() is None:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(process.pid, signal.SIGKILL)
                process.wait()


def run(plan_path, case, output, gpu_index):
    plan = json.loads(plan_path.read_text())
    output = validate_output(output, [ROOT, Path(plan["root"])])
    verify_inputs(plan)
    output.parent.mkdir(parents=True, exist_ok=True)
    command = command_for(plan, case, output)
    allocated = gpu_uuid(gpu_index)
    environment = os.environ.copy()
    environment["CUDA_VISIBLE_DEVICES"] = allocated
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    outer = {
        "status": "running",
        "case": case,
        "plan_sha256": digest(plan_path),
        "command": command,
        "physical_gpu_index": gpu_index,
        "allocated_gpu_uuid": allocated,
        "cuda_visible_devices": allocated,
        "mode": "fresh exposed-data stress; no GT worker argument; not blind evaluation",
        "started_s": time.time(),
    }
    with gpu_lease(ROOT / "artifacts/benchmarking/experiments/.gpu_leases", allocated):
        with output.with_suffix(".execution.log").open("x") as log:
            started = time.monotonic()
            with managed_process(command, cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT) as process:
                outer["worker_pid"] = process.pid
                with output.with_suffix(".gpu_process_samples.jsonl").open("x") as samples:
                    while process.poll() is None:
                        try:
                            rows = subprocess.check_output(
                                [
                                    "nvidia-smi",
                                    "--query-compute-apps=gpu_uuid,pid,used_memory",
                                    "--format=csv,noheader,nounits",
                                ],
                                text=True,
                                timeout=5,
                            )
                            samples.write(json.dumps({"elapsed_s": time.monotonic() - started, "rows": rows}) + "\n")
                            samples.flush()
                        except (OSError, subprocess.SubprocessError) as error:
                            samples.write(json.dumps({"sampling_error": type(error).__name__}) + "\n")
                        time.sleep(2)
            outer["worker_exit_code"] = process.wait()
            outer["elapsed_s"] = time.monotonic() - started
        try:
            verify_inputs(plan)
            outer["frozen_source_inputs_unchanged"] = True
            outer["status"] = "completed" if process.returncode == 0 else "partial_or_failed"
        except ValueError as error:
            outer.update(status="failed_source_guard", error=str(error), frozen_source_inputs_unchanged=False)
        if case == "test7":
            try:
                details = json.loads((output / "inference.json").read_text())
                outer["output_proxy_sha256"] = details["proxy_sha256"]
                outer["worker_report_sha256"] = digest(output / "inference.json")
                outer["verified_source_models_post"] = verify_models(details["models"])
                if process.returncode == 0:
                    item = plan["cases"][case]
                    if (
                        details.get("status") != "completed"
                        or details.get("frames_processed") != item["frames"]
                        or details.get("cached_perception_used") is not False
                        or details.get("source_sha256") != item["source_sha256"]
                    ):
                        raise ValueError("completed full worker lacks exact fresh source/frame bindings")
                    proxy = output / "data/media" / item["source_sha256"] / "proxy.mp4"
                    if digest(proxy) != details["proxy_sha256"]:
                        raise ValueError("completed worker proxy bytes changed")
                    sid = json.loads(Path(item["session"]).read_text())["session_id"]
                    catalog = verify_perception_catalog(
                        output,
                        details.get("perception_cache_catalog"),
                        session_id=sid,
                        source_sha256=item["source_sha256"],
                        proxy_sha256=details["proxy_sha256"],
                        media=details["media"],
                    )
                    outer["perception_cache_catalog_verification"] = {
                        "status": "verified",
                        "phase": "after_worker_close_before_parent_completion_receipt",
                        "catalog_sha256": details["perception_cache_catalog"]["sha256"],
                        "files": catalog["file_count"],
                        "frames": catalog["frame_count"],
                    }
            except (OSError, KeyError, TypeError, ValueError) as error:
                outer["perception_cache_catalog_verification"] = {"status": "failed", "error": str(error)}
                if outer["status"] == "completed":
                    outer["status"] = "failed_cache_catalog_guard"
        elif output.exists():
            sid = json.loads(Path(plan["cases"][case]["session"]).read_text())["session_id"]
            report = output / "results" / sid / "report.json"
            if report.exists():
                details = json.loads(report.read_text())
                outer["output_proxy_sha256"] = details.get("media", {}).get("proxy_sha256")
                outer["worker_report_sha256"] = digest(report)
                outer["frames_processed"] = details.get("frames_processed")
                manifest = json.loads((output / "run.json").read_text())
                outer["verified_source_models_post"] = verify_models(manifest["models"])
                if process.returncode == 0 and (
                    details.get("frames_processed") != plan["cases"][case]["frames"]
                    or details.get("prefix_truncated") is not False
                    or details.get("cached_perception_used") is not False
                ):
                    raise ValueError("completed worker must cover the entire fresh source")
        dump_new(output.with_suffix(".executor.json"), outer)
    return 0 if outer["status"] == "completed" else process.returncode or 1


def require_complete(session, expected_frames):
    from bai_engine.schema import SessionStatus

    if session is None or session.status is not SessionStatus.ANALYSED or session.media is None:
        raise RuntimeError("production analysis did not complete")
    if session.media.n_frames != expected_frames or session.frontier_frame != expected_frames - 1:
        raise RuntimeError("full dynamic source frame count/frontier mismatch")


def test7_worker(plan_path: Path, output: Path):
    """Generic full-upload SessionRunner use; no reference/evaluator is loaded."""
    import resource

    from bai_engine.bus import LocalBus
    from bai_engine.config import Settings, load_profile
    from bai_engine.runtime.runner import SessionRunner
    from bai_engine.schema import Session
    from bai_engine.store import SessionRepository
    from research.validate_real_video_runtime import offline_network, prepare_models
    from scripts.benchmarking.evaluate_rallies import write_predictions

    plan = json.loads(plan_path.read_text())
    item = plan["cases"]["test7"]
    verify_inputs(plan)
    output = validate_output(output, [ROOT, Path(plan["root"])])
    output.mkdir(parents=True, exist_ok=False)
    profile = load_profile("experiment", Path(plan["root"]) / "profiles")
    registry, artifacts = prepare_models(ROOT / "models", output / "models", [profile])
    repo = SessionRepository(output / "data")
    session = Session.model_validate_json(Path(item["session"]).read_bytes())
    # Let the existing media subsystem derive canonical proxy properties.
    session = session.model_copy(update={"media": None})
    repo.save(session)
    settings = Settings(
        _env_file=None,
        data_dir=output / "data",
        models_dir=output / "models",
        profiles_dir=Path(plan["root"]) / "profiles",
        profile="experiment",
        proxy_height=720,
    )
    bus = LocalBus()
    runner = SessionRunner(session.session_id, repo, bus, settings, registry)
    started = time.monotonic()
    try:
        media_started = time.monotonic()
        # SessionRunner injects its staged registry through the current plugin API.
        with offline_network():
            runner._ensure_media()
            media_seconds = time.monotonic() - media_started
            runner._analyse()
        if runner._transcode_thread:
            runner._transcode_thread.join(timeout=60)
            if runner._transcode_thread.is_alive():
                raise RuntimeError("media process still running")
        final = repo.get(session.session_id)
        require_complete(final, item["frames"])
        events = repo.events(session.session_id).query()
        ends = sorted((e for e in events if e.type == "rally_end"), key=lambda e: (e.frame_start, e.frame_end))
        write_predictions(
            output / "predicted_rallies.csv", [(e.frame_start, e.frame_end) for e in ends], float(final.media.fps)
        )
        with (output / "events.jsonl").open("x") as stream:
            for event in repo.events(session.session_id).query(live_only=False):
                stream.write(event.model_dump_json() + "\n")
        dump_new(output / "session.json", final.model_dump(mode="json"))
        import torch

        proxy = repo.media_paths(item["source_sha256"]).proxy
        result = {
            "status": "completed",
            "mode": "fresh generic full-upload SessionRunner; no labels consumed",
            "elapsed_s": time.monotonic() - started,
            "media_ready_s": media_seconds,
            "media": final.media.model_dump(mode="json"),
            "frontier_frame": final.frontier_frame,
            "frames_processed": final.media.n_frames,
            "cached_perception_used": False,
            "profile": profile.model_dump(mode="json"),
            "models": artifacts,
            "execution_backends": runner.sport.perception.runtimes,
            "degraded": runner.sport.degraded(),
            "perception_stage_seconds": runner.sport.perception.stats.seconds,
            "event_counts": dict(collections.Counter(e.type for e in events)),
            "proxy_sha256": digest(proxy),
            "source_sha256": digest(Path(item["source"])),
            "worker_cpu_s": resource.getrusage(resource.RUSAGE_SELF).ru_utime
            + resource.getrusage(resource.RUSAGE_SELF).ru_stime,
            "worker_maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "visible_torch_devices": [
                {
                    "logical_index": i,
                    "name": torch.cuda.get_device_properties(i).name,
                    "uuid": str(torch.cuda.get_device_properties(i).uuid),
                }
                for i in range(torch.cuda.device_count())
            ],
            "runtime_scope": (
                "worker CPU/RSS; perception stage scopes overlap; GPU PID samples external; "
                "no target-hardware/generalization claim"
            ),
        }
        cache_started = time.monotonic()
        result["perception_cache_catalog"] = write_perception_catalog(
            output,
            session_id=final.session_id,
            source_sha256=result["source_sha256"],
            proxy_sha256=result["proxy_sha256"],
            media=result["media"],
        )
        result["perception_cache_catalog_seconds"] = time.monotonic() - cache_started
        verify_inputs(plan)
        result.update(
            elapsed_s=time.monotonic() - started,
            worker_cpu_s=resource.getrusage(resource.RUSAGE_SELF).ru_utime
            + resource.getrusage(resource.RUSAGE_SELF).ru_stime,
            worker_maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        )
        dump_new(output / "inference.json", result)
    finally:
        runner.stop()
        if runner._transcode_thread:
            runner._transcode_thread.join(timeout=10)
        if runner.sport:
            runner.sport.close()
        bus.close()
        repo.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--materials", type=Path, required=True)
    p.add_argument("--profile-source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    for name in ["run", "test7-worker"]:
        p = sub.add_parser(name)
        p.add_argument("--plan", type=Path, required=True)
        p.add_argument("--output", type=Path, required=True)
        if name == "run":
            p.add_argument("--case", choices=["india", "denmark", "doubles", "test7"], required=True)
            p.add_argument("--gpu-index", type=int, required=True)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare(args.materials.resolve(), args.profile_source.resolve(), args.output.resolve())
    elif args.action == "run":
        raise SystemExit(run(args.plan.resolve(), args.case, args.output.resolve(), args.gpu_index))
    else:
        test7_worker(args.plan.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
