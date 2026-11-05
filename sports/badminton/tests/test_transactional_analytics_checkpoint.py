"""Journal isolation, correction order and opaque checkpoints; no sporting labels."""

from copy import deepcopy

import pytest

from bai_badminton.analytics.match import RallyRecord
from bai_badminton.components import TransactionalAnalytics
from bai_engine.schema import Actors, Event, Provenance


def stroke(label="smash", player="P1"):
    return Event(
        session_id="checkpoint",
        type="stroke",
        frame_start=1,
        frame_end=1,
        pts_us=33333,
        actors=Actors(player_id=player),
        provenance=Provenance(model="controlled-fixture"),
        payload={"stroke": label},
    )


def rally(*, duration=1.0, official=True, winner=None):
    return RallyRecord(
        "r",
        1,
        0,
        30,
        winner,
        "P2",
        "unknown",
        [{"stroke": "clear", "frame": 1}],
        {"P1": 0, "P2": 0},
        1,
        {},
        duration,
        official=official,
        score_available=winner is not None,
    )


def test_mutating_original_event_after_append_cannot_change_future_restore():
    aggregate = TransactionalAnalytics(30)
    event = stroke()
    aggregate.on_stroke(event)
    before = deepcopy(aggregate.to_public())
    event.payload["stroke"] = "clear"
    checkpoint = aggregate.checkpoint()
    aggregate.reset()
    aggregate.restore(checkpoint)
    assert aggregate.to_public() == before


@pytest.mark.parametrize("official", [True, False])
def test_mutating_original_rally_cannot_change_retained_projection(official):
    aggregate = TransactionalAnalytics(30)
    record = rally(official=official)
    aggregate.on_rally(record)
    before = deepcopy(aggregate.to_public())
    record.duration_s = 999.0
    record.shots.append({"stroke": "smash"})
    assert aggregate.to_public() == before


def test_checkpoint_does_not_deepcopy_or_replay_existing_history(monkeypatch):
    import bai_badminton.components as components

    aggregate = TransactionalAnalytics(30)
    for _ in range(100):
        aggregate.on_stroke(stroke())

    def fail(*_args, **_kwargs):
        pytest.fail("checkpoint must not copy historical operations")

    monkeypatch.setattr(components.copy, "deepcopy", fail)
    assert aggregate.checkpoint() is not None


def test_reset_keeps_old_checkpoint_restorable_without_cloning_the_provider():
    aggregate = TransactionalAnalytics(30)
    aggregate.on_stroke(stroke())
    before = deepcopy(aggregate.to_public())
    checkpoint = aggregate.checkpoint()
    aggregate.reset()
    assert aggregate.to_public()["shot_accounting"]["total"] == 0
    aggregate.restore(checkpoint)
    assert aggregate.to_public() == before


def test_correction_retraction_and_branched_checkpoints_replay_in_exact_order():
    aggregate = TransactionalAnalytics(30)
    event = stroke()
    aggregate.on_stroke(event)
    first = aggregate.checkpoint()
    original = deepcopy(aggregate.to_public())
    aggregate.on_stroke_retracted(event)
    aggregate.on_stroke(stroke("clear"))
    second = aggregate.checkpoint()
    corrected = deepcopy(aggregate.to_public())
    aggregate.restore(first)
    assert aggregate.to_public() == original
    aggregate.on_stroke(stroke("drive"))
    aggregate.restore(second)
    assert aggregate.to_public() == corrected
    aggregate.restore(first)
    assert aggregate.to_public() == original


def test_caller_mutation_of_retracted_event_cannot_rewrite_journal():
    aggregate = TransactionalAnalytics(30)
    event = stroke()
    aggregate.on_stroke(event)
    aggregate.on_stroke_retracted(event)
    event.payload["stroke"] = "clear"
    expected = deepcopy(aggregate.to_public())
    checkpoint = aggregate.checkpoint()
    aggregate.restore(checkpoint)
    assert aggregate.to_public() == expected


def test_presence_input_is_copied_at_the_append_boundary():
    aggregate = TransactionalAnalytics(30)
    points = [[0, 0], [0, 1]]
    aggregate.on_presence("P1", points)
    points.append([0, 2])
    expected = deepcopy(aggregate.to_public())
    checkpoint = aggregate.checkpoint()
    aggregate.reset()
    aggregate.restore(checkpoint)
    assert aggregate.to_public() == expected


def test_foreign_checkpoint_is_rejected_without_mutating_current_state():
    aggregate = TransactionalAnalytics(30)
    aggregate.on_stroke(stroke())
    before = deepcopy(aggregate.to_public())
    with pytest.raises(ValueError, match="incompatible"):
        aggregate.restore(TransactionalAnalytics(30).checkpoint())
    assert aggregate.to_public() == before


def test_failed_operation_does_not_poison_checkpoint_history(monkeypatch):
    from bai_badminton.analytics.match import MatchAnalytics

    aggregate = TransactionalAnalytics(30)
    aggregate.on_stroke(stroke())
    before = deepcopy(aggregate.to_public())
    original = MatchAnalytics.on_rally

    def fail_after_mutation(self, record):
        original(self, record)
        raise OSError("injected projection failure after append")

    monkeypatch.setattr(MatchAnalytics, "on_rally", fail_after_mutation)
    with pytest.raises(OSError, match="injected"):
        aggregate.on_rally(rally())
    assert aggregate.to_public() == before
    checkpoint = aggregate.checkpoint()
    aggregate.restore(checkpoint)
    assert aggregate.to_public() == before


def test_empty_checkpoint_and_repeated_restore_are_exact():
    aggregate = TransactionalAnalytics(30)
    before = deepcopy(aggregate.to_public())
    empty = aggregate.checkpoint()
    aggregate.on_stroke(stroke())
    aggregate.restore(empty)
    aggregate.restore(empty)
    assert aggregate.to_public() == before


def test_close_does_not_invalidate_an_existing_checkpoint():
    aggregate = TransactionalAnalytics(30)
    aggregate.on_rally(rally())
    before = deepcopy(aggregate.to_public())
    checkpoint = aggregate.checkpoint()
    aggregate.close()
    aggregate.restore(checkpoint)
    assert aggregate.to_public() == before
