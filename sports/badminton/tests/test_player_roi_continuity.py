"""Real recorded detections must survive jumps and runoff without admitting spectators."""

import json
from pathlib import Path

import numpy as np

from bai_badminton.court import Homography
from bai_badminton.perception.players import CourtROI, PlayerPerception

FIXTURE = Path(__file__).parent / "fixtures/roi_tracking_real.json"


def test_real_airborne_and_runoff_players_keep_their_existing_track():
    data = json.loads(FIXTURE.read_text())
    roi = CourtROI(np.asarray(data["polygon"], np.float32), homography=Homography(np.array(data["H"]), 0, 4))
    image = np.zeros((720, 1280, 3), np.uint8)
    x0, y0, _, _ = roi.crop_box(1280, 720)
    found = {}
    for start, _ in data["ranges"]:
        perception = PlayerPerception(None, None, 30, det_stride=2, pose_stride=0)
        perception.set_roi(roi)
        for row in data["records"]:
            if row["segment_start"] != start:
                continue
            boxes = np.asarray(row["boxes"]) - [x0, y0, x0, y0]
            scores = np.asarray(row["scores"])
            perception.detector = lambda _, boxes=boxes, scores=scores: (boxes.copy(), scores.copy())
            persons = perception.process(row["frame"], image, (2, 0))
            assert len(persons) <= 2  # many visible spectators were also detected
            if row["frame"] in (8192, 17820, 9666):
                found[row["frame"]] = persons
                assert len(persons) == 2
                assert all(person.detector_matched for person in persons)
                # At least one real athlete's bbox bottom violates the ground gate.
                assert any(not roi.contains_feet(person.bbox) for person in persons)
    assert set(found) == {8192, 17820, 9666}


def test_outside_person_cannot_bootstrap_a_track_or_survive_a_cut():
    data = json.loads(FIXTURE.read_text())
    roi = CourtROI(np.asarray(data["polygon"], np.float32), homography=Homography(np.array(data["H"]), 0, 4))
    row = next(row for row in data["records"] if row["frame"] == 9666)
    # This is the actual jumping player. Without preceding court observations,
    # a projected outside box cannot establish membership of the chosen court.
    box = np.asarray(row["boxes"])[3:4]
    assert not roi.contains_feet(box[0])
    x0, y0, _, _ = roi.crop_box(1280, 720)

    def detector(_):
        return box - [x0, y0, x0, y0], np.array([0.95])

    perception = PlayerPerception(detector, None, 30, det_stride=1, pose_stride=0)
    perception.set_roi(roi)
    image = np.zeros((720, 1280, 3), np.uint8)
    assert perception.process(0, image) == []
    assert perception.process(1, image) == []
    perception._court_tracks[0] = (0, box[0].copy())
    assert perception.process(31, image) == []
    assert not perception._court_tracks
    perception._court_tracks[0] = (1, box[0].copy())
    perception.on_cut()
    assert not perception._court_tracks
    assert perception.process(2, image) == []


def test_returning_from_a_skipped_scene_does_not_revive_a_stale_box():
    def detector(_):
        return np.array([[10, 10, 30, 70]], float), np.array([0.95])

    perception = PlayerPerception(detector, None, 30, det_stride=2, pose_stride=0)
    image = np.zeros((100, 100, 3), np.uint8)
    perception.process(0, image)
    assert len(perception.process(2, image)) == 1
    assert len(perception.process(3, image)) == 1  # scheduled short carry
    assert perception.process(101, image) == []  # court was unanalysable in the gap
