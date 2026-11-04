"""Equipment image evidence must survive an independent shuttle detection miss.

The real pipeline and classical racket detector run on controlled image edges.
Person/pose inference and camera classification are supplied observations; no
weights, actual video or physical-contact labels are used by these tests.
"""

from types import SimpleNamespace

import cv2
import numpy as np
import pytest

from bai_badminton.perception.pipeline import BadmintonPerception, _Scene
from bai_badminton.perception_types import PersonObs
from bai_engine.config import ModelChoice, Profile
from bai_engine.decode import DecodedChunk
from bai_engine.runtime.registry import ModelRegistry


def _image_and_people(count):
    image = np.zeros((400, 400, 3), np.uint8)
    cv2.ellipse(image, (200, 120), (22, 32), 0, 0, 360, (240, 240, 240), 2)
    cv2.line(image, (200, 151), (200, 205), (230, 230, 230), 2)
    keypoints = np.zeros((17, 3), dtype=float)
    keypoints[9] = [200, 205, 0.95]
    people = [
        PersonObs(
            track_id=7,
            bbox=np.array([150, 180, 250, 380], dtype=float),
            conf=0.95,
            kps=keypoints,
            detector_matched=True,
        )
    ]
    people.extend(
        PersonObs(
            track_id=8 + index,
            bbox=np.array([10 + 30 * index, 10, 30 + 30 * index, 60], dtype=float),
            conf=0.95,
            detector_matched=True,
        )
        for index in range(count - 1)
    )
    return image, people


def _perception(tmp_path, monkeypatch, match_format, people, *, view="main", shuttle=False, racket=True):
    disabled = ModelChoice(model="none", backend="none")
    profile = Profile(
        name="racket-acquisition-contract",
        shuttle=disabled,
        player_detector=disabled,
        pose=disabled,
        stroke=disabled,
        racket=ModelChoice(model="racket_geometry_v1", backend="opencv-cpu") if racket else None,
    )
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    (model_dir / "manifest.yaml").write_text("models: {}\n", encoding="utf-8")
    perception = BadmintonPerception(
        profile,
        ModelRegistry(model_dir),
        30.0,
        model_dir,
        (400, 400),
        match_format=match_format,
    )
    monkeypatch.setattr(
        perception,
        "_scene",
        lambda chunk, cuts: _Scene([view], [0], [1.0], None, [None]),
    )
    # Substitute only unavailable model-produced observations. The pipeline's
    # scene gate and the image-based equipment acquisition remain production code.
    monkeypatch.setattr(perception.players, "process", lambda frame, image, rates: people)
    perception.players.last_detector_observed = True
    if shuttle:
        perception.shuttle = SimpleNamespace(
            seq_len=8,
            detect=lambda frames, shots, *, step, masks: [SimpleNamespace(x=200.0, y=120.0, conf=0.9)],
        )
    return perception


@pytest.mark.parametrize("match_format,count", [("singles", 2), ("doubles", 4)])
@pytest.mark.parametrize("shuttle", [False, True])
def test_current_racket_image_observation_does_not_depend_on_shuttle_success(
    tmp_path, monkeypatch, match_format, count, shuttle
):
    image, people = _image_and_people(count)
    perception = _perception(tmp_path, monkeypatch, match_format, people, shuttle=shuttle)
    observed = perception.process(DecodedChunk(0, [image]), in_play=True).frames[0]

    racket = observed.persons[0].racket
    assert racket is not None, "independent racket evidence was discarded when the shuttle was missing"
    assert racket.method == "opencv_ellipse_shaft_v1"
    np.testing.assert_allclose(racket.center, (200, 120), atol=4)
    assert (observed.shuttle_xy is not None) is shuttle


@pytest.mark.parametrize("view", ["alt", "none"])
def test_non_main_frames_do_not_acquire_racket_evidence(tmp_path, monkeypatch, view):
    image, people = _image_and_people(2)
    perception = _perception(tmp_path, monkeypatch, "singles", people, view=view, shuttle=True)
    observed = perception.process(DecodedChunk(0, [image]), in_play=True).frames[0]

    assert observed.replay is True
    assert observed.persons == []
    assert observed.shuttle_xy is None


@pytest.mark.parametrize("missing", ["person", "pose", "fresh_detector_match", "racket_stage"])
def test_missing_owner_evidence_or_disabled_racket_stage_cannot_manufacture_equipment(
    tmp_path, monkeypatch, missing
):
    image, people = _image_and_people(2)
    if missing == "person":
        people = []
    elif missing == "pose":
        people[0].kps = None
    elif missing == "fresh_detector_match":
        people[0].detector_matched = False
    perception = _perception(
        tmp_path, monkeypatch, "singles", people, shuttle=True, racket=missing != "racket_stage"
    )
    observed = perception.process(DecodedChunk(0, [image]), in_play=True).frames[0]

    assert all(person.racket is None for person in observed.persons)
