"""Dynamic external own-cache semantic replay, no NN inference or annotation input.

The default must reproduce its actual finished external run before either
existing provider is tested as a separate one-variable arm.
This uses actual SID/media/configuration and structural decoder contracts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bai_badminton.components import BASELINE_IMPLEMENTATIONS as DOMAIN_BASELINES  # noqa: E402
from bai_badminton.components import DomainContext, register_domain_components  # noqa: E402
from bai_badminton.court import Homography  # noqa: E402
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig  # noqa: E402
from bai_badminton.events.contact import P_MIN, _seg_velocity, score_frame  # noqa: E402
from bai_badminton.participant_geometry import GeometryBracketPolicy  # noqa: E402
from bai_badminton.plugin import BadmintonSession  # noqa: E402
from bai_badminton.rules.bwf import MatchConfig  # noqa: E402
from bai_engine.components import ComponentRegistry  # noqa: E402
from bai_engine.config import ModelChoice, Profile  # noqa: E402
from bai_engine.schema import Session  # noqa: E402
from bai_engine.store import EventStore  # noqa: E402
from research.production_external_reference_report import validate_coverage, validate_finished  # noqa: E402
from research.production_replay_parity_audit import compare_live  # noqa: E402

REPLAY_SCHEMA = "cached-external-semantic:v2"
REPLAY_OUTPUT_ARTIFACTS = (
    "events.jsonl",
    "current-events.jsonl",
    "parity_vs_fresh.json",
    "emission_frontiers.json",
    "contact_readouts.json",
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def replay_output_hashes(output, *, trace):
    """Bind completed diagnostic bytes, excluding the manifest and mutable SQLite."""
    names = (*REPLAY_OUTPUT_ARTIFACTS, "bounded_fsm_trace.jsonl") if trace else REPLAY_OUTPUT_ARTIFACTS
    hashes = {}
    for name in names:
        path = output / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("completed regular replay output artifact required")
        hashes[name] = sha(path)
    return hashes


def capture_core_source_snapshot(expected, output, *, root=ROOT):
    """Archive the exact core bytes before diagnostic execution, never just hashes."""
    if not expected:
        raise ValueError("nonempty executed core source population required")
    for name, digest in expected.items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("core source snapshot requires repository-relative paths")
        data = (root / relative).read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError("core source changed before snapshot capture")
        destination = output / "executed_core_source" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(data)
    return {"directory": "executed_core_source", "sha256": dict(expected)}


def verify_core_source_snapshot(output, receipt):
    if receipt.get("directory") != "executed_core_source" or not receipt.get("sha256"):
        raise ValueError("unsupported or missing core source snapshot receipt")
    for name, digest in receipt["sha256"].items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("core source snapshot path is not relative")
        path = output / receipt["directory"] / relative
        if path.is_symlink() or not path.is_file() or sha(path) != digest:
            raise ValueError("executed core source snapshot bytes changed")


def verify_replay_output_artifacts(output, manifest):
    expected = manifest.get("output_artifact_sha256")
    actual = replay_output_hashes(output, trace=bool(manifest.get("trace_ranges_telemetry_only")))
    if not expected or actual != expected:
        raise ValueError("replay output artifact bytes or population changed")
    if manifest.get("core_source_snapshot") is not None:
        verify_core_source_snapshot(output, manifest["core_source_snapshot"])


def apply_recorded_format(engine, row):
    """Reapply an actual source decision; preserve its producer, never re-infer."""
    from bai_engine.schema import Event

    original = Event.model_validate(row)
    selected = original.payload.get("match_format")
    if original.type != "format_decision" or original.frame_start != original.frame_end:
        raise ValueError("source format decision must be a canonical single-frame event")
    if selected not in ("unknown", "singles", "doubles"):
        raise ValueError("recorded format decision has no supported format")
    engine.set_match_format(
        None if selected == "unknown" else selected,
        original.frame_start,
        original.provenance,
        decision=original.payload.get("decision", {}),
    )


def source_hashes():
    return {
        str(p.relative_to(ROOT)): sha(p)
        for directory in ("engine/src", "sports/badminton/src")
        for p in sorted((ROOT / directory).rglob("*.py"))
    }


def harness_paths():
    return {
        name: ROOT / name
        for name in (
            "research/production_external_semantic_replay.py",
            "research/production_external_reference_report.py",
            "research/production_replay_parity_audit.py",
            "research/production_contact_result_audit.py",
            "research/production_external_stress.py",
        )
    }


def capture_harness_sources(paths=None):
    captured = {name: path.read_bytes() for name, path in (harness_paths() if paths is None else paths).items()}
    return captured, {name: hashlib.sha256(data).hexdigest() for name, data in captured.items()}


def verify_harness_sources(expected, paths=None):
    if capture_harness_sources(paths)[1] != expected:
        raise ValueError("replay runner/helper changed during execution")


def require_baseline_proof(proof, *, report_sha, engine_sources, harness_sources):
    if (
        proof.get("schema") != REPLAY_SCHEMA
        or proof.get("baseline_parity") is not True
        or proof.get("geometry_bracket") is not False
        or proof.get("contact_motion_reliability") is not False
        or proof.get("source_report_sha256") != report_sha
        or proof.get("executed_source_sha256") != engine_sources
        or not harness_sources
        or proof.get("harness_source_sha256") != harness_sources
    ):
        raise ValueError("baseline parity proof is missing or from another runner/helper/source/configuration")


def require_source_intervention(manifest, proof, *, report_sha, proof_sha, current_sources, recorded_sources):
    """Authorize only an explicit, complete source delta after strict baseline parity.

    This is a development experiment with frozen perception, never a fresh run
    or a baseline proof. Default replay remains strict and refuses changed sport
    sources. Model/perception changes still require subsequent fresh inference.
    """
    recorded = {
        name: digest for name, digest in recorded_sources.items() if name.startswith(("engine/src/", "sports/"))
    }
    changes = {
        name: {"recorded": recorded.get(name), "current": current_sources.get(name)}
        for name in sorted(recorded.keys() | current_sources.keys())
        if recorded.get(name) != current_sources.get(name)
    }
    if (
        not changes
        or manifest.get("schema") != "controlled-semantic-source-intervention:v1"
        or manifest.get("source_report_sha256") != report_sha
        or manifest.get("baseline_proof_sha256") != proof_sha
        or manifest.get("executed_source_sha256") != current_sources
        or manifest.get("changes") != changes
        or not isinstance(manifest.get("hypothesis"), str)
        or not manifest["hypothesis"].strip()
    ):
        raise ValueError("source intervention must bind the complete declared code delta and baseline receipt")
    options = manifest.get("rally_evidence_options", {})
    if (
        not isinstance(options, dict)
        or options.keys() - {"use_short_exchange_evidence", "use_terminal_contact_evidence"}
        or any(type(value) is not bool for value in options.values())
    ):
        raise ValueError("controlled rally options require explicit supported boolean evidence policies")
    if (
        proof.get("schema") != REPLAY_SCHEMA
        or proof.get("baseline_parity") is not True
        or proof.get("geometry_bracket") is not False
        or proof.get("contact_motion_reliability") is not False
        or proof.get("source_intervention") is not None
        or proof.get("source_report_sha256") != report_sha
        or not proof.get("harness_source_sha256")
        or any(
            proof.get("executed_source_sha256", {}).get(name) != digest
            for name, digest in recorded.items()
            if name.startswith("sports/")
        )
    ):
        raise ValueError("source intervention requires an unchanged-sport strict baseline parity proof")
    return changes


@dataclass(frozen=True)
class FinishedInput:
    layout: str
    manifest_path: Path
    report_path: Path
    session_path: Path
    events_path: Path
    cache_directory: Path
    media: dict
    profile: dict
    code_files: dict
    source_commit: str
    expected_caches: dict
    cache_digest_scope: str
    input_paths: tuple[Path, ...]
    cache_catalogue_receipt: dict | None = None


def load_finished_input(run, sid, *, completion_recovery: Path | None = None):
    """Read genuine harness or full-upload exports; never fabricate run metadata."""
    if completion_recovery is not None:
        from research.pipeline_repair_completion import verify_completion_receipt

        bound = verify_completion_receipt(run, completion_recovery)
        if read(bound["session_path"])["session_id"] != sid:
            raise ValueError("recovered completion belongs to a different session")
        return FinishedInput(**{name: bound[name] for name in FinishedInput.__dataclass_fields__})
    if (run / "run.json").is_file():
        manifest_path, report_path = run / "run.json", run / "results" / sid / "report.json"
        manifest, report = read(manifest_path), read(report_path)
        media = report["media"]["canonical"]
        expected = {
            **media,
            "media_n_frames": media["n_frames"],
            "media_sha256": report["media"]["source_sha256"],
            "proxy_sha256": report["media"]["proxy_sha256"],
        }
        validate_finished(manifest, report, sid, expected)
        directory = run / "results" / sid
        validate_coverage(directory / "frame-coverage.jsonl", media["n_frames"])
        for name, digest in report["artifact_hashes"].items():
            if sha(directory / name) != digest:
                raise ValueError("changed completed source artifact")
        return FinishedInput(
            "fresh-real-video-harness",
            manifest_path,
            report_path,
            directory / "session.json",
            directory / "events.jsonl",
            directory / "perception",
            media,
            report["profile"],
            manifest["code"]["files"],
            manifest["code"]["git_commit"],
            {Path(item["path"]).name: item["sha256"] for item in report["perception_retention"]["chunks"]},
            "hash catalogue retained during original inference",
            (manifest_path, report_path),
        )
    report_path, executor_path = run / "inference.json", run.with_suffix(".executor.json")
    info, executor = read(report_path), read(executor_path)
    if (
        info.get("status") != "completed"
        or executor.get("status") != "completed"
        or executor.get("worker_exit_code") != 0
        or executor.get("frozen_source_inputs_unchanged") is not True
        or not isinstance(executor.get("case"), str)
        or info.get("cached_perception_used") is not False
    ):
        raise ValueError("finished source-guarded full-upload worker required")
    if sha(report_path) != executor.get("worker_report_sha256"):
        raise ValueError("full-upload worker report digest changed or missing")
    command = executor["command"]
    if command.count("--plan") != 1:
        raise ValueError("explicit recorded full-upload plan required")
    plan_path = Path(command[command.index("--plan") + 1])
    if sha(plan_path) != executor.get("plan_sha256"):
        raise ValueError("full-upload plan digest changed")
    plan = read(plan_path)
    case = executor["case"]
    cases = plan.get("cases", {})
    if case not in cases or cases[case].get("kind") != "production_upload":
        raise ValueError("finished source-guarded production_upload case required")
    item = cases[case]
    source_session_path = Path(item["session"])
    if sha(source_session_path) != plan.get("input_files_sha256", {}).get(str(source_session_path)):
        raise ValueError("full-upload original session digest changed or missing")
    source_session = read(source_session_path)
    session_path, events_path = run / "session.json", run / "events.jsonl"
    session = read(session_path)
    media = info["media"]
    if (
        session["session_id"] != sid
        or session["status"] != "analysed"
        or session["media"] != media
        or info["frames_processed"] != media["n_frames"]
        or media["n_frames"] != item["frames"]
        or info["frontier_frame"] != media["n_frames"] - 1
        or session["frontier_frame"] != info["frontier_frame"]
        or session["source"]["sha256"] != item["source_sha256"]
        or info["source_sha256"] != item["source_sha256"]
        or source_session["session_id"] != sid
        or source_session["source"]["sha256"] != item["source_sha256"]
        or Path(source_session["source"]["uri"]).resolve() != Path(item["source"]).resolve()
    ):
        raise ValueError("full-upload session/media/source/frontier mismatch")
    proxy = run / "data/media" / info["source_sha256"] / "proxy.mp4"
    if sha(proxy) != info["proxy_sha256"] or info["proxy_sha256"] != executor.get("output_proxy_sha256"):
        raise ValueError("full-upload canonical proxy bytes changed")
    if sha(Path(item["source"])) != item["source_sha256"]:
        raise ValueError("full-upload source bytes changed")
    paths = sorted((run / "data/sessions" / sid / "perception").glob("*.msgpack"))
    if not paths:
        raise ValueError("full-upload own perception caches required")
    code_files = {
        str(Path(path).relative_to(ROOT)): digest
        for path, digest in plan["source_files_sha256"].items()
        if ROOT in Path(path).parents
    }
    if "perception_cache_catalog" in info:
        from research.production_external_stress import verify_perception_catalog

        receipt = info["perception_cache_catalog"]
        catalogue = verify_perception_catalog(
            run,
            receipt,
            session_id=sid,
            source_sha256=info["source_sha256"],
            proxy_sha256=info["proxy_sha256"],
            media=media,
        )
        expected_caches = {Path(row["path"]).name: row["sha256"] for row in catalogue["files"]}
        scope = "source-bound cache catalogue written before worker completion and verified before replay construction"
        catalogue_paths = (run / receipt["path"],)
    else:
        receipt, catalogue_paths = None, ()
        expected_caches = {path.name: sha(path) for path in paths}
        scope = (
            "captured read-only after completion; original full-upload worker did not publish a cache-digest catalogue"
        )
    return FinishedInput(
        "production-full-upload",
        plan_path,
        report_path,
        session_path,
        events_path,
        run / "data/sessions" / sid / "perception",
        media,
        info["profile"],
        code_files,
        plan["code_commit"],
        expected_caches,
        scope,
        (plan_path, report_path, source_session_path, session_path, events_path, executor_path, *catalogue_paths),
        receipt,
    )


def attach_bounded_fsm_trace(provider, engine, ranges, raw_frames):
    trace, counts = [], {"steps": 0}

    def selected(frame):
        return any(lo <= frame < hi for lo, hi in ranges)

    def state():
        admission = getattr(provider, "last_contact_admission", None)
        return {
            "state": provider.state.value,
            "start": provider.start,
            "tentative_end": provider.tentative_end,
            "end_reason": provider.end_reason,
            "closed": asdict(provider.closed) if provider.closed else None,
            "moving_run": provider._run_visible,
            "moving_run_start": provider._run_start,
            "invisible_run": provider._invisible,
            "last_contact": provider._last_contact_frame,
            "contact_admission": asdict(admission) if is_dataclass(admission) else None,
            "exchange_admission": getattr(provider, "last_exchange_admission", None),
        }

    def finite(value):
        return float(value) if value is not None and math.isfinite(value) else None

    original_step = provider.step_evidence

    def step(observation):
        counts["steps"] += 1
        before = state() if selected(observation.frame) else None
        result = original_step(observation)
        if before is not None:
            index = observation.frame - engine._proc0
            trace.append(
                {
                    "call": "step",
                    "frame": observation.frame,
                    "available_through": engine._last_frame,
                    "observation": asdict(observation),
                    "before": before,
                    "after": state(),
                    "update": asdict(result),
                    "processed_xy": [finite(engine._proc.x[index]), finite(engine._proc.y[index])],
                    "interpolated": bool(engine._proc.interp[index]),
                    "raw_perception": raw_frames.get(observation.frame),
                }
            )
        return result

    provider.step_evidence = step
    for name in ("on_contact", "on_contact_evidence", "on_discontinuity", "flush"):
        original = getattr(provider, name, None)
        if not callable(original):
            continue

        def call(frame, *args, original=original, name=name, **kwargs):
            before = state() if selected(frame) or name == "flush" else None
            result = original(frame, *args, **kwargs)
            if before is not None:
                trace.append(
                    {
                        "call": name,
                        "frame": frame,
                        "available_through": engine._last_frame,
                        "before": before,
                        "after": state(),
                        "update": asdict(result),
                    }
                )
            return result

        setattr(provider, name, call)
    return trace, counts


def replay(
    run,
    sid,
    output,
    *,
    bracket=False,
    motion=False,
    baseline_proof=None,
    focus=(),
    trace_ranges=(),
    source_intervention=None,
    completion_recovery=None,
):
    import msgpack

    harness_bytes, harness_before = capture_harness_sources()
    before = source_hashes()
    recorded = (
        load_finished_input(run, sid)
        if completion_recovery is None
        else load_finished_input(run, sid, completion_recovery=completion_recovery)
    )
    manifest_path, report_path, media = recorded.manifest_path, recorded.report_path, recorded.media
    input_before = {
        str(path): sha(path)
        for path in set(recorded.input_paths)
        | {manifest_path, report_path, recorded.events_path, recorded.session_path}
    }
    changes = {
        path: {"recorded": digest, "current": before.get(path)}
        for path, digest in recorded.code_files.items()
        if path in before and before[path] != digest
    }
    if source_intervention is not None:
        if baseline_proof is None or bracket or motion:
            raise ValueError("source intervention requires a strict baseline proof and no other intervention")
        proof = read(baseline_proof / "replay_manifest.json")
        verify_replay_output_artifacts(baseline_proof, proof)
        if proof.get("cache_sha256") != recorded.expected_caches:
            raise ValueError("baseline proof does not bind this completed perception cache")
        for name, digest in proof.get("harness_source_sha256", {}).items():
            if sha(baseline_proof / "executed_helpers" / name) != digest:
                raise ValueError("baseline proof helper source bytes changed")
        intervention = read(source_intervention)
        changes = require_source_intervention(
            intervention,
            proof,
            report_sha=sha(report_path),
            proof_sha=sha(baseline_proof / "replay_manifest.json"),
            current_sources=before,
            recorded_sources=recorded.code_files,
        )
        input_before[str(source_intervention)] = sha(source_intervention)
    elif any(path.startswith("sports/") for path in changes):
        raise ValueError("sport semantics changed from frozen neural run")
    if bracket and motion:
        raise ValueError("one-variable experiments required")
    if bracket or motion:
        if baseline_proof is None:
            raise ValueError("baseline proof required before optional geometry")
        proof = read(baseline_proof / "replay_manifest.json")
        verify_replay_output_artifacts(baseline_proof, proof)
        require_baseline_proof(
            proof, report_sha=sha(report_path), engine_sources=before, harness_sources=harness_before
        )
    if output.exists() or run.resolve() in output.resolve().parents:
        raise ValueError("new output outside inference run required")
    output.mkdir(parents=True)
    core_source_snapshot = capture_core_source_snapshot(before, output)
    session = Session.model_validate_json(recorded.session_path.read_bytes())
    profile = Profile.model_validate(recorded.profile)
    if source_intervention is not None and intervention.get("rally_evidence_options"):
        choice = profile.components.get("rally")
        if choice is None or choice.implementation not in {"rally-evidence-tracklets-v1", "rally-evidence-v2"}:
            raise ValueError("controlled evidence options require the explicit existing rally provider")
        profile = profile.model_copy(
            update={
                "components": {
                    **profile.components,
                    "rally": choice.model_copy(
                        update={"params": {**choice.params, **intervention["rally_evidence_options"]}}
                    ),
                }
            }
        )
    configured_format = session.roster.match_format if session.roster else None
    discipline = configured_format or "singles"
    context = DomainContext(
        float(session.media.fps), media["width"], media["height"], MatchConfig(discipline=discipline)
    )
    registry = ComponentRegistry()
    register_domain_components(registry)
    handles = {}
    for kind, implementation in DOMAIN_BASELINES.items():
        legacy = getattr(profile, kind, None)
        params = legacy.params if legacy is not None and kind == "contact" else {}
        choice = profile.components.get(
            kind, ModelChoice(model="none", backend="none", implementation=implementation, params=params)
        )
        if kind == "contact" and motion:
            if choice.implementation != "contact-evidence-v1" or "spatial_sigma_px" not in choice.params:
                raise ValueError("explicit existing contact-evidence sensitivity required")
            choice = choice.model_copy(update={"implementation": "contact-motion-reliability-v1"}, deep=True)
        handles[kind] = registry.create(
            kind,
            choice.implementation or implementation,
            context=context,
            configuration=choice.model_dump(mode="json"),
            match_format=configured_format or "unknown",
            context_identity={
                "source": session.source.sha256,
                "fps": float(session.media.fps),
                "frame_size": [media["width"], media["height"]],
                "profile": profile.name,
            },
        )
    store = EventStore(output / "events.sqlite", sid)
    emissions, contact_readouts, current = [], [], []

    def emit(events):
        for event in events:
            payload = event.payload
            geometry = payload.get("participant_geometry_context")
            entry = {
                "event_id": event.event_id,
                "seq": event.seq,
                "type": event.type,
                "frame": event.frame_start,
                "available_through": current[0]._last_frame,
                "geometry": geometry,
            }
            if geometry and geometry.get("estimate") is not None:
                source_frames = geometry["estimate"]["source_frames"]
                if max(source_frames) > entry["available_through"]:
                    raise ValueError("geometry uses a future frame beyond actual emission frontier")
            emissions.append(entry)

    engine = BadmintonMatchEngine(
        sid,
        EngineConfig(
            fps=float(session.media.fps),
            frame_width=media["width"],
            frame_height=media["height"],
            profile=profile.name,
            match=MatchConfig(discipline=discipline),
            match_format_known=configured_format is not None,
            participant_geometry_policy=GeometryBracketPolicy() if bracket else None,
        ),
        store,
        emit=emit,
        player_names={p.player_id: p.name for p in session.players},
        contact_inference=handles["contact"].instance,
        stroke_classifier=handles["stroke"].instance,
        activity_tracker=handles["activity"].instance,
        rally_segmenter=handles["rally"].instance,
        outcome_inference=handles["outcome"].instance,
        score_rules=handles["scoring"].instance,
        analytics=handles["analytics"].instance,
        identity_provider=handles["identity"].instance,
        transactional_components={kind: h.instance for kind, h in handles.items() if h.contract.stateful},
    )
    current.append(engine)
    for pair in trace_ranges:
        if (
            len(pair) != 2
            or any(type(value) is not int for value in pair)
            or not 0 <= pair[0] < pair[1] <= media["n_frames"]
        ):
            raise ValueError("trace ranges must be bounded canonical half-open intervals")
    raw_trace_frames = {}
    fsm_trace, trace_counts = (
        attach_bounded_fsm_trace(handles["rally"].instance, engine, trace_ranges, raw_trace_frames)
        if trace_ranges
        else ([], {"steps": None})
    )
    original_detect = handles["contact"].instance.detect

    def detect(window, **kwargs):
        # Production selection runs first and its result is returned untouched.
        selected = original_detect(window, **kwargs)
        for frame in focus:
            index = frame - window.frame0
            if not kwargs.get("start", 0) <= index < kwargs.get("stop", window.n):
                continue
            candidate = score_frame(
                window, index, motion_reliability=handles["contact"].instance.policy if motion else None
            )
            lo, hi = window.segment_bounds(index)
            ok = window.shuttle.vis & ~window.shuttle.interp
            vb = _seg_velocity(window.shuttle.x, window.shuttle.y, ok, max(lo, index - 3), index)
            va = _seg_velocity(window.shuttle.x, window.shuttle.y, ok, index, min(hi - 1, index + 3))
            contact_readouts.append(
                {
                    "frame": frame,
                    "window": [window.frame0, window.frame0 + window.n],
                    "available_through": engine._last_frame,
                    "incoming_velocity": vb,
                    "outgoing_velocity": va,
                    "candidate_p": candidate.p if candidate else None,
                    "candidate_scores": candidate.components if candidate else None,
                    "P_MIN": P_MIN,
                    "selected_at_frame": any(c.frame == frame for c in selected),
                    "nearby_selected": [
                        {"frame": c.frame, "p": c.p, "scores": c.components}
                        for c in selected
                        if abs(c.frame - frame) <= 6
                    ],
                    "player_series": len(window.players),
                    "current_bodies": sum(bool(p.present[index]) for p in window.players.values()),
                }
            )
        return selected

    handles["contact"].instance.detect = detect
    original_rows = [json.loads(line) for line in recorded.events_path.read_text().splitlines() if line]
    calibration = [row for row in original_rows if row["type"] == "calibration"]
    formats = [row for row in original_rows if row["type"] == "format_decision"]
    if len(calibration) != 1 or calibration[0]["frame_start"] != 0:
        raise ValueError("this replay requires an explicit single initial recorded calibration; no guessed geometry")
    value = calibration[0]["payload"]
    engine.set_calibration(
        0,
        Homography.from_json(value),
        tuple(value["net_top"][0]),
        tuple(value["net_top"][1]),
        cam_ref=value["cam_ref"],
        extra=value,
    )
    cache_hashes = {}
    expected_caches = recorded.expected_caches
    cache_paths = sorted(recorded.cache_directory.glob("*.msgpack"))
    if {path.name for path in cache_paths} != set(expected_caches):
        raise ValueError("retained cache population differs from completed inference")
    try:
        for path in cache_paths:
            payload = path.read_bytes()
            cache_hashes[path.name] = hashlib.sha256(payload).hexdigest()
            if cache_hashes[path.name] != expected_caches[path.name]:
                raise ValueError("own-cache bytes differ from completed inference")
            wire = msgpack.unpackb(payload, raw=False)
            if [row["f"] for row in wire["frames"]] != list(range(wire["start"], wire["end"] + 1)):
                raise ValueError("cache observations must cover each source frame exactly")
            for row in wire["frames"]:
                if any(lo <= row["f"] < hi for lo, hi in trace_ranges):
                    raw_trace_frames[row["f"]] = {
                        key: row.get(key)
                        for key in ("s", "c", "r", "sh", "g", "l", "v", "cs", "do", "ps", "sa", "ce", "cc", "cd")
                    }
                    raw_trace_frames[row["f"]]["people"] = [
                        {key: person.get(key) for key in ("t", "b", "dm", "pf", "rf")} for person in row["p"]
                    ]
            receiver = SimpleNamespace(
                perception=SimpleNamespace(ref_id=wire["cr"]), _isolation_id=lambda wire=wire: wire["ci"]
            )
            chunk = BadmintonSession.decode_perception(receiver, payload, diagnostic=True)
            cursor = chunk.start
            for event in sorted(
                (e for e in formats if chunk.start <= e["frame_start"] <= chunk.end), key=lambda e: e["frame_start"]
            ):
                frame = event["frame_start"]
                if cursor < frame:
                    engine.ingest(BadmintonSession._slice_perception(chunk, cursor, frame - 1))
                apply_recorded_format(engine, event)
                cursor = frame
            engine.ingest(BadmintonSession._slice_perception(chunk, cursor, chunk.end))
            engine.drain_tracks()
        engine.flush()
        if engine._last_frame + 1 != media["n_frames"]:
            raise ValueError("replay did not reach the full source frontier")
        if trace_ranges and trace_counts["steps"] != media["n_frames"]:
            raise ValueError("FSM trace did not observe every canonical step")
        fresh_rows = original_rows
        replay_rows = [event.model_dump(mode="json") for event in store.query(live_only=False)]
        parity = compare_live(fresh_rows, replay_rows)
        baseline_parity = not parity["differences"]
        for name, rows in [
            ("events.jsonl", replay_rows),
            ("current-events.jsonl", [e.model_dump(mode="json") for e in store.query()]),
        ]:
            with (output / name).open("x") as stream:
                for row in rows:
                    stream.write(json.dumps(row, allow_nan=False) + "\n")
        dump(output / "parity_vs_fresh.json", parity)
        dump(output / "emission_frontiers.json", emissions)
        dump(output / "contact_readouts.json", contact_readouts)
        if trace_ranges:
            with (output / "bounded_fsm_trace.jsonl").open("x") as stream:
                for row in fsm_trace:
                    stream.write(json.dumps(row, allow_nan=False) + "\n")
        if source_hashes() != before:
            raise ValueError("core source changed during replay")
        verify_harness_sources(harness_before)
        if any(sha(path) != expected_caches[path.name] for path in cache_paths):
            raise ValueError("own-cache changed during replay")
        if any(sha(Path(path)) != expected for path, expected in input_before.items()):
            raise ValueError("source metadata/catalogue/events changed during replay")
        evidence = {
            "schema": REPLAY_SCHEMA,
            "mode": "controlled source intervention on recorded perception; NOT fresh inference"
            if source_intervention is not None
            else "own recorded perception replay; NOT fresh inference",
            "session_id": sid,
            "source_run": str(run),
            "source_report_sha256": sha(report_path),
            "recorded_source_commit": recorded.source_commit,
            "source_layout": recorded.layout,
            "source_report_path": str(report_path),
            "executed_source_sha256": before,
            "core_source_snapshot": core_source_snapshot,
            "harness_source_sha256": harness_before,
            "generic_source_deltas_from_fresh": changes,
            "source_intervention": intervention if source_intervention is not None else None,
            "geometry_bracket": bracket,
            "contact_motion_reliability": motion,
            "actual_contact_configuration": handles["contact"].configuration
            if hasattr(handles["contact"], "configuration")
            else {
                "implementation": "contact-motion-reliability-v1"
                if motion
                else profile.components["contact"].implementation,
                "params": profile.components["contact"].params,
            },
            "geometry_policy": asdict(GeometryBracketPolicy()) if bracket else None,
            "baseline_parity": baseline_parity,
            "baseline_proof_sha256": sha(baseline_proof / "replay_manifest.json") if baseline_proof else None,
            "cache_sha256": cache_hashes,
            "cache_digest_scope": recorded.cache_digest_scope,
            "source_perception_cache_catalogue": recorded.cache_catalogue_receipt,
            "frames": engine._last_frame + 1,
            "trace_ranges_telemetry_only": trace_ranges,
            "trace_step_count": trace_counts["steps"],
            "profile": recorded.profile,
            "actual_profile": profile.model_dump(mode="json"),
            "no_GT_or_neural_model_input": True,
            "format_decision_replay": {
                "mode": "reapplied source-bound recorded decisions with original validated producer provenance",
                "format_detector_rerun": False,
                "fresh_neural_inference": False,
                "source_event_ids": [row["event_id"] for row in formats],
            },
            "frontier_checks": "geometry source frames <= recorded actual emission frontier",
            "input_artifacts_sha256": input_before,
            "output_artifact_sha256": replay_output_hashes(output, trace=bool(trace_ranges)),
        }
        for name, data in harness_bytes.items():
            destination = output / "executed_helpers" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        (output / Path(__file__).name).write_bytes(harness_bytes["research/production_external_semantic_replay.py"])
        verify_replay_output_artifacts(output, evidence)
        dump(output / "replay_manifest.json", evidence)
        if not (bracket or motion or source_intervention is not None) and not baseline_parity:
            raise ValueError("baseline semantic parity failed; optional experiment refused")
        return evidence
    finally:
        store.close()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", required=True, type=Path)
    p.add_argument("--session", required=True)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--geometry-bracket", action="store_true")
    p.add_argument("--contact-motion-reliability", action="store_true")
    p.add_argument("--baseline-proof", type=Path)
    p.add_argument("--source-intervention", type=Path)
    p.add_argument("--completion-recovery", type=Path, help="Explicit independently verified finalization recovery")
    p.add_argument("--focus", default="419,1569,2714,3736,441,1070,621,1100")
    p.add_argument("--trace-ranges", type=json.loads, default=[])
    a = p.parse_args()
    r = replay(
        a.run.resolve(strict=True),
        a.session,
        a.output.resolve(),
        bracket=a.geometry_bracket,
        motion=a.contact_motion_reliability,
        baseline_proof=a.baseline_proof.resolve(strict=True) if a.baseline_proof else None,
        focus=tuple(int(value) for value in a.focus.split(",") if value),
        trace_ranges=a.trace_ranges,
        source_intervention=a.source_intervention.resolve(strict=True) if a.source_intervention else None,
        completion_recovery=a.completion_recovery.resolve(strict=True) if a.completion_recovery else None,
    )
    print(
        json.dumps(
            {
                "output": str(a.output),
                "baseline_parity": r["baseline_parity"],
                "geometry_bracket": r["geometry_bracket"],
            }
        )
    )


if __name__ == "__main__":
    main()
