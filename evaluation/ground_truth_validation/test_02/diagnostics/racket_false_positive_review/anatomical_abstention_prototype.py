"""Diagnosis-local candidate ambiguity policy; NOT a production pipeline fix."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import msgpack
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from probe_racket_candidates import ROOT, digest, people  # noqa: E402


def face_aliases(observation, persons, frame_idx):
    """Positive anatomical ambiguity from multiple distinct, current face joints."""
    angle = np.deg2rad(observation["angle"])
    rotation = np.array([[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]])
    aliases = []
    for person in persons:
        if (
            person.detector_matched is not True
            or person.pose_frame_idx != frame_idx
            or person.kps is None
            or person.kps.shape != (17, 3)
        ):
            continue
        contained = []
        for index in range(5):
            joint = person.kps[index]
            if np.isfinite(joint).all() and 0.5 <= joint[2] <= 1:
                radius = np.linalg.norm(
                    rotation @ (joint[:2] - observation["center"]) / (np.asarray(observation["axes"]) / 2)
                )
                if radius <= 1:
                    contained.append(index)
        distinct = np.unique(person.kps[contained, :2], axis=0)
        if len(contained) >= 3 and len(distinct) >= 3:
            aliases.append({"person_track_id": person.track_id, "face_joints": contained})
    return aliases


def abstain_selected_owner(selected, persons, frame_idx):
    """Do not promote a runner-up after the selected candidate becomes ambiguous."""
    retained, ambiguity = {}, []
    for owner, observation in selected.items():
        aliases = face_aliases(observation, persons, frame_idx)
        if aliases:
            ambiguity.append(
                {
                    "owner": str(owner),
                    "status": "ambiguous",
                    "reason": "racket_anatomical_alias",
                    "candidate": copy.deepcopy(observation),
                    "aliases": aliases,
                    "replacement_policy": "whole-owner abstention; no lower-ranked candidate promoted",
                }
            )
        else:
            retained[str(owner)] = copy.deepcopy(observation)
    return {
        "retained": retained,
        "ambiguity": ambiguity,
        "classification": "diagnostic prototype; not physical object classification",
    }


def veto_then_rerank(trace, persons, frame_idx):
    """Comparison-only policy demonstrating promotion of lower-ranked clutter."""
    remaining = []
    for candidate in trace["accepted_proposals"]:
        observation = {
            "center": candidate["center"],
            "axes": candidate["axes"],
            "angle": candidate["angle"],
            "confidence": candidate["uncalibrated_support"],
            "wrist": candidate["wrist"],
            "method": "opencv_ellipse_shaft_v1",
        }
        if not face_aliases(observation, persons, frame_idx):
            remaining.append((candidate["track_id"], candidate["length_body_ratio"], observation))
    selected = {}
    for owner, distance, observation in sorted(remaining, key=lambda row: -row[2]["confidence"]):
        competitors = [
            (other, gap)
            for other, gap, racket in remaining
            if other != owner
            and np.linalg.norm(np.asarray(racket["center"]) - observation["center"]) < min(observation["axes"]) / 2
        ]
        if not any(gap <= distance + 0.05 for _, gap in competitors):
            selected.setdefault(str(owner), observation)
    return selected


def main():
    output = HERE / "anatomical_policy_v1"
    output.mkdir(exist_ok=False)
    (output / "executed_prototype.py").write_bytes(Path(__file__).read_bytes())
    inputs = {str(Path(__file__)): digest(__file__)}
    probe_path = HERE / "probe_v2/probe_results.json"
    probes = json.loads(probe_path.read_text())
    inputs[str(probe_path)] = digest(probe_path)
    result = {
        "classification": "diagnostic-only proposed contract; no pipeline fix/performance gain claimed",
        "test2": {},
        "test1": {},
    }
    for index in (300, 1594):
        path = HERE.parent / f"component_visual_review/frame_{index:05d}/current_cache_frame.json"
        frozen = json.loads(path.read_text())
        inputs[str(path)] = digest(path)
        persons = people(frozen)
        for person, raw in zip(persons, frozen["p"], strict=True):
            person.pose_frame_idx = raw.get("pf")
        trace = probes["frames"][str(index)]["analysis_proxy"]
        result["test2"][str(index)] = {
            "original": trace["selected"],
            "whole_owner_abstention": abstain_selected_owner(trace["selected"], persons, index),
            "candidate_veto_then_rerank": veto_then_rerank(trace, persons, index),
        }
    run = ROOT / "evaluation/ground_truth_validation/test_01/improved_v1/run"
    sid = json.loads((run / "session.json").read_text())["session_id"]
    for path in sorted((run / "data/sessions" / sid / "perception").glob("*.msgpack")):
        chunk = msgpack.unpackb(path.read_bytes(), raw=False)
        for frame in chunk["frames"]:
            if frame["f"] not in (243, 300, 9000):
                continue
            inputs[str(path)] = digest(path)
            persons = people(frame)
            for person, raw in zip(persons, frame["p"], strict=True):
                person.pose_frame_idx = raw.get("pf")
            selected = {str(p["t"]): p["rk"] for p in frame["p"] if p.get("rk") is not None}
            result["test1"][str(frame["f"])] = {
                "original": selected,
                "whole_owner_abstention": abstain_selected_owner(selected, persons, frame["f"]),
            }
    result["input_sha256"] = inputs
    if any(digest(path) != expected for path, expected in inputs.items()):
        raise ValueError("Prototype input changed")
    (output / "policy_comparison.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": "completed", "output": str(output), "production_changes": False}))


if __name__ == "__main__":
    main()
