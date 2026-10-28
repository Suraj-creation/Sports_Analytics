from pathlib import Path

import pytest

from bai_badminton.identity_review import IdentityReviewLedger
from bai_engine.schema import Event, EventStatus, Provenance
from bai_engine.store import EventStore


def observation(store, pid="participant-abcd-000001", track=1, frame=5, kind="PARTICIPANT_FIRST_OBSERVED"):
    return store.append(
        Event(
            session_id="S1",
            type="participant_observation",
            frame_start=frame,
            frame_end=frame,
            pts_us=0,
            payload={"kind": kind, "participant_id": pid, "track_id": track},
            provenance=Provenance(model="participant_tracker_v1"),
        )
    )


def test_review_survives_restart_and_revoke(tmp_path: Path):
    path = tmp_path / "events.sqlite"
    store = EventStore(path, "S1")
    obs = observation(store)
    ledger = IdentityReviewLedger(store, {"P1", "P2"}, max_frame=100, fps=30)
    event = ledger.confirm(obs.event_id, "P1", 5, 20)
    assert event.pts_us == 166667
    assert event.status == EventStatus.HUMAN_VERIFIED
    assert event.payload["tracker_instance"] == "abcd"
    store.close()
    reopened = EventStore(path, "S1")
    restored = IdentityReviewLedger(reopened, {"P1", "P2"}, max_frame=100, fps=30)
    assert [e.event_id for e in restored.current()] == [event.event_id]
    restored.revoke(event.event_id)
    assert restored.current() == []


def test_rejects_overlapping_mappings_and_epoch_crossing(tmp_path: Path):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    a = observation(store)
    b = observation(store, "participant-abcd-000002", 2)
    ledger = IdentityReviewLedger(store, {"P1", "P2"}, max_frame=100, fps=30)
    ledger.confirm(a.event_id, "P1", 5, 20)
    with pytest.raises(ValueError, match="overlap"):
        ledger.confirm(b.event_id, "P1", 10, 15)
    with pytest.raises(ValueError, match="overlap"):
        ledger.confirm(a.event_id, "P2", 10, 15)
    store.append(
        Event(
            session_id="S1",
            type="identity_ambiguity",
            frame_start=30,
            frame_end=30,
            pts_us=0,
            payload={"reason": "visual_tracker_reset", "tracker_instance": "efgh"},
            provenance=Provenance(model="participant_tracker_v1"),
        )
    )
    with pytest.raises(ValueError, match="epoch"):
        ledger.confirm(b.event_id, "P2", 21, 30)


def test_unverified_cues_cannot_be_used_as_review_source(tmp_path: Path):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    obs = observation(store, kind="PLAYER_REIDENTIFICATION_UNCERTAIN")
    ledger = IdentityReviewLedger(store, {"P1"}, max_frame=100, fps=30)
    with pytest.raises(ValueError, match="observation"):
        ledger.confirm(obs.event_id, "P1", 5, 6)


def test_review_is_not_carried_to_reanalysis_by_nearby_frame(tmp_path: Path):
    from bai_badminton.engine import BadmintonMatchEngine, EngineConfig

    old = EventStore(tmp_path / "old.sqlite", "S1")
    obs = observation(old)
    review = IdentityReviewLedger(old, {"P1"}, max_frame=100, fps=30).confirm(obs.event_id, "P1", 5, 10)
    new = EventStore(tmp_path / "new.sqlite", "S1")
    # A similar old-looking event must never receive an old participant mapping.
    observation(new, "participant-different-000001", 9, 5)
    new.append(
        Event(
            session_id="S1",
            type="identity_review",
            frame_start=5,
            frame_end=10,
            pts_us=0,
            payload={"participant_id": "participant-different-000001"},
            provenance=Provenance(model="automatic"),
        )
    )
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), new)
    assert engine.carry_over([review], Provenance(model="human", worker="carried-over")) == 0
    assert IdentityReviewLedger(new, {"P1"}, max_frame=100, fps=30).current() == []


