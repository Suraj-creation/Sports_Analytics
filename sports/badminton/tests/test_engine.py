from pathlib import Path

import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.testing.synth import make_match
from bai_engine.schema import Event, EventStatus, Provenance
from bai_engine.store import EventStore

WINNERS = ["P1", "P2", "P2", "P1", "P1", "P1", "P2", "P1"]


@pytest.fixture
def run(tmp_path: Path) -> tuple[BadmintonMatchEngine, EventStore, list[Event]]:
    m = make_match(WINNERS)
    store = EventStore(tmp_path / "e.sqlite", "S1")
    seen: list[Event] = []
    eng = BadmintonMatchEngine(
        "S1", EngineConfig(fps=m.fps, frame_width=1280, frame_height=720), store, emit=seen.extend
    )
    eng.set_calibration(0, m.homography)
    for ch in m.chunks:
        eng.ingest(ch)
    eng.flush()
    return eng, store, seen


def test_rallies_points_and_score(run: tuple[BadmintonMatchEngine, EventStore, list[Event]]) -> None:
    eng, store, _ = run
    rallies = store.query(types=["rally_end"])
    assert len(rallies) == len(WINNERS)
    got = [r.payload["winner"] for r in rallies]
    assert got == WINNERS
    points = store.query(types=["point"])
    assert len(points) == len(WINNERS)
    final = eng.public_state()
    assert final["score"] == {"P1": WINNERS.count("P1"), "P2": WINNERS.count("P2")}
    assert final["server"] == WINNERS[-1]
    # every point cites its rally_end as evidence and parent
    ids = {r.event_id for r in rallies}
    assert all(p.parent_id in ids for p in points)


def test_contacts_and_strokes(run: tuple[BadmintonMatchEngine, EventStore, list[Event]]) -> None:
    _, store, _ = run
    contacts = store.query(types=["contact"])
    strokes = store.query(types=["stroke"])
    assert len(strokes) >= 0.8 * len(contacts) > 0
    assert all(c.status in (EventStatus.CONFIRMED, EventStatus.PROVISIONAL) for c in contacts)
    # each stroke references its contact
    cids = {c.payload.get("stroke_event_id") for c in contacts}
    assert sum(1 for s in strokes if s.event_id in cids) >= 0.8 * len(strokes)
    serves = [s for s in strokes if s.payload["is_serve"]]
    assert len(serves) >= len(WINNERS) - 1


def test_states_and_checkpoints(run: tuple[BadmintonMatchEngine, EventStore, list[Event]]) -> None:
    eng, store, _ = run
    snaps = store.states("match")
    assert len(snaps) == len(WINNERS)
    mid = snaps[3]
    assert store.state_at(mid.frame_idx + 1).state == mid.state  # type: ignore[union-attr]
    assert store.states("checkpoint")


def test_emit_callback_receives_seq(run: tuple[BadmintonMatchEngine, EventStore, list[Event]]) -> None:
    _, store, seen = run
    assert [e.seq for e in seen] == list(range(1, store.last_seq() + 1))


def test_analytics(run: tuple[BadmintonMatchEngine, EventStore, list[Event]]) -> None:
    eng, _, _ = run
    a = eng.analytics.to_public()
    assert a["rallies"] == len(WINNERS)
    assert a["players"]["P1"]["points_won"] == WINNERS.count("P1")
    assert eng.analytics.heatmaps.to_public("P1", "presence")["total"] > 0
    hl = eng.analytics.highlights(k=3)
    assert len(hl) <= 3


def test_winner_correction_refolds(run: tuple[BadmintonMatchEngine, EventStore, list[Event]]) -> None:
    eng, store, _ = run
    first = store.query(types=["rally_end"])[0]
    eng.correct_rally_winner(first.event_id, "P2", Provenance(model="human"))
    rallies = store.query(types=["rally_end"])
    assert rallies[0].payload["winner"] == "P2" and rallies[0].status is EventStatus.HUMAN_VERIFIED
    assert len(store.query(types=["point"])) == len(WINNERS)
    expect = ["P2", *WINNERS[1:]]
    assert eng.public_state()["score"] == {"P1": expect.count("P1"), "P2": expect.count("P2")}
    last_point = store.query(types=["point"])[-1]
    assert last_point.payload["state_after"]["score"] == eng.public_state()["score"]


def test_uncalibrated_rallies_have_unknown_winner(tmp_path: Path) -> None:
    m = make_match(["P1", "P2"])
    store = EventStore(tmp_path / "e.sqlite", "S1")
    eng = BadmintonMatchEngine("S1", EngineConfig(fps=m.fps, frame_width=1280, frame_height=720), store)
    for ch in m.chunks:
        eng.ingest(ch)
    eng.flush()
    rallies = store.query(types=["rally_end"])
    assert len(rallies) == 2
    assert all(r.payload["winner"] is None and r.payload["rule_check"] == "uncalibrated" for r in rallies)
    assert store.query(types=["point"]) == []


def test_cancelled_short_rally_retracts_contacts_and_strokes(tmp_path: Path) -> None:
    from bai_badminton.perception_types import ChunkPerception
    from bai_badminton.testing.synth import make_rally, to_frames

    r = make_rally(n_shots=3, shot_frames=12, lead_in=30, tail=60)  # ~1.2 s of play < 2 s minimum
    frames = to_frames(r, 0)
    store = EventStore(tmp_path / "e.sqlite", "S1")
    eng = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    eng.set_calibration(0, r.homography)
    eng.ingest(ChunkPerception(start=0, end=len(frames) - 1, frames=frames))
    eng.flush()
    assert store.query(types=["rally_end"]) == []
    assert store.query(types=["contact"]) == []
    assert store.query(types=["stroke"]) == [], "strokes of a cancelled rally must be retracted"
