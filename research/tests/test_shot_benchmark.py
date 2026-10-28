"""Tests for a source-bound, one-to-one shot evaluation."""

import pytest

from research.shot_benchmark import evaluate, validate_inputs


def documents():
    common = {"session_id": "S1", "media_sha256": "a" * 64, "timebase": "canonical_media_seconds", "window_s": [0, 10]}
    labels = {
        **common,
        "schema_version": 1,
        "status": "reviewed",
        "split": "held_out",
        "exhaustive": True,
        "review": {"human_verified": True},
        "shots": [
            {"time_s": 1, "family": "smash", "player_id": "P1"},
            {"time_s": 2, "family": "clear", "player_id": "P2"},
            {"time_s": 3, "family": "unknown", "player_id": None},
        ],
    }
    predictions = {
        **common,
        "schema_version": 1,
        "shots": [
            {"time_s": 1.1, "family": "smash", "player_id": "P1", "event_id": "e1"},
            {"time_s": 2.1, "family": "unknown", "player_id": None, "event_id": "e2"},
            {"time_s": 4, "family": "clear", "player_id": "P1", "event_id": "e3"},
        ],
    }
    return labels, predictions


def test_metrics_count_missed_and_spurious_and_unresolved():
    labels, predictions = documents()
    result = evaluate(labels, predictions, tolerance_s=0.2)
    assert result["matched"] == 2
    assert result["false_positives"] == result["false_negatives"] == 1
    assert result["confusion"]["smash"]["smash"] == 1
    assert result["confusion"]["clear"]["unknown"] == 1
    assert result["confusion"]["unknown"]["__missed__"] == 1
    assert result["confusion"]["__spurious__"]["clear"] == 1
    assert result["per_class"]["clear"]["recall"] == 0
    assert result["per_class"]["clear"]["precision"] == 0
    assert result["attribution"]["labelled"] == 2
    assert result["attribution"]["correct"] == 1
    assert result["attribution"]["unresolved"] == 1
    assert result["attribution"]["accuracy_all_labelled"] == 0.5
    assert result["timestamp_mae_s"] == pytest.approx(0.1)
    assert result["accuracy_claim_eligible"] is True


def test_matching_is_one_to_one_and_optimizes_count_before_distance():
    labels, predictions = documents()
    labels["shots"] = [{"time_s": 1, "family": "smash"}, {"time_s": 1.2, "family": "clear"}]
    predictions["shots"] = [
        {"time_s": 1.1, "family": "smash", "event_id": "a"},
        {"time_s": 1.3, "family": "clear", "event_id": "b"},
    ]
    assert evaluate(labels, predictions, tolerance_s=0.2)["matched"] == 2


@pytest.mark.parametrize(
    "change,error",
    [
        ({"session_id": "S2"}, "session"),
        ({"media_sha256": "b" * 64}, "media"),
        ({"window_s": [0, 9]}, "window"),
    ],
)
def test_prediction_source_binding(change, error):
    labels, predictions = documents()
    predictions.update(change)
    with pytest.raises(ValueError, match=error):
        validate_inputs(labels, predictions)


def test_draft_requires_opt_in_and_never_supports_accuracy_claim():
    labels, predictions = documents()
    labels["status"] = "draft"
    with pytest.raises(ValueError, match="reviewed"):
        evaluate(labels, predictions)
    assert evaluate(labels, predictions, allow_draft=True)["accuracy_claim_eligible"] is False


def test_development_and_unverified_labels_are_not_held_out_evidence():
    labels, predictions = documents()
    labels["split"] = "development"
    assert evaluate(labels, predictions)["accuracy_claim_eligible"] is False
    labels["review"]["human_verified"] = False
    with pytest.raises(ValueError, match="human"):
        evaluate(labels, predictions)


def test_duplicate_prediction_event_and_outside_window_rejected():
    labels, predictions = documents()
    predictions["shots"][1]["event_id"] = "e1"
    with pytest.raises(ValueError, match="duplicate"):
        evaluate(labels, predictions)
    labels, predictions = documents()
    labels["shots"][0]["time_s"] = 11
    with pytest.raises(ValueError, match="window"):
        evaluate(labels, predictions)


def test_reads_current_session_event_ledger_and_validates_source(tmp_path):
    import sqlite3

    from bai_engine.schema.events import Actors, Event, EventStatus, Provenance
    from bai_engine.schema.session import MediaInfo, Session, Source, SourceKind
    from research.shot_benchmark import predictions_from_session

    labels, _ = documents()
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
        actors=Actors(player_id="P1"),
        payload={"stroke": "smash"},
        status=EventStatus.CONFIRMED,
        provenance=Provenance(model="test"),
    )
    correction = event.correct(payload={"stroke": "clear"})
    provisional = Event(
        session_id="S1",
        type="stroke",
        frame_start=60,
        frame_end=60,
        pts_us=2000000,
        status=EventStatus.PROVISIONAL,
        provenance=Provenance(model="test"),
    )
    with sqlite3.connect(session_dir / "events.sqlite") as conn:
        conn.execute("CREATE TABLE events (seq INTEGER, body TEXT)")
        conn.executemany(
            "INSERT INTO events VALUES (?, ?)",
            [(i, e.model_dump_json()) for i, e in enumerate([event, correction, provisional], 1)],
        )
    result = predictions_from_session(tmp_path, "S1", labels)
    assert len(result["shots"]) == 1
    assert result["shots"][0]["family"] == "clear"
    assert result["shots"][0]["event_id"] == correction.event_id
    assert len(result["event_log_sha256"]) == 64
    labels["media_sha256"] = "b" * 64
    with pytest.raises(ValueError, match="binding"):
        predictions_from_session(tmp_path, "S1", labels)


def test_fractional_media_fps_predictions_can_be_evaluated(tmp_path):
    import json
    import sqlite3
    import subprocess
    import sys

    from bai_engine.schema.events import Event, EventStatus, Provenance
    from bai_engine.schema.session import MediaInfo, Session, Source, SourceKind
    from research.shot_benchmark import predictions_from_session

    labels, _ = documents()
    session = Session(
        session_id="S1",
        title="Test",
        source=Source(kind=SourceKind.UPLOAD, uri="source.mp4", sha256="a" * 64),
        media=MediaInfo(fps_num=30000, fps_den=1001, n_frames=300, width=1280, height=720, duration_us=10010000),
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
        pts_us=1001000,
        payload={"stroke": "smash"},
        status=EventStatus.CONFIRMED,
        provenance=Provenance(model="test"),
    )
    with sqlite3.connect(session_dir / "events.sqlite") as conn:
        conn.execute("CREATE TABLE events (seq INTEGER, body TEXT)")
        conn.execute("INSERT INTO events VALUES (?, ?)", (1, event.model_dump_json()))
    predictions = predictions_from_session(tmp_path, "S1", labels)
    result = evaluate(labels, predictions)
    assert result["matched"] == 1
    assert result["matches"][0]["prediction_time_s"] == pytest.approx(1.001)
    annotations = tmp_path / "labels.json"
    annotations.write_text(json.dumps(labels))
    cli = subprocess.run(
        [
            sys.executable,
            "research/shot_benchmark.py",
            "--session",
            "S1",
            "--annotations",
            str(annotations),
            "--data-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(cli.stdout)["matched"] == 1


@pytest.mark.parametrize("review", [None, "reviewed", []])
def test_review_metadata_must_be_a_mapping(review):
    labels, predictions = documents()
    labels["review"] = review
    with pytest.raises(ValueError, match="human"):
        evaluate(labels, predictions)
