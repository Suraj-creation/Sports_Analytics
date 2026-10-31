from types import SimpleNamespace

import numpy as np
import pytest

from bai_badminton.events.contact import detect_contacts, score_frame
from bai_badminton.observations import PlayerSeries, WindowObs
from bai_badminton.participant_contact import ParticipantSnapshot, participant_window
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.pipeline import BadmintonPerception
from bai_badminton.perception.shuttle_post import Track
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs, RacketObservation
from bai_badminton.plugin import BadmintonSession
from bai_engine.config import ModelChoice


def window():
    track = Track.from_arrays(np.array([70, 80, 90, 100, 90, 80, 70.0]), np.full(7, 100.0), np.ones(7, bool))
    person = PlayerSeries.empty(7)
    person.bbox[:] = [80, 180, 120, 380]
    return WindowObs(0, 30, track, {"one": person})


def racket():
    return RacketObservation((100, 100), (30, 40), 0, 0.9, 9)


def test_racket_overlap_contributes_actual_equipment_evidence_and_hitter():
    w = window()
    before = score_frame(w, 3)
    w.players["one"].racket[3] = racket()
    candidate = score_frame(w, 3)
    assert candidate.scores["racket_overlap"] == 1
    assert candidate.scores["racket_observed"] == 1
    assert candidate.p > before.p
    assert candidate.player_id == "one"
    w.players["one"].racket[3] = None
    assert score_frame(w, 3).scores["racket_observed"] == 0


def test_episode_window_preserves_observed_racket_without_holding_it():
    w = window()
    frames = [
        {
            "episode": ParticipantSnapshot(
                1, w.players["one"].bbox[i], None, (0, -3), "birth", True, True, racket=racket() if i == 3 else None
            )
        }
        for i in range(7)
    ]
    episode = participant_window(w, frames, restrict_target_court=True)
    assert episode.players["episode"].racket[3] == racket()
    assert episode.players["episode"].racket[2] is None


def test_diagnostic_codec_retains_equipment_observation():
    value = BadmintonSession.__new__(BadmintonSession)
    value.perception = SimpleNamespace(ref_id=None)
    value._isolation_id = lambda: "racket-contract"
    person = PersonObs(1, np.array([0.0, 0, 200, 300]), 0.9, racket=racket())
    frame = FramePerception(
        0, (100, 100), 0.9, [person], calibration_state=CalibrationState.VALID, detector_observed=True
    )
    decoded = value.decode_perception(value.encode_perception(ChunkPerception(0, 0, [frame])), diagnostic=True)
    assert decoded.frames[0].persons[0].racket == person.racket


def test_explicit_builtin_racket_stage_never_touches_registry():
    perception = BadmintonPerception.__new__(BadmintonPerception)
    perception.models, perception.runtimes, perception.degraded = {}, {}, []
    detector = perception._load_racket(ModelChoice(model="racket_geometry_v1", backend="opencv-cpu"))
    assert detector is not None
    assert perception.models["racket"] == "racket_geometry_v1@1"
    assert perception.runtimes["racket"]["actual_backend"] == "opencv-cpu"
    assert perception._load_racket(None) is None


def test_camera_stabilization_transforms_equipment_with_shuttle_and_body():
    from bai_badminton.engine import _stabilise

    person = PersonObs(1, np.array([50.0, 100, 200, 300]), 0.9, racket=racket())
    matrix = np.array([[2.0, 0, 10], [0, 2, -20], [0, 0, 1]])
    stabilized = _stabilise(person, matrix)
    np.testing.assert_allclose(stabilized.racket.center, (210, 180), atol=1e-4)
    assert stabilized.racket.overlap((210, 180)) == 1
    assert person.racket.center == (100, 100)


def test_two_overlapping_rackets_with_unequal_centres_do_not_name_a_hitter():
    w = window()
    other = PlayerSeries.empty(7)
    other.bbox[:] = [80, 180, 120, 380]
    w.players["two"] = other
    w.players["one"].racket[3] = racket()
    other.racket[3] = RacketObservation((110, 100), (100, 40), 0, 0.9, 9)
    candidate = score_frame(w, 3)
    assert candidate.player_id is None
    assert candidate.attribution_reason == "ambiguous_racket_overlap"


@pytest.mark.parametrize("size", [1, 7, 16, 32, 64])
def test_observed_racket_contact_evidence_is_partition_invariant(size):
    from bai_badminton.testing.synth import make_rally

    rally = make_rally()
    w = rally.obs
    for frame, player in rally.contacts:
        index = w.idx(frame)
        w.players[player].racket[index] = RacketObservation(
            (float(w.shuttle.x[index]), float(w.shuttle.y[index])), (30, 40), 0, 0.95, 9
        )
    whole = detect_contacts(w, enforce_alternation=False)
    parts = [
        candidate
        for start in range(0, w.n, size)
        for candidate in detect_contacts(w, start=start, stop=min(start + size, w.n), enforce_alternation=False)
    ]
    assert any(candidate.scores["racket_overlap"] >= 0.5 for candidate in whole)
    assert [(candidate.frame, candidate.player_id, candidate.components) for candidate in parts] == [
        (candidate.frame, candidate.player_id, candidate.components) for candidate in whole
    ]
