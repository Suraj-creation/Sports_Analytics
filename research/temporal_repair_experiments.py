"""Bound frozen temporal observations/callbacks; isolate rally temporal policy hypotheses.

This is NOT inference or a full engine replay. Recorded format barriers and
exit-support assessments are held fixed. Exact original callback/state parity
must pass before any counterfactual is written. Labels are never inputs.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import types
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def module(name, source):
    value = types.ModuleType(name)
    sys.modules[name] = value
    exec(compile(source, name, "exec"), value.__dict__)  # noqa: S102 -- recorded local Git source only
    return value


def frozen_modules(commit):
    prefix = "sports/badminton/src/bai_badminton/events/"
    contents = {
        name: subprocess.check_output(["git", "show", f"{commit}:{prefix}{name}.py"], cwd=ROOT).decode()
        for name in ("rally_fsm", "rally_evidence")
    }
    base = module("frozen_temporal_base", contents["rally_fsm"])
    evidence = module(
        "frozen_temporal_evidence",
        contents["rally_evidence"].replace(
            "from bai_badminton.events.rally_fsm import", "from frozen_temporal_base import"
        ),
    )
    return base, evidence, contents


def physical_evidence(payload):
    from bai_badminton.events.contact_evidence import (
        ContactEvidence,
        ContactEvidenceInputs,
        ContactMotionEvidence,
        ContactReview,
        Reliability,
        ReliabilityAssessment,
    )

    value = copy.deepcopy(payload)
    inputs = value["inputs"]
    if inputs.get("participant_context") is not None:
        from bai_badminton.events.exchange_evidence import ContactParticipantContext, ContactParticipantObservation

        context = inputs["participant_context"]
        context["observations"] = tuple(ContactParticipantObservation(**row) for row in context["observations"])
        inputs["participant_context"] = ContactParticipantContext(**context)
    if inputs.get("motion") is not None:
        motion = inputs["motion"]
        for key in ("before_frames", "after_frames"):
            motion[key] = tuple(motion[key])
        inputs["motion"] = ContactMotionEvidence(**motion)
    if inputs.get("review") is not None:
        inputs["review"] = ContactReview(**inputs["review"])
    for key in ("player_observation_frames", "pose_observation_frames", "racket_observation_frames"):
        inputs[key] = tuple(inputs.get(key, ()))
    return ContactEvidence(
        ContactEvidenceInputs(**inputs),
        *(
            ReliabilityAssessment(Reliability(value[key]["reliability"]), tuple(value[key]["reasons"]))
            for key in ("trajectory", "impact", "attribution")
        ),
    )


def snapshot(fsm):
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


def nested_discontinuities(rows):
    """The wrapper logs a step's nested context callback before the step row."""
    return {
        index - 1
        for index, row in enumerate(rows)
        if index
        and row["call"] == "step"
        and rows[index - 1]["call"] == "on_discontinuity"
        and rows[index - 1]["frame"] == row["frame"]
        and (
            row.get("observation", row.get("evidence", {})).get("kind") == "invalid"
            or not row.get("observation", row.get("evidence", {})).get("context_valid", True)
            or row.get("observation", row.get("evidence", {})).get("replay", False)
        )
    }


def run(rows, fsm, observation_module, evidence_by_frame, *, rich=False, verify=False, reset_frames=()):
    skipped = nested_discontinuities(rows)
    finalized, cancelled, decisions = [], [], []
    reset_frames = list(sorted(reset_frames))
    for index, row in enumerate(rows):
        if index in skipped:
            continue
        while reset_frames and row["frame"] >= reset_frames[0]:
            reset_frames.pop(0)
            fsm = type(fsm)(
                fsm.params,
                use_reconstruction=fsm.use_reconstruction,
                motion_guard=fsm.motion_guard,
                use_exit_recovery=fsm.use_exit_recovery,
                **{
                    key: getattr(fsm, key)
                    for key in ("use_short_exchange_evidence", "use_terminal_contact_evidence")
                    if hasattr(fsm, key)
                },
            )
        if verify and snapshot(fsm) != row["before"]:
            raise ValueError(f"original before-state parity failed at callback{index} frame{row['frame']}")
        if row["call"] == "step":
            values = dict(row.get("observation", row.get("evidence")))
            values["kind"] = observation_module.ObservationKind(values["kind"])
            update = fsm.step_evidence(observation_module.RallyObservation(**values))
        elif row["call"] == "on_contact" and rich:
            update = fsm.on_contact_evidence(row["frame"], evidence_by_frame.get(row["frame"]))
            decisions.append(asdict(fsm.last_contact_admission))
        else:
            update = getattr(fsm, row["call"])(row["frame"])
        if verify and (snapshot(fsm) != row["after"] or asdict(update) != row["update"]):
            raise ValueError(f"original after-state/update parity failed at callback{index} frame{row['frame']}")
        if update.finalized is not None:
            finalized.append({"published_frame": row["frame"], **asdict(update.finalized)})
        if update.cancelled_start is not None:
            cancelled.append({"frame": row["frame"], "start": update.cancelled_start})
    return {"finalized": finalized, "cancelled": cancelled, "contact_decisions": decisions}


