"""Q&A must retain physical uncertainty separately from finalized ledger status."""

import json

import pytest

from bai_agents.tools import ToolContext, run_tool
from bai_engine.schema import Event, EventStatus, MediaInfo, Provenance, Session, Source, SourceKind
from bai_engine.store import EventStore


@pytest.fixture
def evidence_context(tmp_path):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    contact = store.append(
        Event(
            session_id="S1",
            type="contact",
            frame_start=10,
            frame_end=10,
            pts_us=333333,
            payload={"physical_event_status": "ambiguous"},
            status=EventStatus.CONFIRMED,
            confidence=0.99,
            provenance=Provenance(model="contact-evidence-v1"),
        )
    )
    stroke = store.append(
        Event(
            session_id="S1",
            type="stroke",
            frame_start=10,
            frame_end=10,
            pts_us=333333,
            payload={
                "stroke": "unknown",
                "physical_event_status": "ambiguous",
                "physical_evidence_event_id": contact.event_id,
            },
            status=EventStatus.CONFIRMED,
            confidence=0.99,
            provenance=Provenance(model="stroke-v1"),
        )
    )
    rally = store.append(
        Event(
            session_id="S1",
            type="rally_end",
            frame_start=0,
            frame_end=50,
            pts_us=0,
            payload={"official": True, "rally_no": 1, "shots": [{"event_id": stroke.event_id}]},
            provenance=Provenance(model="rally-v1"),
        )
    )
    session = Session(
        session_id="S1",
        title="uncertainty contract",
        source=Source(kind=SourceKind.UPLOAD, uri="fixture"),
        media=MediaInfo(fps_num=30, fps_den=1, n_frames=60, width=1280, height=720, duration_us=2000000),
    )
    try:
        yield ToolContext(session=session, store=store, tracks=None), contact, stroke, rally
    finally:
        store.close()


def query(ctx, tool):
    result = json.loads(run_tool(ctx, tool, {"rally_no": 1} if tool == "get_rally" else {}))
    return result, result["shots" if tool == "get_rally" else "strokes"][0]


@pytest.mark.parametrize("tool", ["get_rally", "find_strokes"])
def test_finalized_high_support_event_keeps_ambiguous_impact_and_parent_citation(evidence_context, tool):
    ctx, contact, _, _ = evidence_context
    result, shot = query(ctx, tool)
    assert shot["status"] == "confirmed"
    assert shot["confidence"] == 0.99
    assert shot["analysis_frame"] == 10
    assert shot["frame_timebase"] == "analysis_proxy"
    assert shot["physical_event_status"] == "ambiguous"
    assert shot["physical_evidence_event_id"] == contact.event_id
    assert contact.event_id in result["evidence_ids"]
    assert "uncalibrated" in shot["confidence_semantics"]


@pytest.mark.parametrize("tool", ["get_rally", "find_strokes"])
@pytest.mark.parametrize(
    "invalid", ["retracted_parent", "superseded_parent", "wrong_frame", "conflicting_status", "legacy"]
)
def test_missing_stale_or_unaligned_physical_support_remains_unknown(evidence_context, tool, invalid):
    ctx, contact, stroke, _ = evidence_context
    if invalid == "retracted_parent":
        ctx.store.append(contact.correct(status=EventStatus.RETRACTED, provenance=Provenance(model="human")))
    elif invalid == "superseded_parent":
        ctx.store.append(contact.correct(payload={"physical_event_status": "probable"}))
    elif invalid == "wrong_frame":
        ctx.store.append(stroke.correct(frame_start=11, frame_end=11))
    elif invalid == "conflicting_status":
        ctx.store.append(stroke.correct(payload={**stroke.payload, "physical_event_status": "confirmed"}))
    else:
        ctx.store.append(stroke.correct(payload={"stroke": "clear"}, status=EventStatus.HUMAN_VERIFIED))
    result, shot = query(ctx, tool)
    assert shot["physical_event_status"] == "unknown"
    assert shot["physical_evidence_event_id"] is None
    assert contact.event_id not in result["evidence_ids"]
    assert shot["analysis_frame"] == (11 if invalid == "wrong_frame" else 10)


@pytest.mark.parametrize("source_fps,variable", [("24/1", False), ("25/1", False), ("30/1", True)])
def test_canonical_index_never_claims_an_unavailable_original_frame_mapping(evidence_context, source_fps, variable):
    ctx, _, _, _ = evidence_context
    ctx.session = ctx.session.model_copy(
        update={
            "media": ctx.session.media.model_copy(update={"source_fps": source_fps, "variable_frame_rate": variable}),
        }
    )
    _, shot = query(ctx, "get_rally")
    assert shot["analysis_frame"] == 10
    assert shot["frame_timebase"] == "analysis_proxy"
    assert "source_frame" not in shot
