"""Canonical identity comes from fresh observations, with auditable raw IDs."""

from types import SimpleNamespace

import msgpack
import numpy as np
import pytest

from bai_badminton.perception import players
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs


class Features:
    fingerprint = "test-checkpoint"

    def __init__(self):
        self.calls = []
        self.fail = False

    def embed(self, image, boxes):
        self.calls.append(np.asarray(boxes).copy())
        if self.fail:
            raise RuntimeError("test inference unavailable")
        result = np.zeros((len(boxes), 512), dtype=np.float32)
        for i, box in enumerate(boxes):
            result[i, 0 if box[0] < 70 else 1] = 1
        return result


def perception(monkeypatch, reid):
    state = {
        "tracks": [(4, np.array([10.0, 10.0, 40.0, 110.0]), 0.95), (9, np.array([100.0, 10.0, 130.0, 110.0]), 0.95)],
        "missing": False,
    }
    tracker = SimpleNamespace(update=lambda *_: state["tracks"], reset=lambda: None)
    monkeypatch.setattr(players, "PlayerTracker", lambda fps: tracker)

    def detect(image):
        rows = state["tracks"][:1] if state["missing"] else state["tracks"]
        return np.array([b for _, b, _ in rows]), np.array([c for _, _, c in rows])

    p = players.PlayerPerception(detect, None, 30, max_players=4, reid=reid)
    return p, state, np.zeros((160, 180, 3), dtype=np.uint8)


def test_raw_id_swap_keeps_canonical_people_and_private_features(monkeypatch):
    model = Features()
    p, state, image = perception(monkeypatch, model)
    first = p.process(0, image, (2, 0))
    assert {q.raw_track_id: q.track_id for q in first} == {4: 1, 9: 2}
    state["tracks"] = [(9, np.array([15.0, 10.0, 45.0, 110.0]), 0.95), (4, np.array([95.0, 10.0, 125.0, 110.0]), 0.95)]
    second = p.process(2, image, (2, 0))
    assert {q.raw_track_id: q.track_id for q in second} == {9: 1, 4: 2}
    assert all(q.detector_matched is True for q in second)
    assert all(q.appearance is not None and q.appearance.size == 64 for q in second)


def test_carried_boxes_never_teach_neural_appearance(monkeypatch):
    model = Features()
    p, _, image = perception(monkeypatch, model)
    first = p.process(0, image, (2, 0))
    carried = p.process(1, image, (2, 0))
    assert len(model.calls) == 1
    assert [q.track_id for q in carried] == [q.track_id for q in first]
    assert all(q.detector_matched is False for q in carried)


def test_carried_identity_expires_in_physical_time_without_another_detection(monkeypatch):
    model = Features()
    p, _, image = perception(monkeypatch, model)
    assert all(q.track_id >= 0 for q in p.process(0, image, (60, 0)))
    assert all(q.track_id == -1 for q in p.process(31, image, (60, 0)))
    assert len(model.calls) == 1


def test_only_unique_current_detection_matches_reach_embedder(monkeypatch):
    model = Features()
    p, state, image = perception(monkeypatch, model)
    state["missing"] = True
    result = p.process(0, image, (1, 0))
    assert len(model.calls[0]) == 1
    assert result[0].detector_matched is True and result[0].track_id >= 0
    assert result[1].detector_matched is False and result[1].track_id == -1


def test_descriptor_failure_preserves_canonical_namespace_and_reports_degradation(monkeypatch):
    model = Features()
    p, _, image = perception(monkeypatch, model)
    first = p.process(0, image, (2, 0))
    model.fail = True
    after = p.process(2, image, (2, 0))
    assert [q.track_id for q in after] == [q.track_id for q in first]
    assert p.last_identity_error is not None
    assert p.identity_policy["state"] == "degraded"


def test_cut_clears_gallery_without_reusing_canonical_ids(monkeypatch):
    p, _, image = perception(monkeypatch, Features())
    first = p.process(0, image, (2, 0))
    p.on_cut()
    after = p.process(2, image, (2, 0))
    assert {q.track_id for q in first}.isdisjoint(q.track_id for q in after)


def test_disabled_model_keeps_legacy_ids(monkeypatch):
    p, _, image = perception(monkeypatch, None)
    result = p.process(0, image, (1, 0))
    assert [q.track_id for q in result] == [4, 9]
    assert all(q.raw_track_id == q.track_id for q in result)


def test_cache_binds_identity_policy_and_preserves_raw_provenance(tmp_path, monkeypatch):
    from test_plugin_discipline import make_session

    from bai_badminton.plugin import StaleCacheError

    monkeypatch.setattr(players, "PlayerTracker", lambda fps: SimpleNamespace(reset=lambda: None))
    session = make_session(tmp_path, "doubles")
    session.perception.players = SimpleNamespace(identity_policy={"state": "enabled", "model": "checkpoint-a"})
    person = PersonObs(
        1,
        np.array([10.0, 10.0, 40.0, 110.0]),
        0.9,
        raw_track_id=9,
        detector_matched=True,
        identity_method="neural_motion_match",
    )
    frame = FramePerception(
        0, None, 0, persons=[person], calibration_state=CalibrationState.VALID, detector_observed=True
    )
    payload = session.encode_perception(ChunkPerception(0, 0, [frame]))
    result = session.decode_perception(payload).frames[0].persons[0]
    assert (result.track_id, result.raw_track_id, result.detector_matched, result.identity_method) == (
        1,
        9,
        True,
        "neural_motion_match",
    )
    session.perception.players.identity_policy["model"] = "checkpoint-b"
    with pytest.raises(StaleCacheError):
        session.decode_perception(payload)


def test_cache_cannot_disguise_missing_identity_metadata_as_current(tmp_path, monkeypatch):
    from test_plugin_discipline import make_session

    from bai_badminton.plugin import StaleCacheError

    monkeypatch.setattr(players, "PlayerTracker", lambda fps: SimpleNamespace(reset=lambda: None))
    session = make_session(tmp_path, "doubles")
    frame = FramePerception(
        0,
        None,
        0,
        persons=[PersonObs(1, np.array([1.0, 2.0, 3.0, 4.0]), 0.9)],
        calibration_state=CalibrationState.VALID,
        detector_observed=True,
    )
    data = msgpack.unpackb(session.encode_perception(ChunkPerception(0, 0, [frame])), raw=False)
    data["frames"][0]["p"][0].pop("rt", None)
    with pytest.raises(StaleCacheError):
        session.decode_perception(msgpack.packb(data, use_bin_type=True))
