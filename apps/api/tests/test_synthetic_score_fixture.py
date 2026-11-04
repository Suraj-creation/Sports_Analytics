"""Transport fixtures use explicit review labels, not inferred physical names."""

from apps.web.e2e.score_fixture import create_score_fixture
from bai_badminton.analytics.rebuild import rally_records
from bai_badminton.testing.synth import make_match
from bai_engine.schema import EventStatus
from bai_engine.store import SessionRepository


def test_reviewed_fixture_counts_each_label_once_and_retains_review_provenance(tmp_path):
    repo = SessionRepository(tmp_path / "data")
    try:
        fixture = create_score_fixture(repo, "test-none")
        store = repo.events(fixture["session_id"])
        records = rally_records(store)
        expected = make_match(["P1", "P2"])
        assert fixture["score"] == {"P1": 1, "P2": 1}
        assert [len(rally.shots) for rally in records] == [len(rally.contacts) for rally in expected.rallies]
        assert [event.payload["serve_frame"] for event in store.query(types=["rally_end"])] == [
            offset + rally.contacts[0][0]
            for offset, rally in zip(expected.offsets, expected.rallies, strict=True)
        ]
        owned = [shot["event_id"] for rally in records for shot in rally.shots]
        assert len(owned) == len(set(owned))
        for ident in owned:
            event = store.get(ident)
            assert event.status is EventStatus.HUMAN_VERIFIED
            assert event.provenance.model == "human"
            assert event.payload["fixture_source"] == "synthetic-contact-label"
        original_rallies = [event for event in store.query(types=["rally_end"], live_only=False)
                            if event.supersedes is None]
        original_owned = {shot["event_id"] for rally in original_rallies for shot in rally.payload["shots"]
                          if shot.get("event_id")}
        live_ids = {event.event_id for event in store.query(types=["stroke"])}
        assert original_owned, "The fixture must exercise replacement of actual anonymous inferred strokes"
        assert original_owned.isdisjoint(live_ids)
    finally:
        repo.close()
