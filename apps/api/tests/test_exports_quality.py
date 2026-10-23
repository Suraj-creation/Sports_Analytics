"""Unavailable evidence is not exported as a measured zero score."""

from bai_api.routes.exports import _rally_rows
from bai_engine.schema import Event, EventStatus, Provenance, Session, Source, SourceKind
from bai_engine.store import SessionRepository


def test_unresolved_score_exports_null_cells(tmp_path):
    repo = SessionRepository(tmp_path / "data")
    session = repo.save(Session(title="Partial footage", source=Source(kind=SourceKind.UPLOAD, uri="unused")))
    repo.events(session.session_id).append(
        Event(
            session_id=session.session_id,
            type="rally_end",
            frame_start=0,
            frame_end=30,
            pts_us=0,
            payload={"official": True, "rally_no": 1, "duration_s": 1.0, "winner": None, "shots": []},
            status=EventStatus.CONFIRMED,
            provenance=Provenance(model="rule:incomplete"),
        )
    )
    row = _rally_rows(session, repo)[0]
    assert row["score_P1"] is None
    assert row["score_P2"] is None
    assert row["score_available"] is False
