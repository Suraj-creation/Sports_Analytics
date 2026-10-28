"""Evaluation of automatic episode hypotheses using an independent identity map."""

import pytest

from research.participant_benchmark import evaluate_participants, validate_bindings
from research.tests.test_shot_benchmark import documents


def inputs():
    labels, predictions = documents()
    labels["shots"] = [
        {"time_s": 1, "family": "smash", "player_id": "alice"},
        {"time_s": 2, "family": "clear", "player_id": "bob"},
        {"time_s": 3, "family": "drive", "player_id": "alice"},
    ]
    predictions["shots"] = [
        {
            "time_s": 1.1,
            "family": "smash",
            "event_id": "e1",
            "participant_hypothesis": {
                "status": "provisional",
                "participant_id": "participant-abc-000001",
                "track_id": 1,
            },
        },
        {
            "time_s": 2.1,
            "family": "unknown",
            "event_id": "e2",
            "participant_hypothesis": {"status": "unresolved", "participant_id": None, "track_id": None},
        },
        {
            "time_s": 3.1,
            "family": "drive",
            "event_id": "e3",
            "participant_hypothesis": {
                "status": "provisional",
                "participant_id": "participant-abc-000002",
                "track_id": 2,
            },
        },
        {
            "time_s": 4,
            "family": "clear",
            "event_id": "e4",
            "participant_hypothesis": {
                "status": "provisional",
                "participant_id": "participant-abc-000001",
                "track_id": 1,
            },
        },
    ]
    predictions["event_log_sha256"] = "c" * 64
    bindings = {
        "schema_version": 1,
        "event_log_sha256": "c" * 64,
        "session_id": "S1",
        "media_sha256": "a" * 64,
        "timebase": "canonical_media_seconds",
        "window_s": [0, 10],
        "status": "reviewed",
        "review": {"human_verified": True, "independent_of_shot_labels": True, "exhaustive_for_window": True},
        "bindings": [
            {
                "participant_id": "participant-abc-000001",
                "player_id": "alice",
                "track_id": 1,
                "start_s": 0,
                "end_s": 10,
            },
            {"participant_id": "participant-abc-000002", "player_id": "bob", "track_id": 2, "start_s": 0, "end_s": 10},
        ],
    }
    return labels, predictions, bindings


def test_episode_selection_counts_correct_wrong_unresolved_and_spurious():
    labels, predictions, bindings = inputs()
    result = evaluate_participants(labels, predictions, bindings, tolerance_s=0.2)
    assert result["accuracy_claim_eligible"] is True
    assert result["counting_scope"] == "automatic_episode_hypotheses_conditioned_on_external_identity_bindings"
    assert result["shot_detection"]["matched"] == 3
    assert result["shot_detection"]["false_positives"] == 1
    assert result["participant"]["labelled_truth"] == 3
    assert result["participant"]["correct"] == 1
    assert result["participant"]["wrong"] == 1
    assert result["participant"]["unresolved"] == 1
    assert result["participant"]["accuracy_all_labelled_truth"] == pytest.approx(1 / 3)
    assert result["participant"]["accuracy_resolved_matched"] == pytest.approx(0.5)
    assert result["participant"]["resolved_fraction_matched"] == pytest.approx(2 / 3)
    assert result["shot_classification"]["per_class"]["smash"]["true_positive"] == 1


def test_missed_contact_remains_in_end_to_end_denominator():
    labels, predictions, bindings = inputs()
    predictions["shots"] = predictions["shots"][:1]
    result = evaluate_participants(labels, predictions, bindings)
    assert result["participant"]["unmatched_labelled_truth"] == 2
    assert result["participant"]["accuracy_all_labelled_truth"] == pytest.approx(1 / 3)
    assert result["participant"]["accuracy_resolved_matched"] == 1


@pytest.mark.parametrize(
    "which",
    [
        "source",
        "timebase",
        "window",
        "overlap",
        "person_overlap",
        "not_independent",
        "not_exhaustive",
        "same_track",
        "invalid_track",
    ],
)
def test_invalid_binding_document_fails_closed(which):
    labels, _, bindings = inputs()
    if which == "source":
        bindings["media_sha256"] = "b" * 64
    elif which == "timebase":
        bindings["timebase"] = "other"
    elif which == "window":
        bindings["window_s"] = [0, 9]
    elif which == "overlap":
        bindings["bindings"].append(
            {
                "participant_id": "participant-abc-000001",
                "player_id": "charlie",
                "track_id": 1,
                "start_s": 4,
                "end_s": 7,
            }
        )
    elif which == "person_overlap":
        bindings["bindings"][1]["player_id"] = "alice"
    elif which == "not_independent":
        bindings["review"]["independent_of_shot_labels"] = False
    elif which == "not_exhaustive":
        bindings["review"]["exhaustive_for_window"] = False
    elif which == "same_track":
        bindings["bindings"][1]["track_id"] = 1
    else:
        bindings["bindings"][0]["track_id"] = True
    with pytest.raises(ValueError):
        validate_bindings(labels, bindings)