def test_review_rejects_unknown_player_exit_track_reuse_and_nonhuman_cues(tmp_path: Path):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    first = observation(store)
    ledger = IdentityReviewLedger(store, {"P1"}, max_frame=100, fps=30)
    with pytest.raises(ValueError, match="unknown session player"):
        ledger.confirm(first.event_id, "P4", 5, 10)
    observation(store, frame=12, kind="PLAYER_EXITED")
    with pytest.raises(ValueError, match="exit"):
        ledger.confirm(first.event_id, "P1", 5, 12)
    store = EventStore(tmp_path / "reuse.sqlite", "S1")
    first = observation(store)
    ledger = IdentityReviewLedger(store, {"P1"}, max_frame=100, fps=30)
    second = observation(store, pid="participant-abcd-000002", track=1, frame=15, kind="PLAYER_ENTERED")
    with pytest.raises(ValueError, match="reuse"):
        ledger.confirm(first.event_id, "P1", 5, 20)
    assert ledger.confirm(second.event_id, "P1", 15, 20)


def test_review_checks_input_and_preserves_unrelated_reviews(tmp_path: Path):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    first = observation(store)
    other = observation(store, pid="participant-abcd-000002", track=2)
    ledger = IdentityReviewLedger(store, {"P1", "P2"}, max_frame=100, fps=30)
    with pytest.raises(ValueError):
        ledger.confirm(first.event_id, "P1", True, 10)
    with pytest.raises(ValueError):
        ledger.confirm(first.event_id, "P1", 5, 101)
    a = ledger.confirm(first.event_id, "P1", 5, 10)
    b = ledger.confirm(other.event_id, "P2", 5, 10)
    ledger.revoke(a.event_id)
    assert [event.event_id for event in ledger.current()] == [b.event_id]
    with pytest.raises(ValueError):
        ledger.revoke(a.event_id)


def test_retracted_observation_cannot_be_reviewed(tmp_path: Path):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    obs = observation(store)
    store.append(obs.retract(Provenance(model="human")))
    ledger = IdentityReviewLedger(store, {"P1"}, max_frame=100, fps=30)
    with pytest.raises(ValueError, match="observation"):
        ledger.confirm(obs.event_id, "P1", 5, 10)


def test_generic_event_verification_cannot_rewrite_review_identity(tmp_path: Path):
    from bai_badminton.plugin import BadmintonSession

    store = EventStore(tmp_path / "events.sqlite", "S1")
    obs = observation(store)
    review = IdentityReviewLedger(store, {"P1"}, max_frame=100, fps=30).confirm(obs.event_id, "P1", 5, 10)
    session = BadmintonSession.__new__(BadmintonSession)
    from types import SimpleNamespace

    session.store = store
    session.engine = SimpleNamespace(on_superseded=lambda event: None)
    session._emit = lambda events: None
    result = session.handle(
        {"cmd": "verify_event", "event_id": review.event_id, "payload": {"participant_id": "participant-bad-000001"}}
    )
    assert result["ok"] is False
    assert store.get(review.event_id).payload["participant_id"] == obs.payload["participant_id"]
    assert IdentityReviewLedger(store, {"P1"}, max_frame=100, fps=30).current()[0].event_id == review.event_id


def test_retracting_source_observation_invalidates_review(tmp_path: Path):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    obs = observation(store)
    ledger = IdentityReviewLedger(store, {"P1"}, max_frame=100, fps=30)
    ledger.confirm(obs.event_id, "P1", 5, 10)
    store.append(obs.retract(Provenance(model="human")))
    assert ledger.current() == []


def test_superseded_source_invalidates_review(tmp_path: Path):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    obs = observation(store)
    ledger = IdentityReviewLedger(store, {"P1"}, max_frame=100, fps=30)
    ledger.confirm(obs.event_id, "P1", 5, 10)
    store.append(obs.correct(payload={**obs.payload, "track_id": 2}))
    assert ledger.current() == []


@pytest.mark.parametrize("instance", [None, "abcd"])
def test_epoch_reset_boundary_rejected_even_without_new_instance(tmp_path: Path, instance):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    obs = observation(store)
    store.append(
        Event(
            session_id="S1",
            type="identity_ambiguity",
            frame_start=8,
            frame_end=8,
            pts_us=0,
            payload={"reason": "visual_tracker_reset", "tracker_instance": instance},
            provenance=Provenance(model="participant_tracker_v1"),
        )
    )
    ledger = IdentityReviewLedger(store, {"P1"}, max_frame=100, fps=30)
    with pytest.raises(ValueError, match="epoch"):
        ledger.confirm(obs.event_id, "P1", 5, 10)


