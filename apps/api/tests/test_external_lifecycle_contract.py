"""External ownership must not look like an acknowledged stop or an in-process bus."""

import pytest
from pydantic import ValidationError

from bai_engine.config import Settings
from bai_engine.schema import Session, SessionStatus, Source, SourceKind


def test_external_engine_requires_shared_command_transport():
    with pytest.raises(ValidationError, match="redis"):
        Settings(engine_mode="external", redis_url=None, _env_file=None)


def test_external_session_deletion_preserves_records_without_stop_acknowledgement(client, monkeypatch):
    repo = client.app.state.repo
    session = repo.save(Session(
        title="External active writer", status=SessionStatus.ANALYSING,
        source=Source(kind=SourceKind.UPLOAD, uri="controlled.mp4"),
    ))
    repo.events(session.session_id).set_meta("evidence", "preserve")
    monkeypatch.setattr(client.app.state, "engine", None)
    response = client.delete(f"/api/sessions/{session.session_id}")
    assert response.status_code == 409
    assert repo.get(session.session_id) is not None
    assert repo.events(session.session_id).get_meta("evidence") == "preserve"
