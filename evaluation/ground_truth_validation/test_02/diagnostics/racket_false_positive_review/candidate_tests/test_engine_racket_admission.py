"""Real-engine candidate regressions; controlled observations, no accuracy GT."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.contact import score_frame
from bai_badminton.participant_contact import participant_window
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs, RacketObservation
from bai_badminton.plugin import BadmintonSession
from bai_badminton.rules import MatchConfig
from bai_badminton.testing.synth import broadcast_homography
from bai_engine.schema import TrackObject
from bai_engine.store import EventStore


def person(frame, *, alias=True, track=0):
    joints = np.zeros((17, 3), float)
    face = (600, 400) if alias else (600, 350)
    for index, (dx, dy) in enumerate(((0, 0), (-4, -3), (4, -3), (-9, 0), (9, 0))):
        joints[index] = [face[0] + dx, face[1] + dy, 0.9]
    joints[9] = [640, 450, 0.9]
    joints[10] = [560, 450, 0.9]
    return PersonObs(
        track,
        np.array([550, 380, 650, 600], float),
        0.95,
        kps=joints,
        racket=RacketObservation((600, 400), (30, 40), 0, 0.9, 9),
        detector_matched=True,
        pose_frame_idx=frame,
        racket_frame_idx=frame,
    )


def setup(tmp_path, *, named=False, discipline="singles", tracked=False):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(30, 1280, 720, match=MatchConfig(discipline=discipline)), store)
    engine.set_calibration(0, broadcast_homography(), cam_ref=10 if tracked else None)
    if named:
        engine._multi_person_identity_ambiguous = False
        engine.identity.assign = lambda people, ends, frame: {"P1": people[0]}
    return engine, store


def frames(*, alias=True, count=7, modifier=None, matrix=None):
    result = []
    for index in range(count):
        owner = person(index, alias=alias)
        people = [owner]
        if modifier:
            modifier(owner, people, index)
        if matrix is not None:
            for p in people:
                xy = np.column_stack((p.kps[:, :2], np.ones(17))) @ matrix.T
                p.kps[:, :2] = xy[:, :2] / xy[:, 2:3]
                p.racket = p.racket.transformed(matrix) if p.racket else None
        result.append(
            FramePerception(
                index,
                (600.0 + index, 400.0),
                0.9,
                people,
                cam=matrix,
                view="main",
                calibration_state=CalibrationState.VALID,
                detector_observed=True,
                pose_stride=1,
            )
        )
    return result


def ingest(engine, observations, *, tracked=False, partition=7):
    for start in range(0, len(observations), partition):
        selected = observations[start : start + partition]
        engine.ingest(
            ChunkPerception(
                start,
                start + len(selected) - 1,
                selected,
                models={"player_detector": "controlled-current", "pose": "controlled-current"},
                cam_ref=10 if tracked else None,
            )
        )


def encode(observations):
    codec = BadmintonSession.__new__(BadmintonSession)
    codec.perception = SimpleNamespace(ref_id=None)
    codec._isolation_id = lambda: "admission-raw-immutability"
    return codec.encode_perception(ChunkPerception(0, len(observations) - 1, observations))


def test_named_semantic_buffer_omits_head_but_raw_cache_and_tracks_are_preserved(tmp_path):
    engine, store = setup(tmp_path, named=True)
    observations = frames()
    original = copy.deepcopy(observations)
    encoded = encode(observations)
    ingest(engine, observations)
    assert engine._players["P1"]["racket"] == [None] * 7
    assert encode(observations) == encoded
    for before, after in zip(original, observations, strict=True):
        np.testing.assert_array_equal(before.persons[0].kps, after.persons[0].kps)
        assert after.persons[0].racket == before.persons[0].racket
        assert after.persons[0].racket_frame_idx == before.persons[0].racket_frame_idx
        assert after.persons[0].court_xy is None
    rackets = [row for row in engine.drain_tracks() if row.obj == TrackObject.RACKET]
    assert len(rackets) == 7
    warning = store.query(types=["racket_observation_ambiguity"])
    assert len(warning) == 7
    assert warning[0].actors.player_id is None
    assert warning[0].payload["semantic_admitted"] is False
    assert warning[0].payload["raw_candidate"]["center"] == [600.0, 400.0]
    assert warning[0].payload["owner_track_id"] == 0
    assert warning[0].payload["coordinate_basis"] == "analysis_image_pixels"
    assert warning[0].payload["face_witnesses"][0]["pose_source_frame"] == 0
    assert warning[0].status.value == "provisional"
    store.close()


@pytest.mark.parametrize("discipline", ["singles", "doubles"])
def test_anonymous_participant_window_omits_alias_and_equipment_overlap(tmp_path, discipline):
    engine, store = setup(tmp_path, discipline=discipline)
    observations = frames()
    ingest(engine, observations)
    snapshots = [p for frame in engine._participant_frames for p in frame.values()]
    assert snapshots
    assert all(p.racket is None and p.racket_frame_idx is None for p in snapshots)
    window = engine._window(0, 6)
    episodes = participant_window(window, engine._participant_frames)
    assert episodes.players
    assert all(all(r is None for r in player.racket) for player in episodes.players.values())
    candidate = score_frame(episodes, 4)
    assert candidate.scores["racket_observed"] == 0
    assert candidate.scores["racket_overlap"] == 0
    scoped = engine._contact_with_observation_evidence(candidate, episodes, engine._participant_frames)
    assert scoped.evidence.inputs.racket_observed is False
    assert scoped.evidence.inputs.racket_observation_frames == ()
    store.close()


@pytest.mark.parametrize("tracked", [False, True])
def test_clear_overhead_racket_is_preserved_without_mutating_input(tmp_path, tracked):
    engine, store = setup(tmp_path, named=True, tracked=tracked)
    observations = frames(alias=False, matrix=np.eye(3) if tracked else None)
    raw = encode(observations)
    ingest(engine, observations, tracked=tracked)
    assert all(r is not None for r in engine._players["P1"]["racket"])
    assert not store.query(types=["racket_observation_ambiguity"])
    assert encode(observations) == raw
    store.close()


@pytest.mark.parametrize(
    "change",
    [
        "missing_pose",
        "low_joints",
        "two_joints",
        "collapsed",
        "stale_pose",
        "missing_pose_stamp",
        "stale_racket",
        "missing_racket_stamp",
        "unmatched",
        "low_person_conf",
        "nonfinite_person_conf",
        "duplicate_face_track",
    ],
)
def test_unreliable_face_evidence_does_not_invent_anatomical_alias(tmp_path, change):
    def modify(owner, people, frame):
        if change == "missing_pose":
            owner.kps = None
        elif change == "low_joints":
            owner.kps[:5, 2] = 0.1
        elif change == "two_joints":
            owner.kps[2:5, 2] = 0.1
        elif change == "collapsed":
            owner.kps[:5, :2] = (600, 400)
        elif change == "stale_pose":
            owner.pose_frame_idx = max(0, frame - 1) if frame else None
        elif change == "missing_pose_stamp":
            owner.pose_frame_idx = None
        elif change == "stale_racket":
            owner.racket_frame_idx = max(0, frame - 1) if frame else None
        elif change == "missing_racket_stamp":
            owner.racket_frame_idx = None
        elif change == "unmatched":
            owner.detector_matched = False
        elif change == "low_person_conf":
            owner.conf = 0.4
        elif change == "nonfinite_person_conf":
            owner.conf = float("nan")
        elif change == "duplicate_face_track":
            people.append(copy.deepcopy(owner))

    engine, store = setup(tmp_path)
    observations = frames(modifier=modify)
    ingest(engine, observations)
    assert not store.query(types=["racket_observation_ambiguity"])
    assert all(fp.persons[0].racket is not None for fp in observations)
    store.close()


def test_another_participants_face_in_doubles_is_an_ambiguity(tmp_path):
    def modify(owner, people, frame):
        owner.kps[:5, :2] += [100, 0]
        witness = person(frame, track=1)
        witness.racket, witness.racket_frame_idx = None, None
        people.append(witness)

    engine, store = setup(tmp_path, discipline="doubles")
    ingest(engine, frames(modifier=modify))
    warning = store.query(types=["racket_observation_ambiguity"])
    assert len(warning) == 7
    assert warning[0].payload["face_witnesses"][0]["track_id"] == 1
    assert all(p.racket is None for f in engine._participant_frames for p in f.values() if p.track_id == 0)
    store.close()


def test_four_player_doubles_preserves_three_unaliased_equipment_candidates(tmp_path):
    def modify(owner, people, frame):
        for track, (dx, dy) in enumerate(((200, 0), (-200, -100), (100, -150)), 1):
            other = person(frame, alias=False, track=track)
            other.kps[:, :2] += [dx, dy]
            other.bbox += [dx, dy, dx, dy]
            other.racket = other.racket.transformed(np.array([[1, 0, dx], [0, 1, dy], [0, 0, 1]]))
            people.append(other)

    engine, store = setup(tmp_path, discipline="doubles")
    ingest(engine, frames(modifier=modify))
    snapshots = list(engine._participant_frames[-1].values())
    assert len(snapshots) == 4
    assert next(p for p in snapshots if p.track_id == 0).racket is None
    assert all(p.racket is not None for p in snapshots if p.track_id != 0)
    assert len(store.query(types=["racket_observation_ambiguity"])) == 7
    store.close()


@pytest.mark.parametrize("frame_idx,expected_removed", [(300, {0}), (1594, set())])
def test_source_bound_test2_observation_predicate_without_physical_accuracy_claim(frame_idx, expected_removed):
    helper = pytest.importorskip("bai_badminton.racket_admission", reason="New helper absent in untouched baseline")
    admit_racket_candidates = helper.admit_racket_candidates

    path = (
        Path(__file__).resolve().parents[2] / f"component_visual_review/frame_{frame_idx:05d}/current_cache_frame.json"
    )
    if not path.is_file():
        pytest.skip("Optional retained Test2 diagnostic cache fixture is not packaged")
    raw = json.loads(path.read_text())
    persons = [
        PersonObs(
            p["t"],
            np.asarray(p["b"], float),
            p["c"],
            kps=np.asarray(p["k"], float),
            detector_matched=p["dm"],
            pose_frame_idx=p.get("pf"),
            racket_frame_idx=p.get("rf"),
            racket=RacketObservation(**p["rk"]) if p.get("rk") else None,
        )
        for p in raw["p"]
    ]
    admitted, diagnostics = admit_racket_candidates(persons, frame_idx=frame_idx)
    assert {p.track_id for p in admitted if p.racket is None} == expected_removed
    assert {d["owner_track_id"] for d in diagnostics} == expected_removed
    assert all(p.racket is not None for p in persons)


@pytest.mark.parametrize(
    "matrix",
    [
        np.array([[0.8, -0.6, 120], [0.6, 0.8, -160], [0, 0, 1]]),
        np.array([[1.2, 0.1, -20], [0.03, 0.95, 10], [0.0002, 0.0001, 1]]),
    ],
)
def test_gate_uses_raw_image_basis_before_rotation_or_projective_registration(tmp_path, matrix):
    engine, store = setup(tmp_path, named=True, tracked=True)
    observations = frames(matrix=matrix)
    raw = encode(observations)
    ingest(engine, observations, tracked=True)
    assert engine._players["P1"]["racket"] == [None] * 7
    assert encode(observations) == raw
    assert len(store.query(types=["racket_observation_ambiguity"])) == 7
    store.close()


def test_three_visible_face_joints_with_occlusion_are_explicitly_ambiguous(tmp_path):
    def modify(owner, people, frame):
        owner.kps[3:5, 2] = 0.1

    engine, store = setup(tmp_path, named=True)
    ingest(engine, frames(modifier=modify))
    assert engine._players["P1"]["racket"] == [None] * 7
    warning = store.query(types=["racket_observation_ambiguity"])
    assert warning[0].payload["face_witnesses"][0]["joint_indices"] == [0, 1, 2]
    store.close()


@pytest.mark.parametrize("partition", [1, 3, 7])
def test_ambiguity_event_admission_is_chunk_partition_invariant(tmp_path, partition):
    engine, store = setup(tmp_path, named=True)
    ingest(engine, frames(), partition=partition)
    warning = store.query(types=["racket_observation_ambiguity"])
    assert [e.frame_start for e in warning] == list(range(7))
    assert engine._players["P1"]["racket"] == [None] * 7
    store.close()
