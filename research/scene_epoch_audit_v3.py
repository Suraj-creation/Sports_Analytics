"""Versioned scene-epoch structural compatibility; numerical coverage is preserved.

Every packet must pass the caller's verified native diagnostic decoder. This
module performs no inference, source loading, annotation reads or ROOT mutation.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256

import msgpack
import numpy as np

AUDIT_VERSION = "source-native-scene-epoch-audit:v5"


def validate_scene_epoch_proofs(frames, packets, *, decode_packet):
    flattened = [f for packet in packets for f in packet["frames"]]
    if msgpack.packb(flattened, use_bin_type=True) != msgpack.packb(frames, use_bin_type=True):
        raise ValueError("Frame audit differs from the native-decoded packet population")
    typed = {}
    for packet in packets:
        chunk = decode_packet(packet)
        if [f.frame_idx for f in chunk.frames] != [f["f"] for f in packet["frames"]]:
            raise ValueError("Native decoder changed the source frame population")
        for f in chunk.frames:
            if f.frame_idx in typed:
                raise ValueError("Duplicate source frame across native decoded packets")
            typed[f.frame_idx] = f
    actual = {}
    weak, camera, cross_chunk, abstained = [], [], [], []
    acquisition_frames, verified_acquisitions = [], set()
    packets_by_end = {packet["end"]: packet for packet in packets}
    previous_epoch = None
    for packet in packets:
        acquisition_context_alive = True
        has_acquisition = any(
            getattr(typed[row["f"]], "acquisition_request", None) is not None for row in packet["frames"]
        )
        first_context = (
            (packet["frames"][0]["sh"], packet["frames"][0]["ce"])
            if packet["frames"] and has_acquisition else None
        )
        for f in packet["frames"]:
            index = f["f"]
            raw, d = f.get("cc"), f.get("cd")
            raw_hypothesis = bool(raw and raw.get("hypothesis"))
            barrier = previous_epoch is not None and f["ce"] > previous_epoch
            previous_epoch = f["ce"]
            t = typed[index]
            if has_acquisition and (
                f.get("r") or f.get("v") != "main" or f.get("cs") != "VALID"
                or (f["sh"], f["ce"]) != first_context
            ):
                acquisition_context_alive = False
            acquisition = getattr(t, "acquisition_request", None)
            if acquisition is not None:
                if not acquisition_context_alive:
                    raise ValueError("Sampling request resumed after an invalidated chunk context")
                prior_chunk = packets_by_end.get(acquisition.completed_chunk_end)
                if (
                    prior_chunk is None or prior_chunk["start"] != acquisition.completed_chunk_start
                    or acquisition.decision_frame != packet["start"]
                    or prior_chunk["end"] >= packet["start"]
                ):
                    raise ValueError("Sampling proof lacks its actual previously completed source chunk")
                identity = (
                    acquisition.decision_frame, acquisition.epoch, acquisition.source_frames,
                    acquisition.reference_xy, acquisition.minimum_motion_px_per_frame,
                    acquisition.maximum_age_frames,
                )
                if identity not in verified_acquisitions:
                    for source_frame, claimed_point in zip(
                        acquisition.source_frames, acquisition.reference_xy, strict=True
                    ):
                        source_raw = actual.get(source_frame)
                        source = typed.get(source_frame)
                        evidence = getattr(source, "shuttle_observation", None)
                        if (
                            source_raw is None or source is None or evidence is None
                            or evidence.status != "observed"
                            or evidence.association_status not in {"tracked", "reacquisition"}
                            or evidence.selected_xy is None
                            or source.cam is None or source.replay or source.view != "main"
                            or source.calibration_state is None or source.calibration_state.value != "VALID"
                            or ((source.shot_id << 32) | source.content_epoch) != acquisition.epoch
                        ):
                            raise ValueError("Sampling proof lacks actual observed source and registered context")
                        point = np.linalg.inv(source.cam) @ np.r_[evidence.selected_xy, 1.0]
                        if (
                            not np.isfinite(point).all() or abs(point[2]) < 1e-12
                            or not np.allclose(point[:2] / point[2], claimed_point, rtol=0, atol=1e-9)
                        ):
                            raise ValueError("Sampling proof alters its actual observed source coordinates")
                    verified_acquisitions.add(identity)
                acquisition_frames.append(index)
            if raw and raw.get("version") == "foreground-scene-hypothesis:v5" and t.content_change.regions:
                prior = actual.get(raw.get("previous_frame"))
                if prior is None:
                    raise ValueError("Exclusive feature origins lack the actual adjacent source foreground")
                prior_typed = typed[prior["f"]]
                if tuple(row.region for row in t.content_change.regions) != prior_typed.foreground_regions:
                    raise ValueError("Exclusive feature origins omit or alter actual previous-frame foreground")
            overlap_dependent = bool(
                d
                and d.get("version") == "detector-layout-scene-decision:v4"
                and d.get("feature_origin_overlap_dependent")
            )
            if overlap_dependent and d.get("decision") == "unknown":
                if barrier:
                    raise ValueError("Uncorroborated overlap-dependent hypothesis cannot reset an epoch")
                abstained.append(index)
            if overlap_dependent and d.get("decision") in {"barrier", "no_barrier"}:
                context = packet["ci"].get("layout_format_context")
                if not (
                    isinstance(context, dict)
                    and context.get("confirmed") is True
                    and d.get("expected_participants") == {"singles": 2, "doubles": 4}.get(context.get("match_format"))
                ):
                    raise ValueError("Overlap-dependent decision lacks confirmed prior source format")
            if (
                d
                and d.get("version") in {"detector-layout-scene-decision:v3", "detector-layout-scene-decision:v4"}
                and d.get("previous_to_current")
            ):
                prior = actual.get(d["previous_frame"])
                if prior is None or d["previous_frame"] != index - 1:
                    raise ValueError("Relative scene proof lacks the actual adjacent previous source frame")
                for source in (prior, f):
                    if (
                        source.get("g") is None
                        or source.get("cs") != "VALID"
                        or source.get("v") != "main"
                        or source.get("r")
                    ):
                        raise ValueError("Relative scene proof lacks valid adjacent source calibration/views")
                a = np.asarray(prior["g"], dtype=float).reshape(3, 3)
                b = np.asarray(f["g"], dtype=float).reshape(3, 3)
                claimed = np.asarray(d["previous_camera"], dtype=float).reshape(3, 3)
                relative = np.asarray(d["previous_to_current"], dtype=float).reshape(3, 3)
                if not np.array_equal(a, claimed):
                    raise ValueError("Serialized previous camera differs across the actual cache timeline")
                if not np.allclose(relative, b @ np.linalg.inv(a), rtol=0, atol=1e-9):
                    raise ValueError("Relative scene transform disagrees with actual adjacent cameras")
                camera.append(index)
                if d["previous_frame"] < packet["start"]:
                    cross_chunk.append(index)
            if barrier and not raw_hypothesis:
                if not (
                    raw
                    and d
                    and (
                        (
                            packet["v"] >= 23
                            and raw.get("version") == "foreground-scene-hypothesis:v4"
                            and d.get("version") == "detector-layout-scene-decision:v3"
                        )
                        or (
                            packet["v"] >= 24
                            and raw.get("version") == "foreground-scene-hypothesis:v5"
                            and d.get("version") == "detector-layout-scene-decision:v4"
                        )
                    )
                    and d.get("decision") == "barrier"
                    and d.get("raw_hypothesis") is False
                    and t.content_change is not None
                    and t.content_change.hypothesis is False
                    and t.content_decision is not None
                    and t.content_decision.decision == "barrier"
                    and t.content_decision.raw_hypothesis is False
                    and index in camera
                ):
                    raise ValueError(
                        "Weak epoch reset lacks native validated positive version-paired court/camera proof"
                    )
                context = packet["ci"].get("layout_format_context")
                if not (
                    isinstance(context, dict)
                    and context.get("confirmed") is True
                    and d.get("expected_participants") == {"singles": 2, "doubles": 4}.get(context.get("match_format"))
                ):
                    raise ValueError("Weak epoch reset lacks confirmed prior source format")
                weak.append(index)
            if d and d.get("decision") == "barrier" and not raw_hypothesis and not barrier:
                raise ValueError("Positive weak barrier lacks its actual epoch increment")
            actual[index] = f
    return {
        "version": AUDIT_VERSION,
        "native_decoded_packets": len(packets),
        "native_decoded_frames": len(typed),
        "weak_barrier_frames": weak,
        "overlap_dependent_abstentions": abstained,
        "relative_camera_proof_frames": camera,
        "cross_chunk_camera_proof_frames": cross_chunk,
        "motion_acquisition_proof_frames": acquisition_frames,
        "packet_population_sha256": sha256(msgpack.packb(packets, use_bin_type=True)).hexdigest(),
        "raw_hypothesis_values_preserved": True,
        "accuracy_validated": False,
    }


def audit_frames(frames: list[dict], expected_frames: int, *, packets, decode_packet) -> tuple[dict, list[list], dict]:
    proof = validate_scene_epoch_proofs(frames, packets, decode_packet=decode_packet)
    weak_barriers = set(proof["weak_barrier_frames"])
    abstained = set(proof["overlap_dependent_abstentions"])
    if [f["f"] for f in frames] != list(range(expected_frames)):
        raise ValueError("fresh cache frames must cover each canonical source frame exactly once")
    counts, categories = Counter(), defaultdict(Counter)
    scenes = []
    rows, previous_epoch = [], None
    for frame in frames:
        f, people = frame["f"], frame.get("p", [])
        raw, decision = frame.get("cc"), frame.get("cd")
        hypothesis = bool(raw and raw.get("hypothesis"))
        epoch = frame.get("ce", 0)
        barrier = previous_epoch is not None and epoch > previous_epoch
        epoch_reset = previous_epoch is not None and epoch < previous_epoch
        previous_epoch = epoch
        counts.update(
            {
                "frames": 1,
                "raw_shuttle_present": frame.get("s") is not None,
                "detector_executed_frames": frame.get("do") is True,
                "person_rows": len(people),
                "scene_telemetry_present": raw is not None,
                "scene_raw_hypotheses": hypothesis,
                "actual_content_epoch_increments": barrier,
                "content_epoch_decreases": epoch_reset,
                "detailed_diagnostic_frames": frame.get("dg") is not None,
            }
        )
        for key, value in (
            ("view", frame.get("v")),
            ("calibration_state", frame.get("cs")),
            ("player_population", len(people)),
            ("association_status", (frame.get("sa") or {}).get("status")),
        ):
            categories[key][str(value)] += 1
        categories["association_reason"].update((frame.get("sa") or {}).get("reasons", []))
        if raw is not None:
            categories["scene_raw_status"][str(raw.get("status"))] += 1
        if decision is not None:
            counts["scene_decision_records"] += 1
            categories["scene_decision"][decision["decision"]] += 1
            categories["scene_decision_reason"][decision["reason"]] += 1
            counts["scene_positive_correspondence_vetoes"] += decision["decision"] == "no_barrier"
            counts["scene_current_detector_probes"] += decision.get("detector_frame") is not None
            if decision["decision"] == "no_barrier" and barrier:
                raise ValueError("no_barrier decision contradicted by actual content epoch")
            if decision["decision"] in {"barrier", "unknown"} and hypothesis and not barrier and f not in abstained:
                raise ValueError("selected scene reset/fallback missing its actual content epoch")
        if barrier and not hypothesis and f not in weak_barriers:
            raise ValueError("content epoch reset lacks raw source hypothesis")
        if hypothesis or decision is not None or barrier or epoch_reset:
            scenes.append(
                {
                    "frame": f,
                    "raw_hypothesis": hypothesis,
                    "actual_barrier": barrier,
                    "epoch": epoch,
                    "raw": raw,
                    "decision": decision,
                }
            )
        pose_current, racket_current = 0, 0
        for person in people:
            matched = person.get("dm")
            categories["person_detector_match"][str(matched)] += 1
            categories["person_identity_method"][str(person.get("im"))] += 1
            counts["person_current_detector_matches"] += matched is True
            counts["person_propagated_or_unmatched"] += matched is False
            for name, payload, stamp in (("pose", "k", "pf"), ("racket", "rk", "rf")):
                source = person.get(stamp)
                if source is not None and (type(source) is not int or source > f or source < 0):
                    raise ValueError("future or malformed component source timestamp")
                present = person.get(payload) is not None
                current = present and source == f
                counts[f"{name}_present_rows"] += present
                counts[f"{name}_current_source_rows"] += current
                counts[f"{name}_present_without_current_source"] += present and not current
                counts[f"{name}_current_on_propagated_box"] += current and matched is False
                if name == "pose":
                    pose_current += current
                else:
                    racket_current += current
        rows.append(
            [
                f,
                frame.get("v"),
                frame.get("cs"),
                len(people),
                frame.get("do"),
                pose_current,
                racket_current,
                hypothesis,
                barrier,
                decision["decision"] if decision else None,
                epoch,
            ]
        )
    return (
        {
            "counts": dict(counts),
            "categories": dict(categories),
            "scene_records": scenes,
            "limits": [
                "Counts are technical coverage, not reviewed component accuracy.",
                "Raw shuttle is pre-association decoder output that already passed court masking.",
                "Current pose execution and current box/person association are separate.",
                "Content epochs measure actual tracking action; raw hypotheses remain separate.",
            ],
        },
        rows,
        proof,
    )


def audit_completed_component_frames(frames, expected_frames, *, packets, consumed, producer_root):
    """Versioned structural audit for canonical component evaluators.

    Their matching and metric arithmetic stay untouched. Native decoding and
    explicit producer/tool provenance are mandatory; no module globals change.
    """
    import importlib
    from pathlib import Path

    adapter = importlib.import_module("evaluation.ground_truth_validation.orchestration.analyse_native_completed_run")
    root = Path(producer_root).resolve()
    if (
        Path(adapter.__file__).resolve()
        != root / "evaluation/ground_truth_validation/orchestration/analyse_native_completed_run.py"
    ):
        raise ValueError("Completed component audit requires the actual native adapter")
    original, auditor, decoder, provenance = adapter.load_native_interfaces(root, root)
    if original.ROOT.resolve() != root:
        raise ValueError("Component audit cannot rebase a recorded producer ROOT")
    report, rows, _ = auditor.audit_frames(frames, expected_frames, packets=packets, decode_packet=decoder)
    consumed.update(provenance["source_sha256"])
    return report, rows
