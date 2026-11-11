"""Separate raw geometric racket candidates from semantic equipment admission.

Multiple current facial landmarks inside a selected ellipse provide positive
anatomical ambiguity. They do not classify the pixels as a head, certify other
rackets, or infer a missing physical contact. Raw observations remain untouched.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, replace

import numpy as np

from bai_badminton.perception_types import PersonObs

POLICY = "racket_anatomical_alias_abstention_v1"
GEOMETRIC_METHOD = "opencv_ellipse_shaft_v1"
FACIAL_JOINTS = range(5)  # COCO nose, eyes and ears; not a fixed image/body region.
MIN_SUPPORT = 0.5  # Existing detector/posed-wrist evidence cutoff, not a probability.
MIN_DISTINCT_FACE_JOINTS = 3


def _fresh_person(person: PersonObs, counts: Counter[int]) -> bool:
    return bool(
        person.track_id >= 0
        and counts[person.track_id] == 1
        and person.detector_matched is True
        and np.isfinite(person.conf)
        and MIN_SUPPORT <= person.conf <= 1
        and person.bbox.shape == (4,)
        and np.isfinite(person.bbox).all()
    )


def admit_racket_candidates(persons: list[PersonObs], *, frame_idx: int) -> tuple[list[PersonObs], list[dict]]:
    """Return new semantic copies and explicit selected-candidate abstentions.

    Only the supported geometric candidate is gated. No alternate ellipse is
    selected after an anatomical alias, and missing anatomy never invents an alias.
    Evaluate in the raw analysis-image basis before camera registration.
    """
    if type(frame_idx) is not int or frame_idx < 0:
        raise ValueError("racket admission requires a canonical source frame")
    counts = Counter(person.track_id for person in persons)
    witnesses = [
        person
        for person in persons
        if _fresh_person(person, counts)
        and person.pose_frame_idx == frame_idx
        and person.kps is not None
        and person.kps.shape == (17, 3)
    ]
    copies, ambiguity = [], []
    for person in persons:
        racket = person.racket
        if (
            racket is None
            or racket.method != GEOMETRIC_METHOD
            or person.racket_frame_idx != frame_idx
            or not _fresh_person(person, counts)
        ):
            copies.append(replace(person))
            continue
        angle = np.deg2rad(racket.angle)
        rotation = np.array([[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]])
        face_witnesses = []
        for witness in witnesses:
            indices = []
            for index in FACIAL_JOINTS:
                point = witness.kps[index]
                if not np.isfinite(point).all() or not MIN_SUPPORT <= point[2] <= 1:
                    continue
                radius = np.linalg.norm(rotation @ (point[:2] - racket.center) / (np.asarray(racket.axes) / 2))
                if radius <= 1:
                    indices.append(index)
            distinct = np.unique(witness.kps[indices, :2], axis=0)
            if len(indices) < MIN_DISTINCT_FACE_JOINTS or len(distinct) < MIN_DISTINCT_FACE_JOINTS:
                continue
            face_witnesses.append(
                {
                    "track_id": witness.track_id,
                    "pose_source_frame": witness.pose_frame_idx,
                    "detector_matched": witness.detector_matched,
                    "joint_indices": indices,
                    "joint_xy_support": witness.kps[indices].tolist(),
                }
            )
        if not face_witnesses:
            copies.append(replace(person))
            continue
        copies.append(replace(person, racket=None, racket_frame_idx=None))
        ambiguity.append(
            {
                "schema": "racket_semantic_admission_v1",
                "policy": POLICY,
                "reason": "racket_anatomical_alias",
                "status": "ambiguous",
                "semantic_admitted": False,
                "frame_idx": frame_idx,
                "owner_track_id": person.track_id,
                "racket_source_frame": person.racket_frame_idx,
                "owner_pose_source_frame": person.pose_frame_idx,
                "coordinate_basis": "analysis_image_pixels",
                "raw_candidate": asdict(racket),
                "raw_candidate_preserved": True,
                "face_witnesses": face_witnesses,
                "replacement_policy": "whole_owner_selected_candidate_abstention_no_reranking",
                "interpretation": "Equipment/anatomy ambiguity, not a verified head or physical negative-contact label",
            }
        )
    return copies, ambiguity
