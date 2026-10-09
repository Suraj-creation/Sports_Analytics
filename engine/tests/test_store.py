from pathlib import Path

import pytest

from bai_engine.schema import (
    ConfidenceBand,
    Event,
    EventStatus,
    Provenance,
    Session,
    SessionStatus,
    Source,
    SourceKind,
    StateSnapshot,
    TrackObject,
    TrackSample,
    current_view,
    samples_to_table,
    table_to_samples,
)
from bai_engine.store import EventStore, SessionRepository, TrackStore

PROV = Provenance(model="rule:test")


def ev(sid: str, t: str = "contact", f: int = 10, **kw: object) -> Event:
    return Event(
        session_id=sid, type=t, frame_start=f, frame_end=kw.pop("fe", f), pts_us=f * 33_334, provenance=PROV, **kw
    )  # type: ignore[arg-type]


class TestEventModel:
    def test_band_thresholds(self) -> None:
        assert ConfidenceBand.from_confidence(0.9) is ConfidenceBand.CONFIRMED
        assert ConfidenceBand.from_confidence(0.7) is ConfidenceBand.PROBABLE
        assert ConfidenceBand.from_confidence(0.2) is ConfidenceBand.UNCERTAIN
        assert ConfidenceBand.from_confidence(None) is ConfidenceBand.UNKNOWN

    def test_invalid_frames(self) -> None:
        with pytest.raises(ValueError):
            ev("S1", f=10, fe=5)

    def test_corrected_requires_supersedes(self) -> None:
        with pytest.raises(ValueError):
            ev("S1", status=EventStatus.CORRECTED)

    def test_invalid_type(self) -> None:
        with pytest.raises(ValueError):
            ev("S1", t="bad type!")

    def test_correct_and_fold(self) -> None:
        a = ev("S1", payload={"stroke": "clear"})
        b = a.correct(payload={"stroke": "smash"}, confidence=0.9)
        c = ev("S1", f=30)
        live = current_view([a, b, c])
        assert [e.event_id for e in live] == [b.event_id, c.event_id]
        assert live[0].payload["stroke"] == "smash"
        r = c.retract(PROV)
        assert [e.event_id for e in current_view([a, b, c, r])] == [b.event_id]


class TestEventStore:
    def test_append_seq_and_since(self, tmp_path: Path) -> None:
        store = EventStore(tmp_path / "e.sqlite", "S1")
        e1, e2 = store.append_many([ev("S1", f=1), ev("S1", f=2)])
        assert (e1.seq, e2.seq) == (1, 2)
        assert [e.event_id for e in store.since(1)] == [e2.event_id]
        assert store.last_seq() == 2

    def test_rejects_foreign_session_and_unknown_supersedes(self, tmp_path: Path) -> None:
        store = EventStore(tmp_path / "e.sqlite", "S1")
        with pytest.raises(ValueError):
            store.append(ev("S2"))
        orphan = ev("S1").correct()
        with pytest.raises(KeyError):
            store.append(orphan)

    def test_query_folds_corrections_outside_window(self, tmp_path: Path) -> None:
        store = EventStore(tmp_path / "e.sqlite", "S1")
        a = store.append(ev("S1", t="stroke", f=100, payload={"stroke": "drop"}))
        # correction moves the event to frame 200 — querying the old window must not return stale 'a'
        store.append(a.correct(frame_start=200, frame_end=200, pts_us=200 * 33_334, payload={"stroke": "smash"}))
        assert store.query(types=["stroke"], frame_from=90, frame_to=110) == []
        moved = store.query(types=["stroke"], frame_from=190, frame_to=210)
        assert len(moved) == 1 and moved[0].payload["stroke"] == "smash"
        assert len(store.query(types=["stroke"], live_only=False)) == 2

    def test_query_filters(self, tmp_path: Path) -> None:
        store = EventStore(tmp_path / "e.sqlite", "S1")
        from bai_engine.schema import Actors

        store.append_many(
            [
                ev("S1", t="contact", f=10, actors=Actors(player_id="P1")),
                ev("S1", t="contact", f=20, actors=Actors(player_id="P2")),
                ev("S1", t="rally_end", f=30),
            ]
        )
        assert len(store.query(types=["contact"])) == 2
        assert [e.frame_start for e in store.query(player_id="P2")] == [20]
        assert store.query(types=[]) == []
        assert store.count("contact") == 2

    def test_state_at(self, tmp_path: Path) -> None:
        store = EventStore(tmp_path / "e.sqlite", "S1")
        for f, score in [(100, [1, 0]), (300, [1, 1]), (500, [2, 1])]:
            store.put_state(StateSnapshot(session_id="S1", frame_idx=f, state={"score": score}))
        assert store.state_at(50) is None
        snap = store.state_at(450)
        assert snap is not None and snap.state["score"] == [1, 1]
        assert len(store.states()) == 3

    def test_persists_across_reopen(self, tmp_path: Path) -> None:
        p = tmp_path / "e.sqlite"
        with EventStore(p, "S1") as s:
            s.append(ev("S1"))
            s.set_meta("frontier", "120")
        with EventStore(p, "S1") as s:
            assert s.count() == 1 and s.get_meta("frontier") == "120"


