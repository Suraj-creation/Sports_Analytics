"""Product projections keep one committed revision and accepted point semantics."""

from pathlib import Path

import pytest

from apps.web.e2e.score_fixture import create_score_fixture
from bai_api.analytics import AnalyticsCache
from bai_api.product_analytics import insights, overview
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.match_phase import PhaseParams
from bai_engine.schema import EventStatus, Provenance
from bai_engine.store import EventStore, SessionRepository


def _correct_after_fold(repo, cache, fixture, monkeypatch):
    """Commit through another WAL connection between the fold and its consumers."""
    sid = fixture["session_id"]
    before_seq = repo.events(sid).last_seq()
    get = cache.get
    revisions = {"before": before_seq}

    def get_then_correct(session_id):
        result = get(session_id)
        if "after" not in revisions:
            with EventStore(repo.events(sid).path, sid) as writer:
                engine = BadmintonMatchEngine(
                    sid,
                    EngineConfig(
                        fps=30,
                        frame_width=1280,
                        frame_height=720,
                        phase=PhaseParams(allow_heuristic_official=True),
                    ),
                    writer,
                )
                engine.restore_from_log(fixture["frame"] + 1)
                engine.correct_rally_winner(fixture["rally_event_ids"][1], "P1", Provenance(model="human"))
                revisions["after"] = writer.last_seq()
        return result

    monkeypatch.setattr(cache, "get", get_then_correct)
    return revisions


def test_insights_keeps_fold_evidence_and_lineage_in_one_committed_revision(tmp_path: Path, monkeypatch):
    with_repo = SessionRepository(tmp_path / "data")
    try:
        fixture = create_score_fixture(with_repo, "test-none")
        sid = fixture["session_id"]
        cache = AnalyticsCache(with_repo)
        revisions = _correct_after_fold(with_repo, cache, fixture, monkeypatch)
        data = insights(with_repo, cache, with_repo.get(sid))
        assert len(data["rallies"]) == 2
        assert all(rally["score_available"] for rally in data["rallies"])
        assert (data["rallies"][-1]["score_after"], data["lineage"]["event_seq"]) in (
            ({"P1": 1, "P2": 1}, revisions["before"]),
            ({"P1": 2, "P2": 0}, revisions["after"]),
        )
    finally:
        with_repo.close()


def test_overview_lineage_identifies_the_fold_that_was_returned(tmp_path: Path, monkeypatch):
    repo = SessionRepository(tmp_path / "data")
    try:
        fixture = create_score_fixture(repo, "test-none")
        cache = AnalyticsCache(repo)
        revisions = _correct_after_fold(repo, cache, fixture, monkeypatch)
        match = overview(repo, cache).matches[0]
        assert match.analytics is not None
        assert (match.analytics["players"]["P1"]["points_won"], match.lineage.event_seq) in (
            (1, revisions["before"]),
            (2, revisions["after"]),
        )
    finally:
        repo.close()


@pytest.mark.parametrize("invalid", ["provisional", "retracted", "unknown_winner"])
def test_tactical_point_rates_ignore_rally_winners_without_accepted_decisions(tmp_path: Path, invalid):
    repo = SessionRepository(tmp_path / "data")
    try:
        fixture = create_score_fixture(repo, "test-none")
        sid = fixture["session_id"]
        store = repo.events(sid)
        for point in store.query(types=["point"]):
            if invalid == "retracted":
                replacement = point.retract(Provenance(model="human"), "fixture review")
            else:
                replacement = point.correct(
                    status=EventStatus.PROVISIONAL if invalid == "provisional" else EventStatus.CONFIRMED,
                    payload=point.payload if invalid == "provisional" else {**point.payload, "winner": None},
                )
            store.append(replacement)
        data = insights(repo, AnalyticsCache(repo), repo.get(sid))
        assert all(not rally["score_available"] for rally in data["rallies"])
        # Keep observed service/return activity, but do not turn it into points.
        assert sum(row["serves"] for row in data["tactics"].values()) > 0
        for row in data["tactics"].values():
            assert row["serve_points_won"] == row["return_points_won"] == 0
            assert row["serve_win_rate"] is row["return_win_rate"] is None
            assert all(bucket["rallies"] == bucket["points_won"] == 0 for bucket in row["rally_length"])
    finally:
        repo.close()


def test_tactical_point_rates_retain_accepted_decisions(tmp_path: Path):
    repo = SessionRepository(tmp_path / "data")
    try:
        fixture = create_score_fixture(repo, "test-none")
        sid = fixture["session_id"]
        data = insights(repo, AnalyticsCache(repo), repo.get(sid))
        assert all(rally["score_available"] for rally in data["rallies"])
        for row in data["tactics"].values():
            assert sum(bucket["rallies"] for bucket in row["rally_length"]) == 2
            assert sum(bucket["points_won"] for bucket in row["rally_length"]) == 1
    finally:
        repo.close()
