"""Actual image processing, not a mocked racket detector."""

import cv2
import numpy as np
import pytest

from bai_badminton.perception.racket import RacketDetector
from bai_badminton.perception_types import PersonObs


def scene(scale=1, angle=0, *, shaft=True, head=True):
    image = np.zeros((400 * scale, 400 * scale, 3), np.uint8)
    centre, wrist = (200 * scale, 120 * scale), (200 * scale, 205 * scale)
    if head:
        cv2.ellipse(image, centre, (22 * scale, 32 * scale), angle, 0, 360, (240, 240, 240), 2 * scale)
    if shaft:
        cv2.line(image, (200 * scale, 151 * scale), wrist, (230, 230, 230), 2 * scale)
    kps = np.zeros((17, 3), float)
    kps[9] = [*wrist, 0.95]
    person = PersonObs(7, np.array([150, 180, 250, 380], float) * scale, 0.95, kps=kps, detector_matched=True)
    return image, person, centre


@pytest.mark.parametrize("scale,angle", [(1, 0), (1, 35), (2, 0), (2, 60)])
def test_observes_a_real_ellipse_and_connected_shaft(scale, angle):
    image, person, centre = scene(scale, angle)
    result = RacketDetector().detect(image, [person])
    assert set(result) == {7}
    racket = result[7]
    assert np.linalg.norm(np.asarray(racket.center) - centre) < 4 * scale
    assert racket.method == "opencv_ellipse_shaft_v1"
    assert 0.5 <= racket.confidence <= 1


@pytest.mark.parametrize("shaft,head", [(False, False), (True, False), (False, True)])
def test_wrist_head_or_shaft_alone_does_not_invent_racket(shaft, head):
    image, person, _ = scene(shaft=shaft, head=head)
    assert RacketDetector().detect(image, [person]) == {}


def test_missing_pose_carried_person_and_ambiguous_owner_abstain():
    image, person, _ = scene()
    person.detector_matched = False
    assert RacketDetector().detect(image, [person]) == {}
    person.detector_matched = True
    other = PersonObs(8, person.bbox.copy(), 0.95, kps=person.kps.copy(), detector_matched=True)
    assert RacketDetector().detect(image, [person, other]) == {}
    person.kps = None
    assert RacketDetector().detect(image, [person]) == {}


def test_low_confidence_or_duplicate_track_id_cannot_claim_equipment():
    image, person, _ = scene()
    person.conf = 0.49
    assert RacketDetector().detect(image, [person]) == {}
    person.conf = 0.9
    other = PersonObs(person.track_id, person.bbox.copy(), 0.9, kps=person.kps.copy(), detector_matched=True)
    assert RacketDetector().detect(image, [person, other]) == {}


def test_invalid_image_rejected_and_off_image_wrist_is_not_clamped_into_evidence():
    image, person, _ = scene()
    with pytest.raises(ValueError):
        RacketDetector().detect(image.astype(float), [person])
    person.kps[9] = [-20, -20, 0.9]
    assert RacketDetector().detect(image, [person]) == {}
