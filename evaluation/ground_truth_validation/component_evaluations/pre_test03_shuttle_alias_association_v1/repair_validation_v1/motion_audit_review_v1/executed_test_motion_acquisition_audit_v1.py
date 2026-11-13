"""Source-timeline audit after a typed decoder; no NN or physical labels.

Native codec25 parsing has separate sport tests. These controlled two chunks
exercise cross-packet source binding, including selected-versus-raw coordinates.
"""

from types import SimpleNamespace

import numpy as np
import pytest

from bai_badminton.perception.acquisition import MotionAcquisitionProof
from bai_badminton.perception.association import (
    CURRENT_ASSOCIATION_METHOD,
    CURRENT_ASSOCIATION_SCHEMA,
    ShuttleObservationEvidence,
)
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.diagnostics import HeatmapCandidate
from bai_badminton.perception_types import FramePerception
from research import scene_epoch_audit_v3 as audit

EPOCH = (2 << 32) | 3


def point(frame):
    return 10.0 + 4.0 * frame, 20.0


def source_row(frame):
    camera = np.eye(3)
    camera[0, 2] = 5.0
    xy = (point(frame)[0] + 5.0, point(frame)[1])
    return {
        "f": frame,
        "sh": 2,
        "ce": 3,
        "g": camera.ravel().tolist(),
        "cs": "VALID",
        "v": "main",
        "r": False,
        "s": [500.0, 400.0] if frame in range(4, 8) else list(xy),
        "c": 0.9,
        "p": [],
        "do": True,
        "cc": None,
        "cd": None,
        "fg": [],
        "status": "observed",
        "association_status": "tracked",
        "selected": list(xy),
        "alternative": frame in range(4, 8),
    }


def two_chunks():
    first = [source_row(f) for f in range(8)]
    current = [source_row(f) for f in range(8, 12)]
    proof = MotionAcquisitionProof(
        decision_frame=8,
        completed_chunk_start=0,
        completed_chunk_end=7,
        source_frames=(4, 5, 6, 7),
        reference_xy=tuple(point(f) for f in range(4, 8)),
        epoch=EPOCH,
        minimum_motion_px_per_frame=3.0,
        maximum_age_frames=60,
    )
    for f in current:
        f["aq"] = proof.to_dict()
    return [
        {"v": 25, "start": 0, "end": 7, "frames": first},
        {"v": 25, "start": 8, "end": 11, "frames": current},
    ]


def typed_decode(packet):
    result = []
    for row in packet["frames"]:
        raw = tuple(row["s"]) if row["s"] is not None else None
        selected = tuple(row["selected"]) if row["selected"] is not None else None
        epoch = (row["sh"] << 32) | row["ce"]
        evidence = None
        if row.get("status") is not None:
            extra = {}
            if row["alternative"] and row["status"] == "observed":
                # Deliberately distinct raw argmax: the auditor must bind the
                # selected current NN point, never substitute frame.s.
                raw = (500.0, 400.0)
                candidates = (
                    HeatmapCandidate(1, raw, raw, 0.9, 10, 3.0, True, True, True),
                    HeatmapCandidate(2, selected, selected, 0.8, 10, 3.0, True, True, False),
                )
                extra = dict(
                    candidates=candidates,
                    schema=CURRENT_ASSOCIATION_SCHEMA,
                    method=CURRENT_ASSOCIATION_METHOD,
                    hypothesis_id=0,
                    competing_motion_frames=(row["f"] - 3, row["f"] - 2, row["f"] - 1),
                    selected_candidate_rank=2,
                    selected_model_support=0.8,
                    selection_coordinate_source="current_candidate_peak",
                    selection_witness_frames=(row["f"] - 3, row["f"] - 2, row["f"] - 1),
                    selection_model_threshold=0.5,
                    selection_hypothesis_id=1,
                    raw_masked_peak_xy=raw,
                )
            evidence = ShuttleObservationEvidence(
                frame_idx=row["f"],
                epoch=epoch,
                status=row["status"],
                association_status=row["association_status"],
                raw_xy=raw,
                selected_xy=selected,
                raw_model_support=row["c"],
                **extra,
            )
        result.append(
            FramePerception(
                frame_idx=row["f"],
                shuttle_xy=raw,
                shuttle_conf=row["c"],
                shot_id=row["sh"],
                content_epoch=row["ce"],
                cam=np.asarray(row["g"]).reshape(3, 3),
                replay=row["r"],
                view=row["v"],
                calibration_state=CalibrationState(row["cs"]),
                shuttle_observation=evidence,
                acquisition_request=MotionAcquisitionProof.from_dict(row["aq"]) if row.get("aq") else None,
            )
        )
    return SimpleNamespace(frames=result)


def verify(packets):
    frames = [f for p in packets for f in p["frames"]]
    return audit.validate_scene_epoch_proofs(frames, packets, decode_packet=typed_decode)