def test_later_epoch_evidence_invalidates_review(tmp_path: Path):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    obs = observation(store)
    ledger = IdentityReviewLedger(store, {"P1"}, max_frame=100, fps=30)
    ledger.confirm(obs.event_id, "P1", 5, 10)
    store.append(
        Event(
            session_id="S1",
            type="identity_ambiguity",
            frame_start=8,
            frame_end=8,
            pts_us=0,
            payload={"reason": "visual_tracker_reset"},
            provenance=Provenance(model="participant_tracker_v1"),
        )
    )
    assert ledger.current() == []


def test_generic_verification_cannot_rewrite_tracker_reset(tmp_path: Path) -> None:
    from types import SimpleNamespace

    from bai_badminton.plugin import BadmintonSession

    store = EventStore(tmp_path / "events.sqlite", "S1")
    obs = observation(store)
    ledger = IdentityReviewLedger(store, {"P1"}, max_frame=100, fps=30)
    ledger.confirm(obs.event_id, "P1", 5, 10)
    reset = store.append(
        Event(
            session_id="S1",
            type="identity_ambiguity",
            frame_start=8,
            frame_end=8,
            pts_us=0,
            payload={"reason": "visual_tracker_reset", "tracker_instance": "efgh"},
            provenance=Provenance(model="participant_tracker_v1"),
        )
    )
    assert ledger.current() == []
    session = BadmintonSession.__new__(BadmintonSession)
    session.store = store
    session.engine = SimpleNamespace(on_superseded=lambda event: None)
    session._emit = lambda events: None
    result = session.handle(
        {"cmd": "verify_event", "event_id": reset.event_id, "payload": {"reason": "none", "tracker_instance": "abcd"}}
    )
    assert result["ok"] is False
    assert ledger.current() == []


@pytest.mark.parametrize("event_type", ["identity_ambiguity", "participant_observation", "stroke_participant_review"])
def test_tracker_evidence_is_never_carried_to_a_new_analysis(tmp_path: Path, event_type: str) -> None:
    from bai_badminton.engine import BadmintonMatchEngine, EngineConfig

    old = EventStore(tmp_path / "old.sqlite", "S1")
    event = old.append(
        Event(
            session_id="S1",
            type=event_type,
            frame_start=10,
            frame_end=10,
            pts_us=0,
            payload={"tracker_instance": "old", "reason": "multiple_court_tracks"},
            status=EventStatus.HUMAN_VERIFIED,
            provenance=Provenance(model="human"),
        )
    )
    new = EventStore(tmp_path / "new.sqlite", "S1")
    current = new.append(
        Event(
            session_id="S1",
            type=event_type,
            frame_start=10,
            frame_end=10,
            pts_us=0,
            payload={"tracker_instance": "new", "reason": "visual_tracker_reset"},
            provenance=Provenance(model="participant_tracker_v1"),
        )
    )
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), new)
    assert engine.carry_over([event], Provenance(model="human")) == 0
    assert new.query(types=[event_type])[0].event_id == current.event_id


def test_reanalysis_preserves_new_stroke_episode_when_carrying_old_classification(tmp_path: Path) -> None:
    from bai_badminton.engine import BadmintonMatchEngine, EngineConfig

    old = EventStore(tmp_path / "old_stroke.sqlite", "S1")
    previous = old.append(
        Event(
            session_id="S1",
            type="stroke",
            frame_start=10,
            frame_end=10,
            pts_us=0,
            payload={
                "stroke": "drop",
                "participant_hypothesis": {"participant_id": "participant-old-000001", "track_id": 1},
            },
            status=EventStatus.HUMAN_VERIFIED,
            provenance=Provenance(model="human"),
        )
    )
    new = EventStore(tmp_path / "new_stroke.sqlite", "S1")
    hypothesis = {"participant_id": "participant-new-000002", "track_id": 2, "status": "provisional"}
    new.append(
        Event(
            session_id="S1",
            type="stroke",
            frame_start=10,
            frame_end=10,
            pts_us=0,
            payload={"stroke": "clear", "participant_hypothesis": hypothesis},
            provenance=Provenance(model="stroke_rules_v0"),
        )
    )
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), new)
    assert engine.carry_over([previous], Provenance(model="human")) == 1
    current = new.query(types=["stroke"])[0]
    assert current.payload["stroke"] == "drop"
    assert current.payload["participant_hypothesis"] == hypothesis


