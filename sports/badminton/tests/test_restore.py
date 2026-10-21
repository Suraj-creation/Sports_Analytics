"""Re-attaching to a finished analysis and carrying human inputs across a re-analysis."""

from pathlib import Path

from bai_badminton.analytics.rebuild import rally_records
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.testing.synth import make_match
from bai_engine.schema import Event, EventStatus, Provenance
from bai_engine.store import EventStore

WINNERS = ["P1", "P2", "P2", "P1", "P1", "P1", "P2", "P1"]
HUMAN = Provenance(model="human", worker="test")


def _analyse(store: EventStore) -> BadmintonMatchEngine:
    m = make_match(WINNERS)
    eng = BadmintonMatchEngine("S1", EngineConfig(fps=m.fps, frame_width=1280, frame_height=720), store)
    eng.set_calibration(0, m.homography)
    for ch in m.chunks:
        eng.ingest(ch)
    eng.flush()
    return eng


def _live_counts(store: EventStore) -> dict[str, int]:
    return {t: len(store.query(types=[t])) for t in ("rally_end", "point", "stroke", "contact")}


def test_restored_engine_applies_corrections_without_reanalysis(tmp_path: Path) -> None:
    store = EventStore(tmp_path / "e.sqlite", "S1")
    first = _analyse(store)
    before = _live_counts(store)
    final_frame = first._last_frame

    # a new process: fresh engine on the same log, nothing re-ingested
    eng = BadmintonMatchEngine("S1", EngineConfig(fps=first.cfg.fps, frame_width=1280, frame_height=720), store)
    assert eng.restore_from_log(final_frame) == len(WINNERS)
    assert eng.public_state()["score"] == first.public_state()["score"]
    assert eng.analytics.to_public()["rallies"] == len(WINNERS)

    third = store.query(types=["rally_end"])[2]
    eng.correct_rally_winner(third.event_id, "P1", HUMAN)
    expect = WINNERS[:2] + ["P1"] + WINNERS[3:]
    assert eng.public_state()["score"] == {"P1": expect.count("P1"), "P2": expect.count("P2")}
    assert _live_counts(store) == before  # corrected in place — nothing duplicated
    assert [r.payload["winner"] for r in store.query(types=["rally_end"])] == expect


def test_verified_rally_keeps_its_point(tmp_path: Path) -> None:
    store = EventStore(tmp_path / "e.sqlite", "S1")
    _analyse(store)
    r = store.query(types=["rally_end"])[0]
    store.append(r.correct(payload=r.payload, status=EventStatus.HUMAN_VERIFIED, provenance=HUMAN, confidence=1.0))
    recs = rally_records(store)
    # the point still belongs to the rally after the rally_end was superseded by its verification
    assert recs[0].score_after == {"P1": 1, "P2": 0}


def test_carry_over_reapplies_human_corrections_after_reanalysis(tmp_path: Path) -> None:
    old = EventStore(tmp_path / "old.sqlite", "S1")
    eng = _analyse(old)
    second = old.query(types=["rally_end"])[1]
    eng.correct_rally_winner(second.event_id, "P1", HUMAN)
    smash = old.query(types=["stroke"])[0]
    old.append(
        smash.correct(payload={**smash.payload, "stroke": "drop"}, status=EventStatus.HUMAN_VERIFIED, provenance=HUMAN)
    )
    human: list[Event] = [e for e in old.query() if e.status is EventStatus.HUMAN_VERIFIED]
    assert {e.type for e in human} == {"rally_end", "stroke"}

    new = EventStore(tmp_path / "new.sqlite", "S1")
    eng2 = _analyse(new)
    applied = eng2.carry_over(human, HUMAN)
    assert applied == 2
    expect = [WINNERS[0], "P1", *WINNERS[2:]]
    assert [r.payload["winner"] for r in new.query(types=["rally_end"])] == expect
    assert eng2.public_state()["score"] == {"P1": expect.count("P1"), "P2": expect.count("P2")}
    s0 = new.query(types=["stroke"])[0]
    assert s0.payload["stroke"] == "drop" and s0.status is EventStatus.HUMAN_VERIFIED
    # nothing to carry twice: re-applying is idempotent
    assert eng2.carry_over(human, HUMAN) == 0
