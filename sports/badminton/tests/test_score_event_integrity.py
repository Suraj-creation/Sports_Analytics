"""Sporting decisions, durable score history and retry behavior stay consistent.

The outcome fixture bypasses perception accuracy, while exercising the real phase,
rule, event, SQLite, correction and restoration implementations.
"""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, _Contact, _PendingRally
from bai_badminton.events.contact import ContactCandidate
from bai_badminton.events.match_phase import RallyEvidence
from bai_badminton.events.rally_fsm import RallySegment
from bai_engine.schema import EventStatus, Provenance
from bai_engine.store import EventStore


def _engine(tmp_path: Path, monkeypatch, *, emit=None):
    store = EventStore(tmp_path / "score.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store, emit=emit)
    monkeypatch.setattr(engine, "_outcome", lambda seg: ("winner", "far", "fixture_observed_rest", 0.85))
    monkeypatch.setattr(engine, "_phase_evidence", lambda seg, until: RallyEvidence(scoreboard="changed"))
    return engine, store


def _pending(start=10, end=20):
    return _PendingRally(RallySegment(start, end, None, "stationary"), [], None)


@pytest.mark.parametrize("boundary", ["point", "snapshot"])
def test_failed_point_publication_rolls_back_and_keeps_the_rally_retryable(tmp_path, monkeypatch, boundary):
    delivered = []
    engine, store = _engine(tmp_path, monkeypatch, emit=delivered.extend)
    with store:
        engine._pending = [_pending()]
        before = engine.public_state()
        append, snapshot = store.append_many, store.put_state

        def fail_point(events):
            events = list(events)
            if any(event.type == "point" for event in events):
                raise OSError("injected point persistence failure")
            return append(events)

        def fail_snapshot(snap):
            raise OSError("injected snapshot persistence failure")

        monkeypatch.setattr(store, "append_many", fail_point if boundary == "point" else append)
        monkeypatch.setattr(store, "put_state", fail_snapshot if boundary == "snapshot" else snapshot)
        with pytest.raises(OSError, match="injected"):
            engine._finalize_pending(100)

        assert store.query() == []
        assert store.states() == []
        assert delivered == []
        assert engine.public_state() == before
        assert engine._last_rally_end is None
        assert len(engine._pending) == 1

        monkeypatch.setattr(store, "append_many", append)
        monkeypatch.setattr(store, "put_state", snapshot)
        engine._finalize_pending(100)
        assert engine.state.score == {"P1": 1, "P2": 0}
        assert len(store.query(types=["rally_end"])) == len(store.query(types=["point"])) == 1
        assert store.state_at(100).state["score"] == {"P1": 1, "P2": 0}
        assert engine._pending == []


def test_failed_correction_keeps_old_history_and_can_be_retried(tmp_path, monkeypatch):
    engine, store = _engine(tmp_path, monkeypatch)
    with store:
        engine._pending = [_pending(), _pending(40, 50)]
        engine._finalize_pending(100)
        first = store.query(types=["rally_end"])[0]
        old_events, old_states = store.since(), store.states()
        old_public = engine.public_state()
        snapshot = store.put_state

        def fail_snapshot(snap):
            raise OSError("injected correction failure")

        monkeypatch.setattr(store, "put_state", fail_snapshot)
        with pytest.raises(OSError, match="injected correction"):
            engine.correct_rally_winner(first.event_id, "P2", Provenance(model="human"))
        assert store.since() == old_events
        assert store.states() == old_states
        assert engine.public_state() == old_public
        assert engine._rallies[0].observed_winner == "P1"
        assert engine._rallies[0].override is None

        monkeypatch.setattr(store, "put_state", snapshot)
        engine.correct_rally_winner(first.event_id, "P2", Provenance(model="human"))
        assert engine.state.score == {"P1": 1, "P2": 1}
        assert len(store.query(types=["point"])) == 2
        restored = BadmintonMatchEngine("S1", engine.cfg, store)
        restored.restore_from_log(100)
        assert restored.public_state() == engine.public_state()


def test_retry_after_snapshot_failure_reclassifies_the_last_contact_from_durable_evidence(tmp_path, monkeypatch):
    engine, store = _engine(tmp_path, monkeypatch)
    with store:
        contact_event = store.append(engine._event("contact", 10, 10, model="fixture_contact"))
        pending = _pending()
        pending.contacts.append(_Contact(ContactCandidate(10, "P1", 0.8), contact_event))
        engine._pending = [pending]
        snapshot = store.put_state

        def fail_snapshot(snap):
            raise OSError("injected snapshot failure")

        monkeypatch.setattr(store, "put_state", fail_snapshot)
        with pytest.raises(OSError, match="injected"):
            engine._finalize_pending(100)
        assert store.query(types=["stroke"]) == []
        assert engine._pending[0].contacts[0].stroke_event is None
        assert engine._pending[0].contacts[0].event.event_id == contact_event.event_id

        monkeypatch.setattr(store, "put_state", snapshot)
        engine._finalize_pending(100)
        stroke = store.query(types=["stroke"])[0]
        contact = store.query(types=["contact"])[0]
        assert stroke.payload["contact_event_id"] == contact_event.event_id
        assert contact.payload["stroke_event_id"] == stroke.event_id
        assert store.query(types=["rally_end"])[0].payload["shots"][0]["event_id"] == stroke.event_id
        assert len(store.query(types=["point"])) == 1


def test_restore_does_not_promote_an_orphan_rally_winner_to_a_point(tmp_path, monkeypatch):
    engine, store = _engine(tmp_path, monkeypatch)
    with store:
        store.append(engine._event(
            "rally_end", 10, 20,
            payload={"official": True, "winner": "P1", "observed_winner": "P1", "phase_override": None},
            status=EventStatus.CONFIRMED, model="rally_outcome_v1",
        ))
        restored = BadmintonMatchEngine("S1", engine.cfg, store)
        assert restored.restore_from_log(100) == 1
        assert restored.state.score == {"P1": 0, "P2": 0}
        assert restored.state.rally_no == 0
        assert store.query(types=["point"]) == []


def test_restore_accepts_a_corrected_point_revision(tmp_path, monkeypatch):
    engine, store = _engine(tmp_path, monkeypatch)
    with store:
        engine._pending = [_pending()]
        engine._finalize_pending(100)
        point = store.query(types=["point"])[0]
        store.append(point.correct(payload=point.payload))
        restored = BadmintonMatchEngine("S1", engine.cfg, store)
        restored.restore_from_log(100)
        assert restored.state.score == {"P1": 1, "P2": 0}
        assert restored.state.rally_no == 1


def test_unrelated_review_and_second_reload_cannot_promote_an_orphan_point(tmp_path, monkeypatch):
    engine, store = _engine(tmp_path, monkeypatch)
    with store:
        orphan = store.append(engine._event(
            "rally_end", 10, 20,
            payload={"official": True, "winner": "P1", "observed_winner": "P1", "phase_override": True},
            status=EventStatus.CONFIRMED, model="rally_outcome_v1",
        ))
        engine._pending = [_pending(40, 50)]
        engine._finalize_pending(100)
        reviewed = store.query(types=["rally_end"])[1]
        for winner in ("P2", "P1"):
            restored = BadmintonMatchEngine("S1", engine.cfg, store)
            restored.restore_from_log(100)
            restored.correct_rally_winner(reviewed.event_id, winner, Provenance(model="human"))
            assert len(store.query(types=["point"])) == 1
            assert restored.state.score == ({"P1": 0, "P2": 1} if winner == "P2" else {"P1": 1, "P2": 0})
        restored.correct_rally_winner(orphan.event_id, "P2", Provenance(model="human"))
        assert restored.state.score == {"P1": 1, "P2": 1}
        assert len(store.query(types=["point"])) == 2


def test_duplicate_pending_rally_contributes_exactly_one_point(tmp_path, monkeypatch):
    engine, store = _engine(tmp_path, monkeypatch)
    with store:
        engine._pending = [_pending(), _pending()]
        engine._finalize_pending(100)
        assert engine.state.score == {"P1": 1, "P2": 0}
        assert len(store.query(types=["rally_end"])) == len(store.query(types=["point"])) == 1


def test_pending_rallies_are_applied_in_video_order(tmp_path, monkeypatch):
    engine, store = _engine(tmp_path, monkeypatch)
    with store:
        monkeypatch.setattr(
            engine, "_outcome",
            lambda seg: ("winner", "near" if seg.start == 10 else "far", "fixture_observed_rest", 0.85),
        )
        engine._pending = [_pending(40, 50), _pending()]
        engine._finalize_pending(100)
        points = store.query(types=["point"])
        assert [event.payload["rally_no"] for event in points] == [1, 2]
        assert [event.payload["state_after"]["score"] for event in points] == [
            {"P1": 0, "P2": 1}, {"P1": 1, "P2": 1},
        ]
        assert engine.state.server == "P1"


def test_delivery_observes_committed_point_and_snapshot(tmp_path, monkeypatch):
    observed = []
    engine, store = _engine(tmp_path, monkeypatch)
    with store:
        def delivered(events):
            observed.append((engine.public_state()["score"], store.state_at(100), len(store.query(types=["point"]))))

        engine._emit_cb = delivered
        engine._pending = [_pending()]
        engine._finalize_pending(100)
        assert observed
        assert all(score == {"P1": 1, "P2": 0} and snap is not None and count == 1 for score, snap, count in observed)


def test_notification_failure_cannot_make_a_committed_point_retry(tmp_path, monkeypatch):
    def broken_delivery(events):
        raise RuntimeError("injected subscriber failure")

    engine, store = _engine(tmp_path, monkeypatch, emit=broken_delivery)
    with store:
        engine._pending = [_pending()]
        engine._finalize_pending(100)
        assert engine.state.score == {"P1": 1, "P2": 0}
        assert len(store.query(types=["point"])) == 1
        assert engine._pending == []


def test_retrying_the_same_review_decision_does_not_append_another_revision(tmp_path, monkeypatch):
    engine, store = _engine(tmp_path, monkeypatch)
    with store:
        engine._pending = [_pending()]
        engine._finalize_pending(100)
        original = store.query(types=["rally_end"])[0]
        engine.correct_rally_winner(original.event_id, "P2", Provenance(model="human"))
        seq = store.last_seq()
        assert engine.correct_rally_winner(original.event_id, "P2", Provenance(model="human")) == []
        assert store.last_seq() == seq
        assert engine.state.score == {"P1": 0, "P2": 1}


def test_concurrent_reviews_keep_both_point_decisions_and_restore_the_same_score(tmp_path, monkeypatch):
    engine, store = _engine(tmp_path, monkeypatch)
    with store:
        engine._pending = [_pending(), _pending(40, 50)]
        engine._finalize_pending(100)
        rallies = store.query(types=["rally_end"])
        ready = Barrier(2)

        def review(event):
            ready.wait(timeout=5)
            engine.correct_rally_winner(event.event_id, "P2", Provenance(model="human"))

        with ThreadPoolExecutor(max_workers=2) as executor:
            list(executor.map(review, rallies))
        assert engine.state.score == {"P1": 0, "P2": 2}
        assert len(store.query(types=["point"])) == 2
        assert store.state_at(100).state["score"] == {"P1": 0, "P2": 2}
        restored = BadmintonMatchEngine("S1", engine.cfg, store)
        restored.restore_from_log(100)
        assert restored.public_state() == engine.public_state()


def test_carry_over_cannot_copy_an_old_human_point_snapshot_over_the_current_score(tmp_path, monkeypatch):
    engine, store = _engine(tmp_path, monkeypatch)
    with store:
        engine._pending = [_pending()]
        engine._finalize_pending(100)
        point = store.query(types=["point"])[0]
        old_review = point.correct(
            payload={
                **point.payload,
                "state_after": {**point.payload["state_after"], "score": {"P1": 7, "P2": 0}},
            },
            status=EventStatus.HUMAN_VERIFIED,
        )
        seq = store.last_seq()
        assert engine.carry_over([old_review], Provenance(model="human")) == 0
        assert store.last_seq() == seq
        assert store.query(types=["point"])[0].payload["state_after"]["score"] == {"P1": 1, "P2": 0}
        assert store.state_at(100).state["score"] == engine.state.score == {"P1": 1, "P2": 0}
