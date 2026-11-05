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
from dataclasses import asdict, dataclass
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
from bai_engine.schema import Provenance, Session  # noqa: E402
from bai_engine.store import EventStore  # noqa: E402
from research.production_external_reference_report import validate_coverage, validate_finished  # noqa: E402
from research.production_replay_parity_audit import compare_live  # noqa: E402

REPLAY_SCHEMA = "cached-external-semantic:v2"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


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


def load_finished_input(run, sid):
    """Read genuine harness or full-upload exports; never fabricate run metadata."""
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
        or executor.get("case") != "test7"
        or info.get("cached_perception_used") is not False
    ):
        raise ValueError("finished source-guarded full-upload worker required")
    command = executor["command"]
    if command.count("--plan") != 1:
        raise ValueError("explicit recorded full-upload plan required")
    plan_path = Path(command[command.index("--plan") + 1])
    if sha(plan_path) != executor.get("plan_sha256"):
        raise ValueError("full-upload plan digest changed")
    plan = read(plan_path)
    item = plan["cases"]["test7"]
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
        (plan_path, report_path, session_path, events_path, executor_path, *catalogue_paths),
        receipt,
    )


def attach_bounded_fsm_trace(provider, engine, ranges, raw_frames):
    trace, counts = [], {"steps": 0}

    def selected(frame):
        return any(lo <= frame < hi for lo, hi in ranges)

    def state():
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
    for name in ("on_contact", "on_discontinuity", "flush"):
        original = getattr(provider, name)

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


def replay(run, sid, output, *, bracket=False, motion=False, baseline_proof=None, focus=(), trace_ranges=()):
    import msgpack

    harness_bytes, harness_before = capture_harness_sources()
    before = source_hashes()
    recorded = load_finished_input(run, sid)
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
    if any(path.startswith("sports/") for path in changes):
        raise ValueError("sport semantics changed from frozen neural run")
    if bracket and motion:
        raise ValueError("one-variable experiments required")
    if bracket or motion:
        if baseline_proof is None:
            raise ValueError("baseline proof required before optional geometry")
        proof = read(baseline_proof / "replay_manifest.json")
        require_baseline_proof(
            proof, report_sha=sha(report_path), engine_sources=before, harness_sources=harness_before
        )
    if output.exists() or run.resolve() in output.resolve().parents:
        raise ValueError("new output outside inference run required")
    output.mkdir(parents=True)
    session = Session.model_validate_json(recorded.session_path.read_bytes())
    profile = Profile.model_validate(recorded.profile)
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
                        key: row.get(key) for key in ("s", "c", "r", "sh", "g", "l", "v", "cs", "do", "ps", "sa", "ce")
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
                value = event["payload"]
                engine.set_match_format(
                    value["match_format"],
                    frame,
                    Provenance(model="diagnostic:recorded-format"),
                    decision=value["decision"],
                )
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
            "mode": "own recorded perception replay; NOT fresh inference",
            "session_id": sid,
            "source_run": str(run),
            "source_report_sha256": sha(report_path),
            "recorded_source_commit": recorded.source_commit,
            "source_layout": recorded.layout,
            "source_report_path": str(report_path),
            "executed_source_sha256": before,
            "harness_source_sha256": harness_before,
            "generic_source_deltas_from_fresh": changes,
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
            "no_GT_or_neural_model_input": True,
            "frontier_checks": "geometry source frames <= recorded actual emission frontier",
            "input_artifacts_sha256": input_before,
        }
        for name, data in harness_bytes.items():
            destination = output / "executed_helpers" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        (output / Path(__file__).name).write_bytes(harness_bytes["research/production_external_semantic_replay.py"])
        dump(output / "replay_manifest.json", evidence)
        if not (bracket or motion) and not baseline_parity:
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
