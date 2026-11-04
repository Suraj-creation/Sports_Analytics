"""Concurrent readers must join one committed rally/point history, never two revisions."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event

from apps.web.e2e.score_fixture import create_score_fixture
from bai_badminton.analytics.rebuild import rally_records
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.match_phase import PhaseParams
from bai_engine.schema import Provenance
from bai_engine.store import EventStore, SessionRepository


def test_analysis_snapshot_keeps_rally_and_point_queries_in_one_revision(tmp_path: Path, monkeypatch) -> None:
    repo = SessionRepository(tmp_path / "data")
    try:
        fixture = create_score_fixture(repo, "test-none", media=False)
        sid = fixture["session_id"]
        reader = repo.events(sid)
        with EventStore(reader.path, sid) as writer:
            engine = BadmintonMatchEngine(
                sid,
                EngineConfig(
                    fps=30, frame_width=1280, frame_height=720,
                    phase=PhaseParams(allow_heuristic_official=True),
                ),
                writer,
            )
            engine.restore_from_log(fixture["frame"] + 1)
            read_rallies, continue_read = Event(), Event()
            query = reader.query

            def pause_after_rallies(**kwargs):
                rows = query(**kwargs)
                if kwargs.get("types") == ["rally_end"] and not read_rallies.is_set():
                    read_rallies.set()
                    if not continue_read.wait(timeout=10):
                        raise TimeoutError("The concurrent correction did not finish")
                return rows

            monkeypatch.setattr(reader, "query", pause_after_rallies)

            def read_history():
                with repo.analysis_snapshot(sid) as (_, store, _):
                    return rally_records(store)

            with ThreadPoolExecutor(max_workers=1) as workers:
                pending = workers.submit(read_history)
                try:
                    assert read_rallies.wait(timeout=10), "Reader did not reach the rally/point boundary"
                    # A separate WAL connection can commit while a read snapshot is
                    # open, so the regression does not depend on same-object locks.
                    engine.correct_rally_winner(
                        fixture["rally_event_ids"][1], "P1", Provenance(model="human"),
                    )
                    assert engine.public_state()["score"] == {"P1": 2, "P2": 0}
                finally:
                    continue_read.set()
                records = pending.result(timeout=10)

            assert len(records) == 2
            assert all(record.score_available for record in records), "Mixed revisions lost a valid point parent"
            assert [record.score_after for record in records] in (
                [{"P1": 1, "P2": 0}, {"P1": 1, "P2": 1}],
                [{"P1": 1, "P2": 0}, {"P1": 2, "P2": 0}],
            )
            with repo.analysis_snapshot(sid) as (_, store, _):
                current = rally_records(store)
            assert [record.score_after for record in current] == [
                {"P1": 1, "P2": 0}, {"P1": 2, "P2": 0},
            ]
    finally:
        repo.close()