def test_worker_generic_verify_rejects_scoped_participant_review(tmp_path: Path) -> None:
    from types import SimpleNamespace

    from bai_badminton.plugin import BadmintonSession

    store = EventStore(tmp_path / "guard.sqlite", "S1")
    event = store.append(
        Event(
            session_id="S1",
            type="stroke_participant_review",
            frame_start=10,
            frame_end=10,
            pts_us=0,
            payload={"scope": "participant_only"},
            status=EventStatus.HUMAN_VERIFIED,
            provenance=Provenance(model="human"),
        )
    )
    session = BadmintonSession.__new__(BadmintonSession)
    session.store = store
    session.engine = SimpleNamespace(on_superseded=lambda event: None)
    session._emit = lambda events: None
    result = session.handle({"cmd": "verify_event", "event_id": event.event_id, "payload": {"player_id": "U2"}})
    assert result["ok"] is False
    assert store.get(event.event_id).payload == {"scope": "participant_only"}


@pytest.mark.parametrize(
    "kind,payload",
    [
        ("identity_ambiguity", {"reason": "visual_tracker_reset"}),
        (
            "participant_observation",
            {"kind": "PLAYER_EXITED", "participant_id": "participant-abcd-000001", "track_id": 1},
        ),
        (
            "participant_observation",
            {"kind": "PARTICIPANT_FIRST_OBSERVED", "participant_id": "participant-other-000002", "track_id": 1},
        ),
    ],
)
def test_same_frame_boundary_after_birth_invalidates_identity_review(tmp_path: Path, kind, payload):
    store = EventStore(tmp_path / "sameframe.sqlite", "S1")
    obs = observation(store)
    ledger = IdentityReviewLedger(store, {"P1"}, max_frame=100, fps=30)
    ledger.confirm(obs.event_id, "P1", obs.frame_start, 20)
    store.append(
        Event(
            session_id="S1",
            type=kind,
            frame_start=obs.frame_start,
            frame_end=obs.frame_start,
            pts_us=0,
            payload=payload,
            provenance=Provenance(model="participant_tracker_v1"),
        )
    )
    assert ledger.current() == []
    with pytest.raises(ValueError):
        ledger.confirm(obs.event_id, "P1", obs.frame_start, 20)


def test_same_frame_reset_before_birth_starts_valid_new_epoch(tmp_path: Path):
    store = EventStore(tmp_path / "sameframe-new.sqlite", "S1")
    store.append(
        Event(
            session_id="S1",
            type="identity_ambiguity",
            frame_start=5,
            frame_end=5,
            pts_us=0,
            payload={"reason": "visual_tracker_reset"},
            provenance=Provenance(model="participant_tracker_v1"),
        )
    )
    obs = observation(store)
    ledger = IdentityReviewLedger(store, {"P1"}, max_frame=100, fps=30)
    review = ledger.confirm(obs.event_id, "P1", 5, 20)
    assert [e.event_id for e in ledger.current()] == [review.event_id]


def test_worker_rejects_generic_hypothesis_rewrite_but_accepts_label_correction(tmp_path: Path):
    from types import SimpleNamespace
    from bai_badminton.plugin import BadmintonSession

    store = EventStore(tmp_path / "verify.sqlite", "S1")
    hypothesis = {"participant_id": "participant-abcd-000001", "track_id": 1, "observation_id": "birth-one"}
    event = store.append(Event(session_id="S1", type="stroke", frame_start=10, frame_end=10, pts_us=0,
                               payload={"stroke": "drive", "participant_hypothesis": hypothesis},
                               provenance=Provenance(model="stroke_rules_v0")))
    session = BadmintonSession.__new__(BadmintonSession)
    session.store = store
    session.engine = SimpleNamespace(on_superseded=lambda _event: None)
    session._emit = lambda _events: None
    rejected = session.handle({"cmd": "verify_event", "event_id": event.event_id,
                               "payload": {"participant_hypothesis": {**hypothesis, "observation_id": "forged"}}})
    assert rejected["ok"] is False
    assert store.get(event.event_id).payload["participant_hypothesis"] == hypothesis
    accepted = session.handle({"cmd": "verify_event", "event_id": event.event_id, "payload": {"stroke": "clear"}})
    assert accepted["ok"] is True
    corrected = store.get(accepted["event_id"])
    assert corrected.payload["stroke"] == "clear"
    assert corrected.payload["participant_hypothesis"] == hypothesis
