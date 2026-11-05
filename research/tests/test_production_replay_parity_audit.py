"""Parity audit controls; no sporting labels, providers or model calls."""

import copy

import pytest

from research.production_replay_parity_audit import compare_live


def event(identity, *, kind="contact", frame=10, seq=1, status="confirmed", supersedes=None):
    return {
        "event_id": identity,
        "session_id": "FRESH",
        "type": kind,
        "frame_start": frame,
        "frame_end": frame,
        "seq": seq,
        "status": status,
        "supersedes": supersedes,
        "actors": {"player_id": None},
        "payload": {"physical_event_status": "ambiguous"},
        "provenance": {"model": "real-scorer", "profile": "experiment"},
    }


def test_only_recorded_identity_origins_session_and_profile_are_normalized():
    fresh = event("fresh")
    replay = {
        **copy.deepcopy(fresh),
        "event_id": "replay",
        "session_id": "REPLAY",
        "provenance": {"model": "real-scorer", "profile": "diagnostic"},
    }
    assert compare_live([fresh], [replay])["differences"] == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("physical_event_status", "confirmed"),
        ("pose_observation_frames", [11]),
        ("stroke", "smash"),
        ("support", 0.50001),
        ("unrecognized_id", "another-arbitrary-id"),
    ],
)
def test_physical_cue_label_numeric_and_unknown_identity_changes_remain_visible(field, value):
    fresh = event("fresh")
    replay = {**copy.deepcopy(fresh), "event_id": "replay"}
    replay["payload"][field] = value
    result = compare_live([fresh], [replay])
    assert len(result["differences"]) == 1
    assert "/payload/" + field in [d["path"] for d in result["differences"][0]["differences"]]


def test_current_corrections_match_and_historical_parent_references_remain_resolved():
    fresh = [event("old"), event("new", seq=2, status="corrected", supersedes="old")]
    replay = [event("rold"), event("rnew", seq=2, status="corrected", supersedes="rold")]
    assert compare_live(fresh, replay)["differences"] == []
    assert compare_live(fresh, replay)["fresh_live_counts"] == {"contact": 1}


def test_multiple_current_events_at_same_frame_are_retained():
    fresh = [event("a"), event("b", seq=2)]
    replay = [event("x")]
    result = compare_live(fresh, replay)
    assert result["fresh_live_counts"] == {"contact": 2}
    assert result["differences"][0]["cause"] == "live event multiplicity differs"


def test_producer_provenance_model_is_not_dropped_as_identity_noise():
    fresh, replay = event("a"), event("b")
    replay["provenance"]["model"] = "recorded-format"
    result = compare_live([fresh], [replay])
    assert result["differences"][0]["differences"][0]["path"] == "/provenance/model"


def test_participant_identity_is_resolved_from_recorded_origin_and_track():
    fresh_origin = event("observation", kind="participant_observation")
    fresh_origin["payload"] = {"participant_id": "FRESH-PERSON", "track_id": 12}
    replay_origin = copy.deepcopy(fresh_origin)
    replay_origin["event_id"] = "replay-observation"
    replay_origin["payload"]["participant_id"] = "REPLAY-PERSON"
    fresh_contact, replay_contact = event("contact", seq=2), event("replay-contact", seq=2)
    fresh_contact["payload"]["attribution_target"] = "FRESH-PERSON"
    replay_contact["payload"]["attribution_target"] = "REPLAY-PERSON"
    assert not compare_live([fresh_origin, fresh_contact], [replay_origin, replay_contact])["differences"]
    replay_origin["payload"]["track_id"] = 99
    assert compare_live([fresh_origin, fresh_contact], [replay_origin, replay_contact])["differences"]


def test_event_reference_lists_are_resolved_and_nonidentity_text_is_preserved():
    fresh, replay = event("contact"), event("replay-contact")
    fresh_highlight = event("h", kind="highlight", seq=2)
    replay_highlight = event("rh", kind="highlight", seq=2)
    fresh_highlight["payload"]["evidence_ids"] = ["contact"]
    replay_highlight["payload"]["evidence_ids"] = ["replay-contact"]
    fresh_highlight["payload"]["literal_label"] = "contact"
    replay_highlight["payload"]["literal_label"] = "contact"
    assert not compare_live([fresh, fresh_highlight], [replay, replay_highlight])["differences"]