def test_two_complete_chunks_bind_registered_selected_observations_not_raw_argmax():
    p = two_chunks()
    proof = verify(p)
    assert proof["motion_acquisition_proof_frames"] == [8, 9, 10, 11]
    assert proof["native_decoded_frames"] == 12
    assert proof["raw_hypothesis_values_preserved"] is True
    assert p[0]["frames"][4]["g"][2] == 5.0
    assert typed_decode(p[0]).frames[4].shuttle_observation.raw_xy == (500.0, 400.0)
    assert p[0]["frames"][4]["s"] == [500.0, 400.0]


def test_acquisition_metadata_keeps_original_numeric_coverage_and_csv_unchanged():
    from research.pipeline_repair_run_analysis import audit_frames as original

    p = two_chunks()
    frames = [f for packet in p for f in packet["frames"]]
    expected = original(frames, len(frames))
    report, csv_rows, proof = audit.audit_frames(frames, len(frames), packets=p, decode_packet=typed_decode)
    assert (report, csv_rows) == expected
    assert proof["motion_acquisition_proof_frames"] == [8, 9, 10, 11]


@pytest.mark.parametrize(
    "change",
    [
        "claimed_point",
        "actual_camera",
        "source_epoch",
        "missing_source",
        "missing_evidence",
        "rejected_source",
        "unknown_association",
    ],
)
def test_acquisition_source_claims_must_match_actual_completed_neural_observations(change):
    p = two_chunks()
    if change == "claimed_point":
        for f in p[1]["frames"]:
            f["aq"]["reference_xy"] = ((26.25, 20.0), (30.0, 20.0), (34.0, 20.0), (38.0, 20.0))
    elif change == "actual_camera":
        p[0]["frames"][4]["g"][2] = 6.0
    elif change == "source_epoch":
        p[0]["frames"][4]["sh"] = 3
    elif change == "missing_source":
        p[0]["frames"].pop(4)
    elif change == "missing_evidence":
        p[0]["frames"][4]["status"] = None
    elif change == "rejected_source":
        p[0]["frames"][4].update(
            status="ambiguous", association_status="static_candidate", selected=None, alternative=False
        )
    else:
        p[0]["frames"][4]["association_status"] = "unknown"
    with pytest.raises(ValueError, match="Sampling proof"):
        verify(p)


def test_verification_memo_cannot_hide_later_changed_source_coordinates():
    p = two_chunks()
    # First frame publishes a genuine proof, then an altered same-frame-list
    # claim must be independently rebound rather than reusing a frame-ID memo.
    p[1]["frames"][9 - 8]["aq"]["reference_xy"] = ((26.25, 20.0), (30.0, 20.0), (34.0, 20.0), (38.0, 20.0))
    with pytest.raises(ValueError, match="actual observed source coordinates"):
        verify(p)


@pytest.mark.parametrize("change", ["prior_start", "prior_end", "decision_chunk", "future_sources"])
def test_sampling_publication_requires_actual_prior_completed_chunk_and_past_sources(change):
    p = two_chunks()
    if change == "prior_start":
        for f in p[1]["frames"]:
            f["aq"]["completed_chunk_start"] = 1
    elif change == "prior_end":
        p[0]["end"] = 6
    elif change == "decision_chunk":
        for f in p[1]["frames"]:
            f["aq"].update(decision_frame=7, completed_chunk_end=6)
            f["aq"]["source_frames"] = (3, 4, 5, 6)
            f["aq"]["reference_xy"] = tuple(point(x) for x in (3, 4, 5, 6))
    else:
        for f in p[1]["frames"]:
            f["aq"]["source_frames"] = (8, 9, 10, 11)
            f["aq"]["reference_xy"] = tuple(point(x) for x in (8, 9, 10, 11))
    with pytest.raises(ValueError):
        verify(p)


@pytest.mark.parametrize("change", ["view", "replay", "geometry", "shot", "content_epoch"])
def test_request_cannot_resume_when_chunk_context_temporarily_invalidates(change):
    p = two_chunks()
    bad = p[1]["frames"][1]
    bad["aq"] = None
    if change == "view":
        bad["v"] = "alt"
    elif change == "replay":
        bad["r"] = True
    elif change == "geometry":
        bad["cs"] = "LOST"
    elif change == "shot":
        bad["sh"] = 3
    else:
        bad["ce"] = 4
        bad["cc"] = {"hypothesis": True, "status": "hypothesis"}
    with pytest.raises(ValueError, match="resumed after an invalidated chunk context"):
        verify(p)


def test_legacy_no_aq_never_requires_new_sampling_source_fields_or_changes_numeric_coverage():
    from research.pipeline_repair_run_analysis import audit_frames as original
    from research.tests.test_scene_epoch_audit_v3 import frame, packet, typed_stub

    frames = [frame(0), frame(1)]  # controlled historical minimal records lack sh/aq
    expected = original(frames, 2)
    actual, csv, proof = audit.audit_frames(frames, 2, packets=[packet(frames)], decode_packet=typed_stub)
    assert (actual, csv) == expected
    assert proof["motion_acquisition_proof_frames"] == []