class TestTrackStore:
    def _samples(self, start: int, n: int) -> list[TrackSample]:
        return [
            TrackSample(
                frame_idx=start + i, obj=TrackObject.SHUTTLE, x=float(i), y=2.0 * i, conf=0.875, model="tracknetv3@1"
            )
            for i in range(n)
        ] + [
            TrackSample(
                frame_idx=start + i,
                obj=TrackObject.PLAYER,
                track_id=3,
                player_id="P1",
                bbox=(1, 2, 3, 4),
                keypoints=tuple((float(k), float(k), 0.5) for k in range(17)),
                conf=0.75,
            )
            for i in range(n)
        ]

    def test_roundtrip_conversion(self) -> None:
        s = self._samples(0, 3)
        assert table_to_samples(samples_to_table(s)) == s

    def test_write_read_range_and_revisions(self, tmp_path: Path) -> None:
        store = TrackStore(tmp_path)
        t = samples_to_table([x for x in self._samples(0, 60) if x.obj is TrackObject.SHUTTLE])
        store.write_chunk(TrackObject.SHUTTLE, 0, 59, t)
        t2 = samples_to_table([x for x in self._samples(60, 60) if x.obj is TrackObject.SHUTTLE])
        store.write_chunk(TrackObject.SHUTTLE, 60, 119, t2)
        out = store.read([TrackObject.SHUTTLE], 50, 70)
        assert out["frame_idx"].to_pylist() == list(range(50, 71))
        # refinement revision replaces chunk 0
        refined = samples_to_table(
            [TrackSample(frame_idx=i, obj=TrackObject.SHUTTLE, x=99.0, y=99.0, conf=1.0) for i in range(60)]
        )
        store.write_chunk(TrackObject.SHUTTLE, 0, 59, refined)
        assert set(store.read([TrackObject.SHUTTLE], 0, 10)["x"].to_pylist()) == {99.0}
        assert store.covered_ranges(TrackObject.SHUTTLE) == [(0, 119)]
        assert store.read([TrackObject.RACKET], 0, 10).num_rows == 0

    def test_rejects_rows_outside_chunk(self, tmp_path: Path) -> None:
        store = TrackStore(tmp_path)
        with pytest.raises(ValueError):
            store.write_chunk(TrackObject.SHUTTLE, 0, 9, samples_to_table(self._samples(5, 10)))


class TestSessionRepository:
    def test_crud_and_paths(self, tmp_path: Path) -> None:
        repo = SessionRepository(tmp_path)
        s = repo.save(Session(title="Axelsen v Momota", source=Source(kind=SourceKind.UPLOAD, uri="x.mp4")))
        assert repo.get(s.session_id) is not None
        repo.set_status(s.session_id, SessionStatus.ANALYSING, "chunk 3/90")
        got = repo.get(s.session_id)
        assert got is not None and got.status is SessionStatus.ANALYSING and got.status_detail == "chunk 3/90"
        repo.events(s.session_id).append(ev(s.session_id))
        assert repo.events(s.session_id).count() == 1
        assert [x.session_id for x in repo.list()] == [s.session_id]
        repo.delete(s.session_id)
        assert repo.get(s.session_id) is None
        assert not repo.paths(s.session_id).root.exists()

    def test_path_traversal_rejected(self, tmp_path: Path) -> None:
        repo = SessionRepository(tmp_path)
        with pytest.raises(ValueError):
            repo.paths("../etc")
        with pytest.raises(ValueError):
            repo.media_paths("../../x")
