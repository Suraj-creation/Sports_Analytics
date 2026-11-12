"""Independently verify a closed fresh run after the known codec21 catalogue failure.

This tool performs no neural inference, event replay, prediction correction or
annotation evaluation. It never writes into the failed original run. Lost worker
measurements remain unavailable; a new post-hoc receipt is explicitly separate.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import shutil
import sqlite3
import sys
import tempfile
import types
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def digest(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"regular nonsymlink file required: {path}")
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_new(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def validate_failure(receipt, log, *, plan_path, run, case):
    expected = [
        str(ROOT / "research/production_external_stress.py"),
        "upload-worker",
        "--case",
        case,
        "--plan",
        str(plan_path),
        "--output",
        str(run),
    ]
    if (
        receipt.get("status") != "partial_or_failed"
        or receipt.get("worker_exit_code") != 1
        or receipt.get("frozen_source_inputs_unchanged") is not True
        or receipt.get("case") != case
        or receipt.get("plan_sha256") != digest(plan_path)
        or receipt.get("command", [])[1:] != expected
    ):
        raise ValueError("original failure receipt does not bind this frozen fresh worker")
    terminal = "ValueError: invalid bounded cache header/frames: seg_00000.msgpack: unsupported cache codec version"
    if (
        not log.rstrip().endswith(terminal)
        or log.count("Traceback (most recent call last):") != 2
        or "in upload_worker" not in log
        or "in write_perception_catalog" not in log
        or "in perception_catalog" not in log
        or "ValueError: unsupported cache codec version" not in log
    ):
        raise ValueError("only the known post-analysis codec catalogue failure is recoverable")


def copied_sql_rows(path, query, params=()):
    """Query a detached database/WAL copy; SQLite cannot mutate original files."""
    digest(path)
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / path.name
        shutil.copyfile(path, target)
        for suffix in ("-wal", "-shm"):
            side = path.with_name(path.name + suffix)
            if side.exists():
                digest(side)
                shutil.copyfile(side, target.with_name(target.name + suffix))
        with sqlite3.connect(target) as connection:
            return connection.execute(query, params).fetchall()


def _validate_cache_context(payload, profile, media, *, accepted_versions=(21,), context_label="codec21"):
    import msgpack

    from bai_badminton.plugin import BadmintonSession

    value = msgpack.unpackb(payload, raw=False)
    identity = value.get("ci")
    if (
        value.get("v") not in accepted_versions
        or not isinstance(identity, dict)
        or identity.get("profile") != profile
        or identity.get("loaded_models") != value.get("models")
        or identity.get("frame_size") != [media["width"], media["height"]]
        or identity.get("fps") != media["fps_num"] / media["fps_den"]
    ):
        raise ValueError(f"{context_label} source profile/model/media identity mismatch")
    for group in ("components", "domain_components"):
        for kind, metadata in identity.get(group, {}).items():
            configuration = metadata.get("configuration")
            choice = profile.get("components", {}).get(kind, profile.get(kind))
            if choice is not None and configuration != choice:
                raise ValueError(f"cache component configuration mismatch: {kind}")
    # Actual production decoder validates every association, diagnostic, current
    # layout decision, raw link, detector model/shape/IoU and pose/racket source.
    receiver = SimpleNamespace(perception=SimpleNamespace(ref_id=value.get("cr")), _isolation_id=lambda: identity)
    decoded = BadmintonSession.decode_perception(receiver, payload, diagnostic=True)
    return value, decoded


def validate_cache21(payload, profile, media):
    """Historical recovery contract stays strictly codec21, without header rewriting."""
    return _validate_cache_context(payload, profile, media, accepted_versions=(21,))


def validate_completed_cache(payload, profile, media):
    """Normal completed-run schema validation; no recovery or neural execution."""
    return _validate_cache_context(
        payload, profile, media, accepted_versions=(21, 22, 23, 24), context_label="completed codec21/22/23/24"
    )


def cache_catalog(run, *, session_id, source_sha256, proxy_sha256, media, profile):
    from research import production_external_stress as original

    # Reuse the exact frozen header/extent/size guards in isolated globals. The
    # independent recovery policy accepts ONLY21; original module stays intact.
    limits = {**original.PERCEPTION_CATALOG_LIMITS, "accepted_codec_versions": [21]}
    globals_copy = {**original.perception_catalog.__globals__, "PERCEPTION_CATALOG_LIMITS": limits}
    check = types.FunctionType(original.perception_catalog.__code__, globals_copy)
    catalog = check(run, session_id=session_id, source_sha256=source_sha256, proxy_sha256=proxy_sha256, media=media)
    declarations, decisions, counts = {}, {}, collections.Counter()
    for entry in catalog["files"]:
        path = run / entry["path"]
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
            raise ValueError("cache changed before strict codec validation")
        value, decoded = validate_cache21(payload, profile, media)
        identity = value["ci"]
        for kind in ["loaded_models", "runtimes", "components", "domain_components"]:
            record = identity.get(kind, {})
            key = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
            declarations.setdefault(kind, {})[key] = record
        for frame in decoded.frames:
            counts["frames_strictly_decoded"] += 1
            if frame.content_decision is not None:
                counts["content_decisions"] += 1
                decision = frame.content_decision
                if decision.detector_frame is not None:
                    decisions[decision.detector_frame] = (decision.detector_image_sha256, decision.detector_image_shape)
    if counts["frames_strictly_decoded"] != media["n_frames"]:
        raise ValueError("strict decode missed source frames")
    catalog.update(
        schema="posthoc-analysis-cache-catalog:v1",
        snapshot_stage="independent_readonly_verification_after_failed_worker_close",
        scope="posthoc codec21 complete source-bound observations; original publication failed",
    )
    return catalog, declarations, decisions, dict(counts)


def decode_source_pts(source, media):
    import av

    times, rows = [], []
    with av.open(str(source)) as container:
        stream = container.streams.video[0]
        stream.thread_type = "AUTO"
        stream.codec_context.thread_count = 2
        for frame_index, frame in enumerate(container.decode(stream)):
            if frame.pts is None:
                raise ValueError("source presentation timestamp unavailable")
            time = Fraction(frame.pts) * frame.time_base
            if times and time != times[0] + Fraction(frame_index * media["fps_den"], media["fps_num"]):
                raise ValueError("source is not exact canonical-rate CFR")
            times.append(time)
            rows.append([frame_index, frame.pts, frame.time_base.numerator, frame.time_base.denominator])
    if len(times) != media["n_frames"]:
        raise ValueError("source full decoded frame population mismatch")
    return times, rows


def verify_proxy(proxy, media, decisions, source_times):
    import av

    found, count, origin = set(), 0, None
    with av.open(str(proxy)) as container:
        stream = container.streams.video[0]
        stream.thread_type = "AUTO"
        stream.codec_context.thread_count = 2
        for index, frame in enumerate(container.decode(stream)):
            if (frame.width, frame.height) != (media["width"], media["height"]):
                raise ValueError("proxy decoded dimensions disagree with canonical media")
            if frame.pts is None:
                raise ValueError("proxy presentation timestamp unavailable")
            time = Fraction(frame.pts) * frame.time_base
            if origin is None:
                origin = time
            if (
                time != origin + Fraction(index * media["fps_den"], media["fps_num"])
                or index >= len(source_times)
                or time != source_times[index]
            ):
                raise ValueError("source/proxy full rational presentation timestamps disagree")
            if index in decisions:
                expected, shape = decisions[index]
                pixels = frame.to_ndarray(format="bgr24")
                if tuple(pixels.shape) != tuple(shape) or hashlib.sha256(pixels.tobytes()).hexdigest() != expected:
                    raise ValueError("scene decision image hash differs from actual decoded source pixels")
                found.add(index)
            count = index + 1
    if count != media["n_frames"] or found != set(decisions):
        raise ValueError("proxy decode/tail/decision-frame population mismatch")
    return {
        "frames_decoded": count,
        "exact_pts_frames": count,
        "scene_image_hashes_verified": len(found),
        "decoder": "PyAV BGR24, CPU2threads; no neural execution",
        "source_proxy_full_rational_pts_equal": True,
        "origin_rational_seconds": str(origin),
    }


def validate_predictions(path, live_events, fps):
    from scripts.benchmarking.evaluate_rallies import write_predictions

    ends = sorted((e for e in live_events if e.type == "rally_end"), key=lambda e: (e.frame_start, e.frame_end))
    with tempfile.TemporaryDirectory() as directory:
        expected = Path(directory) / "comparison_only.csv"
        write_predictions(expected, [(e.frame_start, e.frame_end) for e in ends], fps)
        if expected.read_bytes() != path.read_bytes():
            raise ValueError("existing predictions are not exact unchanged export of ALL live rally_end events")
    return {
        "rally_end_count": len(ends),
        "prediction_sha256": digest(path),
        "scope": "byte comparison only; no new predictions or reconstructed intervals published",
    }


def verify_archive_extraction(archive, extraction):
    """Bind actual extracted graphs to bytes inside the pinned source archive."""
    import zipfile

    record = json.loads((extraction / "manifest.json").read_text())
    if (
        record.get("schema") != "verified-archive-extraction-v1"
        or record.get("archive_sha256") != digest(archive)
        or record.get("graph") not in record.get("files", {})
        or not record["graph"].endswith(".onnx")
    ):
        raise ValueError("extracted model provenance differs from its verified archive")
    with zipfile.ZipFile(archive) as source:
        names = {info.filename for info in source.infolist() if not info.is_dir()}
        if names != set(record["files"]):
            raise ValueError("extracted model archive file population differs")
        for name, expected in record["files"].items():
            relative = Path(name)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("archive extraction path escape")
            with source.open(name) as stream:
                archive_hash = hashlib.file_digest(stream, "sha256").hexdigest()
            if archive_hash != expected or digest(extraction / "files" / relative) != expected:
                raise ValueError("extracted model graph/data bytes differ from the pinned archive")


def verify_models(run, declarations, profile):
    if len(declarations.get("loaded_models", {})) != 1:
        raise ValueError("loaded-model declarations must remain identical across the full source run")
    import importlib.util

    import yaml

    from bai_engine.config import Profile
    from research.validate_real_video_runtime import effective_model_choices

    manifest_path = ROOT / "models/manifest.yaml"
    if digest(run / "models/manifest.yaml") != digest(manifest_path):
        raise ValueError("staged model manifest differs from frozen original")
    pins = json.loads((ROOT / "models/cache/lock.json").read_text())
    if json.loads((run / "models/cache/lock.json").read_text()) != pins:
        raise ValueError("staged model pins differ from original")
    manifest = yaml.safe_load(manifest_path.read_text())["models"]
    names = {
        c.model
        for c in effective_model_choices(Profile.model_validate(profile)).values()
        if c is not None and c.model != "none" and c.backend != "none"
    }
    result = {"registry_artifacts": {}, "package_ocr_artifacts": {}}
    loaded = next(iter(declarations["loaded_models"].values()))
    for name in sorted(names):
        spec = manifest.get(name)
        if spec is None or spec["format"] in {"builtin", "package"}:
            continue
        filename = Path(spec.get("source", {}).get("file") or spec.get("source", {}).get("url", name)).name
        source, staged = ROOT / "models/cache" / name / filename, run / "models/cache" / name / filename
        expected = spec.get("sha256")
        if expected in (None, "pin-on-first-fetch"):
            expected = pins.get(name)
        if not staged.exists() or not source.exists():
            if any(value.startswith(name + "@") for value in loaded.values()):
                raise ValueError("loaded model lacks actual staged/original bytes")
            result["registry_artifacts"][name] = {"status": "unavailable_not_claimed_loaded"}
            continue
        if not expected or digest(source) != expected or digest(staged) != expected:
            raise ValueError("staged/source model differs from frozen integrity pin")
        if staged.suffix == ".zip":
            extractions = list((staged.parent / "extracted-v1").glob("*/manifest.json"))
            if len(extractions) != 1:
                raise ValueError("loaded archive model needs one actual verified extraction")
            verify_archive_extraction(staged, extractions[0].parent)
        result["registry_artifacts"][name] = {
            "sha256": expected,
            "source_path": str(source),
            "staged_path": str(staged),
        }
    package_root = Path(importlib.util.find_spec("rapidocr").origin).parent
    for runtime in declarations["runtimes"].values():
        for stage, spec in runtime.get("ocr", {}).get("stages", {}).items():
            paths = list(package_root.rglob(spec["model_file"]))
            if len(paths) != 1 or digest(paths[0]) != spec["sha256"]:
                raise ValueError("package OCR model differs from recorded actual runtime")
            result["package_ocr_artifacts"][stage] = {"path": str(paths[0]), "sha256": spec["sha256"]}
    return result


def verify_frozen_plan(plan, *, current_source_guard):
    """Post-close consumers bind original snapshots even after later code edits."""
    if current_source_guard:
        from research.production_external_stress import verify_inputs

        verify_inputs(plan)
    for path, expected in plan["input_files_sha256"].items():
        if digest(path) != expected:
            raise ValueError("frozen input/configuration changed")
    snapshots = Path(plan["root"]) / "executed_source"
    for path, expected in plan["source_files_sha256"].items():
        relative = Path(path).relative_to(ROOT)
        if digest(snapshots / relative) != expected:
            raise ValueError("frozen executed source snapshot changed")


def collect(plan_path, run, case, *, current_source_guard=True):
    from bai_engine.config import load_profile
    from bai_engine.schema import Event, Session, SessionStatus
    from bai_engine.schema.events import current_view
    from research.pipeline_repair_performance import summarize_stage_samples

    plan_path, run = Path(plan_path).resolve(strict=True), Path(run).resolve(strict=True)
    if run.is_symlink() or not run.is_dir():
        raise ValueError("original run must be a nonsymlink existing directory")
    receipt_path, log_path = run.with_suffix(".executor.json"), run.with_suffix(".execution.log")
    receipt = json.loads(receipt_path.read_text())
    validate_failure(receipt, log_path.read_text(), plan_path=plan_path, run=run, case=case)
    if (run / "inference.json").exists():
        raise ValueError("worker inference report exists; this narrow recovery is not applicable")
    plan = json.loads(plan_path.read_text())
    verify_frozen_plan(plan, current_source_guard=current_source_guard)
    item = plan["cases"][case]
    prepared = json.loads(Path(item["session"]).read_text())
    session = Session.model_validate_json((run / "session.json").read_bytes())
    sid = session.session_id
    if (
        item["kind"] != "production_upload"
        or sid != prepared["session_id"]
        or session.status is not SessionStatus.ANALYSED
        or session.media is None
        or session.media.n_frames != item["frames"]
        or session.frontier_frame != item["frames"] - 1
        or session.analysed_frames != item["frames"]
        or session.source != Session.model_validate(prepared).source
    ):
        raise ValueError("actual completed session/source/frontier does not match frozen complete upload")
    media = session.media.model_dump(mode="json")
    if media["variable_frame_rate"]:
        raise ValueError("independent recovery requires verified unchanged CFR")
    database = run / "data/sessions.sqlite"
    rows = copied_sql_rows(database, "SELECT body FROM sessions WHERE session_id=?", (sid,))
    if len(rows) != 1 or Session.model_validate_json(rows[0][0]) != session:
        raise ValueError("exported session disagrees with committed actual session database")
    event_database = run / "data/sessions" / sid / "events.sqlite"
    rows = copied_sql_rows(event_database, "SELECT seq,body FROM events ORDER BY seq")
    database_events = [Event.model_validate_json(body).with_seq(seq) for seq, body in rows]
    source_events = [Event.model_validate_json(line) for line in (run / "events.jsonl").open() if line.strip()]
    if {e.event_id: e for e in source_events} != {e.event_id: e for e in database_events} or len(source_events) != len(
        database_events
    ):
        raise ValueError("exported event ledger disagrees with actual committed database")
    live_events = current_view(database_events)
    prediction = validate_predictions(run / "predicted_rallies.csv", live_events, float(session.media.fps))
    source, proxy = Path(item["source"]), run / "data/media" / item["source_sha256"] / "proxy.mp4"
    if digest(source) != item["source_sha256"]:
        raise ValueError("original video bytes differ from frozen source")
    proxy_sha256 = digest(proxy)
    profile = load_profile("experiment", Path(plan["root"]) / "profiles").model_dump(mode="json")
    catalog, declarations, decisions, counts = cache_catalog(
        run,
        session_id=sid,
        source_sha256=item["source_sha256"],
        proxy_sha256=proxy_sha256,
        media=media,
        profile=profile,
    )
    models = verify_models(run, declarations, profile)
    source_times, source_pts = decode_source_pts(source, media)
    pixels = verify_proxy(proxy, media, decisions, source_times)
    stages_path = run / "stage_latency_samples.json"
    stages = json.loads(stages_path.read_text())
    stage_summary = summarize_stage_samples(stages)
    if any(stage not in stages or not stages[stage] for stage in ["shuttle", "players", "ocr"]):
        raise ValueError("required original neural stage measurements missing")
    bindings = {
        str(p): digest(p)
        for p in [
            plan_path,
            receipt_path,
            log_path,
            run / "session.json",
            run / "events.jsonl",
            run / "predicted_rallies.csv",
            stages_path,
            source,
            proxy,
            database,
            event_database,
        ]
    }
    verify_frozen_plan(plan, current_source_guard=current_source_guard)
    for entry in catalog["files"]:
        if digest(run / entry["path"]) != entry["sha256"]:
            raise ValueError("cache changed during independent recovery")
    for path, expected in bindings.items():
        if digest(path) != expected:
            raise ValueError("original completion input changed during independent recovery")
    result = {
        "schema": "independent-analysis-completion-recovery:v1",
        "status": "analysis_artifacts_verified_after_catalog_publication_failure",
        "mode": "posthoc readonly finalization proof; NO new inference/replay/prediction edits/GT evaluation",
        "original_run": str(run),
        "original_parent_status": receipt["status"],
        "original_parent_receipt": receipt,
        "original_worker_exit_code": receipt["worker_exit_code"],
        "session_id": sid,
        "media": media,
        "frames_processed": media["n_frames"],
        "frontier_frame": session.frontier_frame,
        "event_counts": dict(collections.Counter(e.type for e in live_events)),
        "source_sha256": item["source_sha256"],
        "proxy_sha256": proxy_sha256,
        "profile": profile,
        "frames_verified": counts,
        "proxy_pixel_and_pts_verification": pixels,
        "source_pts_rows": source_pts,
        "source_pts_row_schema": ["source_frame", "pts", "time_base_num", "time_base_den"],
        "prediction_export_verification": prediction,
        "declarations_from_actual_cache_identities": declarations,
        "models_verified_posthoc": models,
        "original_stage_samples_sha256": bindings[str(stages_path)],
        "stage_samples_summary": stage_summary,
        "original_session_degraded": session.meta.get("degraded", []),
        "input_sha256": bindings,
        "frozen_source_inputs_verified": True,
        "fresh_nn_evidence_scope": (
            "Frozen original worker required sequential fresh perception; actual completed session, full codec21 "
            "observations, neural-stage samples and original GPU execution receipt support complete fresh execution. "
            "This tool performs no neural calls and does not recreate the lost worker report."
        ),
        "unavailable_lost_worker_fields": [
            "worker elapsed inference duration",
            "model staging/init timings",
            "worker total CPU",
            "worker peak RSS",
            "worker CUDA-device enumeration",
        ],
        "resource_scope": (
            "Original failed-parent elapsed and external PID samples remain separate; stage invocation scopes overlap."
        ),
        "original_artifacts_modified": False,
        "recovery_source_sha256": digest(Path(__file__)),
    }
    return result, catalog


def recover(plan_path, run, case, output):
    run, output = Path(run).resolve(strict=True), Path(output).resolve()
    if output.exists() or output == run or run in output.parents:
        raise ValueError("completion output must be a new directory outside the original run")
    result, catalog = collect(plan_path, run, case)
    output.mkdir(parents=True, exist_ok=False)
    write_new(output / "perception_catalog.json", catalog)
    result["posthoc_catalog_sha256"] = digest(output / "perception_catalog.json")
    write_new(output / "completion_receipt.json", result)
    shutil.copyfile(Path(__file__), output / "executed_recovery_source.py")
    write_new(
        output / "recovery_manifest.json",
        {
            "schema": "independent-analysis-recovery-publication:v1",
            "original_run": str(run),
            "plan_path": str(Path(plan_path).resolve(strict=True)),
            "case": case,
            "artifact_sha256": {
                name: digest(output / name)
                for name in ["completion_receipt.json", "perception_catalog.json", "executed_recovery_source.py"]
            },
        },
    )
    return result


def verify_completion_receipt(run: Path, recovery: Path) -> dict:
    """Strict explicit downstream gate; original default loaders stay unchanged.

    Returns Path objects for file/directory keys and a tuple of input_paths.
    Rechecks the original evidence rather than trusting a new completed flag.
    """
    run, recovery = Path(run).resolve(strict=True), Path(recovery).resolve(strict=True)
    publication_path = recovery / "recovery_manifest.json"
    publication = json.loads(publication_path.read_text())
    if publication.get("schema") != "independent-analysis-recovery-publication:v1" or publication.get(
        "original_run"
    ) != str(run):
        raise ValueError("recovery publication belongs to another run")
    required = {"completion_receipt.json", "perception_catalog.json", "executed_recovery_source.py"}
    if set(publication.get("artifact_sha256", {})) != required:
        raise ValueError("recovery artifact population is incomplete")
    for name, expected in publication["artifact_sha256"].items():
        if digest(recovery / name) != expected:
            raise ValueError("recovery artifact digest mismatch")
    receipt_path = recovery / "completion_receipt.json"
    recorded = json.loads(receipt_path.read_text())
    plan_path = Path(publication["plan_path"])
    verified, catalog = collect(plan_path, run, publication["case"], current_source_guard=False)
    for key, value in verified.items():
        if key != "recovery_source_sha256" and recorded.get(key) != value:
            raise ValueError(f"recovery receipt differs from independently verified source: {key}")
    if recorded.get("recovery_source_sha256") != digest(recovery / "executed_recovery_source.py"):
        raise ValueError("recorded recovery helper identity mismatch")
    if json.loads((recovery / "perception_catalog.json").read_text()) != catalog or recorded.get(
        "posthoc_catalog_sha256"
    ) != digest(recovery / "perception_catalog.json"):
        raise ValueError("posthoc cache catalog does not match complete actual source population")
    plan = json.loads(plan_path.read_text())
    sid = verified["session_id"]
    code_files = {str(Path(path).relative_to(ROOT)): value for path, value in plan["source_files_sha256"].items()}
    snapshots = [Path(plan["root"]) / "executed_source" / name for name in code_files]
    inputs = [Path(path) for path in verified["input_sha256"]]
    inputs += [Path(path) for path in plan["input_files_sha256"]]
    for group in verified["models_verified_posthoc"].values():
        for model in group.values():
            inputs.extend(Path(model[key]) for key in ["source_path", "staged_path", "path"] if key in model)
    for model in verified["models_verified_posthoc"]["registry_artifacts"].values():
        if "staged_path" in model and Path(model["staged_path"]).suffix == ".zip":
            inputs.extend(p for p in (Path(model["staged_path"]).parent / "extracted-v1").rglob("*") if p.is_file())
    inputs += [
        *snapshots,
        publication_path,
        receipt_path,
        recovery / "perception_catalog.json",
        recovery / "executed_recovery_source.py",
    ]
    cache_dir = run / "data/sessions" / sid / "perception"
    caches = {Path(row["path"]).name: row["sha256"] for row in catalog["files"]}
    return {
        "layout": "production-full-upload-posthoc-completion-recovery",
        "media": verified["media"],
        "profile": verified["profile"],
        "session_id": sid,
        "session_path": run / "session.json",
        "events_path": run / "events.jsonl",
        "plan_path": plan_path,
        "manifest_path": plan_path,
        "receipt_path": receipt_path,
        "report_path": receipt_path,
        "cache_dir": cache_dir,
        "cache_directory": cache_dir,
        "cache_sha256": caches,
        "expected_caches": caches,
        "code_files": code_files,
        "code_commit": plan["code_commit"],
        "source_commit": plan["code_commit"],
        "input_paths": tuple(sorted(set(inputs))),
        "source_sha256": verified["source_sha256"],
        "proxy_sha256": verified["proxy_sha256"],
        "prediction_sha256": verified["prediction_export_verification"]["prediction_sha256"],
        "cache_digest_scope": "independent posthoc codec21 catalogue after original failed worker close",
        "cache_catalogue_receipt": {
            "schema": catalog["schema"],
            "path": str(recovery / "perception_catalog.json"),
            "sha256": recorded["posthoc_catalog_sha256"],
            "file_count": catalog["file_count"],
            "frame_count": catalog["frame_count"],
        },
        "original_parent_status": verified["original_parent_status"],
        "completion_receipt": recorded,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["plan", "run", "output"]:
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--case", required=True)
    args = parser.parse_args()
    result = recover(args.plan, args.run, args.case, args.output)
    print(
        json.dumps(
            {
                "status": result["status"],
                "frames": result["frames_verified"],
                "predictions": result["prediction_export_verification"]["rally_end_count"],
            }
        )
    )


if __name__ == "__main__":
    main()