def main():
    from bai_badminton.events import rally_evidence as candidate
    from bai_badminton.events import rally_fsm as candidate_base
    from scripts.benchmarking.evaluate_rallies import read_csv, write_predictions

    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("trace", "proof", "events", "inference", "predictions", "cache", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--baseline-commit", required=True)
    a = parser.parse_args()
    proof, info = json.loads(a.proof.read_text()), json.loads(a.inference.read_text())
    expected = proof.get("trace_sha256", proof.get("output_artifact_sha256", {}).get(a.trace.name))
    if expected != sha(a.trace):
        raise ValueError("frozen source trace digest mismatch")
    cache_hashes = {p.name: sha(p) for p in sorted(a.cache.glob("*.msgpack"))}
    if not cache_hashes or cache_hashes != proof["cache_sha256"]:
        raise ValueError("actual own perception caches do not match frozen trace")
    rows = [json.loads(s) for s in a.trace.open() if s.strip()]
    aliases = {"contact": "on_contact", "discontinuity": "on_discontinuity"}
    rows = [{**row, "call": aliases.get(row["call"], row["call"])} for row in rows]
    n = info["media"]["n_frames"]
    if [row["frame"] for row in rows if row["call"] == "step"] != list(range(n)):
        raise ValueError("full ordered temporal trace required")
    evidence, reset_frames = {}, []
    for line in a.events.open():
        event = json.loads(line)
        if event["type"] == "format_decision":
            reset_frames.append(event["frame_start"])
        if event["type"] == "contact" and "physical_evidence" in event["payload"]:
            value = physical_evidence(event["payload"]["physical_evidence"])
            if event["frame_start"] in evidence and evidence[event["frame_start"]] != value:
                raise ValueError("source contact evidence revisions disagree")
            evidence[event["frame_start"]] = value
    old_base, old, sources = frozen_modules(a.baseline_commit)
    candidate_source = (ROOT / "sports/badminton/src/bai_badminton/events/rally_evidence.py").read_text()
    guard_only = module(
        "candidate_guard_frozen_base",
        candidate_source.replace(
            "from bai_badminton.events.rally_fsm import", "from frozen_temporal_base import"
        ).replace("pair = self._short_exchange_witnesses(segment) if segment is not None else None", "pair = None"),
    )
    witness_only = module(
        "candidate_witness_frozen_base",
        candidate_source.replace(
            "from bai_badminton.events.rally_fsm import", "from frozen_temporal_base import"
        ).replace("elif self.state is RallyState.IN_PLAY:", "elif self.state is not RallyState.IDLE:"),
    )
    only_contact = module(
        "candidate_contact_frozen_base",
        (ROOT / "sports/badminton/src/bai_badminton/events/rally_evidence.py")
        .read_text()
        .replace("from bai_badminton.events.rally_fsm import", "from frozen_temporal_base import"),
    )
    profile = info.get("profile", info.get("effective_profile"))
    params = dict(profile["components"]["rally"]["params"])
    flags = {key: params.pop(key, False) for key in ("use_reconstruction", "motion_guard", "use_exit_recovery")}
    params.pop("use_curve_exit", None)
    fps = info["media"]["fps_num"] / info["media"]["fps_den"]
    baseline = run(
        rows,
        old.EvidenceRallyFSM(old_base.RallyParams(fps=fps, **params), **flags),
        old,
        evidence,
        verify=True,
        reset_frames=reset_frames,
    )
    original = read_csv(a.predictions, fps)
    if [(s["start"], s["end"]) for s in baseline["finalized"]] != [(p.start_frame, p.end_frame) for p in original]:
        raise ValueError("original source callback reproduction differs from original predictions")
    a.output.mkdir(parents=True, exist_ok=False)
    outcomes = {"baseline": baseline}
    for name, mod, base, rich in [
        ("terminal_guard_only", guard_only, old_base, True),
        ("short_witness_only", witness_only, old_base, True),
        ("contact_only", only_contact, old_base, True),
        ("resume_only", candidate, candidate_base, False),
        ("combined", candidate, candidate_base, True),
    ]:
        outcomes[name] = run(
            rows,
            mod.EvidenceRallyFSM(
                base.RallyParams(fps=fps, **params),
                **flags,
                use_terminal_contact_evidence=rich,
                use_short_exchange_evidence=name in {"short_witness_only", "contact_only", "combined"},
            ),
            mod,
            evidence,
            rich=rich,
            reset_frames=reset_frames,
        )
    for name, value in outcomes.items():
        directory = a.output / name
        directory.mkdir()
        write_predictions(
            directory / "predicted_rallies.csv", [(p["start"], p["end"]) for p in value["finalized"]], fps
        )
        (directory / "result.json").write_text(json.dumps(value, indent=2) + "\n")
    result = {
        "mode": "conditional recorded-observation/callback policy experiment; NOT inference/full engine replay",
        "original_state_update_and_prediction_parity": True,
        "frames": n,
        "baseline_source_sha256": {k: hashlib.sha256(v.encode()).hexdigest() for k, v in sources.items()},
        "current_sources": {
            str(p): sha(p)
            for p in [
                Path(__file__),
                ROOT / "sports/badminton/src/bai_badminton/events/rally_evidence.py",
                ROOT / "sports/badminton/src/bai_badminton/events/rally_fsm.py",
            ]
        },
        "input_sha256": {str(p): sha(p) for p in (a.trace, a.proof, a.events, a.inference, a.predictions)},
        "cache_sha256": cache_hashes,
        "parameters": {"fps": fps, **params, **flags},
        "source_recorded_format_reset_frames": reset_frames,
        "counts": {name: len(value["finalized"]) for name, value in outcomes.items()},
        "limits": [
            "Recorded startup format barriers and exit-support assessments held fixed",
            "Qualification-dependent continuity must be recomputed in actual engine before promotion",
            "No label or interval reconstruction input; full trace remains source-bound",
        ],
    }
    (a.output / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    (a.output / "executed_source.py").write_bytes(Path(__file__).read_bytes())
    (a.output / "candidate_rally_evidence.py").write_text(candidate_source)
    (a.output / "candidate_rally_fsm.py").write_bytes(Path(candidate_base.__file__).read_bytes())
    print(json.dumps(result["counts"]))


if __name__ == "__main__":
    main()