def test_unreviewed_binding_requires_draft_opt_in_and_cannot_support_accuracy_claim():
    labels, predictions, bindings = inputs()
    bindings["status"] = "draft"
    bindings["review"]["human_verified"] = False
    with pytest.raises(ValueError, match="reviewed"):
        evaluate_participants(labels, predictions, bindings)
    assert evaluate_participants(labels, predictions, bindings, allow_draft=True)["accuracy_claim_eligible"] is False


def test_unknown_episode_or_track_mismatch_is_unresolved_not_wrong():
    labels, predictions, bindings = inputs()
    predictions["shots"][0]["participant_hypothesis"]["track_id"] = 9
    result = evaluate_participants(labels, predictions, bindings)
    assert result["participant"]["unresolved"] == 2
    assert result["participant"]["correct"] == 0


def test_reviewed_or_forged_hypothesis_cannot_enter_automatic_evaluation():
    labels, predictions, bindings = inputs()
    predictions["shots"][0]["participant_hypothesis"]["status"] = "human_verified"
    with pytest.raises(ValueError, match="automatic"):
        evaluate_participants(labels, predictions, bindings)


def test_session_extraction_is_machine_only_and_detects_retracted_human_edits(tmp_path):
    import json
    import sqlite3
    import subprocess
    import sys

    from bai_engine.schema.events import Actors, Event, EventStatus, Provenance
    from bai_engine.schema.session import MediaInfo, Session, Source, SourceKind
    from research.participant_benchmark import automatic_predictions_from_session

    labels, _, bindings = inputs()
    session = Session(
        session_id="S1",
        title="Test",
        source=Source(kind=SourceKind.UPLOAD, uri="source.mp4", sha256="a" * 64),
        media=MediaInfo(fps_num=30, fps_den=1, n_frames=300, width=1280, height=720, duration_us=10000000),
    )
    with sqlite3.connect(tmp_path / "sessions.sqlite") as conn:
        conn.execute("CREATE TABLE sessions (session_id TEXT, body TEXT)")
        conn.execute("INSERT INTO sessions VALUES (?, ?)", ("S1", session.model_dump_json()))
    session_dir = tmp_path / "sessions" / "S1"
    session_dir.mkdir(parents=True)
    event = Event(
        session_id="S1",
        type="stroke",
        frame_start=30,
        frame_end=30,
        pts_us=1000000,
        actors=Actors(player_id="P2"),
        status=EventStatus.CONFIRMED,
        provenance=Provenance(model="stroke_rules_v0"),
        payload={
            "stroke": "smash",
            "participant_hypothesis": {
                "status": "provisional",
                "participant_id": "participant-abc-000001",
                "track_id": 1,
            },
        },
    )
    with sqlite3.connect(session_dir / "events.sqlite") as conn:
        conn.execute("CREATE TABLE events (seq INTEGER, body TEXT)")
        conn.execute("INSERT INTO events VALUES (?, ?)", (1, event.model_dump_json()))
    predictions = automatic_predictions_from_session(tmp_path, "S1", labels)
    bindings["event_log_sha256"] = predictions["event_log_sha256"]
    result = evaluate_participants(labels, predictions, bindings)
    # The matching independent episode map wins over the deliberately wrong legacy P2 score slot.
    assert result["participant"]["correct"] == 1
    annotations = tmp_path / "labels.json"
    mapping = tmp_path / "bindings.json"
    annotations.write_text(json.dumps(labels))
    mapping.write_text(json.dumps(bindings))
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.participant_benchmark",
            "--session",
            "S1",
            "--annotations",
            str(annotations),
            "--bindings",
            str(mapping),
            "--data-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(completed.stdout)
    assert report["participant"]["correct"] == 1
    assert report["provenance"]["event_log_sha256"] == predictions["event_log_sha256"]
    retraction = event.retract(Provenance(model="human"), "incorrect contact")
    with sqlite3.connect(session_dir / "events.sqlite") as conn:
        conn.execute("INSERT INTO events VALUES (?, ?)", (2, retraction.model_dump_json()))
    with pytest.raises(ValueError, match="machine-only"):
        automatic_predictions_from_session(tmp_path, "S1", labels)


def test_bindings_must_match_the_exact_evaluated_event_log():
    labels, predictions, bindings = inputs()
    bindings["event_log_sha256"] = "d" * 64
    with pytest.raises(ValueError, match="event log hash mismatch"):
        evaluate_participants(labels, predictions, bindings)
    bindings.pop("event_log_sha256")
    with pytest.raises(ValueError, match="event log hash required"):
        evaluate_participants(labels, predictions, bindings)


def test_empty_identity_labels_cannot_support_participant_accuracy_claim():
    labels, predictions, bindings = inputs()
    for shot in labels["shots"]:
        shot["player_id"] = None
    result = evaluate_participants(labels, predictions, bindings)
    assert result["participant"]["labelled_truth"] == 0
    assert result["participant"]["accuracy_all_labelled_truth"] is None
    assert result["accuracy_claim_eligible"] is False
