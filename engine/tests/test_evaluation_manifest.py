"""Evaluation must bind labels to actual media and preserve review uncertainty."""

import hashlib
import json
import sqlite3
import sys

import pytest

from bai_engine.schema.session import MediaInfo, Session, Source, SourceKind
from research.evaluate_session import load_annotations


@pytest.fixture
def sample(tmp_path):
    session = Session(
        session_id="EVAL",
        title="Evaluation",
        source=Source(kind=SourceKind.UPLOAD, uri="source.mp4", sha256="a" * 64),
        media=MediaInfo(fps_num=30000, fps_den=1001, n_frames=300, width=1280, height=720, duration_us=10010000),
    )
    labels = {
        "schema_version": 1,
        "media_sha256": "a" * 64,
        "timebase": "canonical_media_seconds",
        "status": "draft",
        "split": "diagnostic",
        "population": "all_exchanges",
        "exhaustive": True,
        "window_s": [0, 10],
        "rallies": [{"start_s": 1, "end_s": 8}],
    }
    return session, labels, tmp_path / "annotations.json"


def test_draft_cannot_silently_become_accuracy_evidence(sample):
    session, labels, path = sample
    path.write_text(json.dumps(labels))
    with pytest.raises(ValueError, match="draft annotations"):
        load_annotations(path, session)
    assert load_annotations(path, session, allow_draft=True)["status"] == "draft"


@pytest.mark.parametrize(
    "key,value,error",
    [
        ("media_sha256", "b" * 64, "hash"),
        ("timebase", "wall_clock", "canonical"),
        ("window_s", [0, 11], "exceeds"),
        ("exhaustive", False, "exhaustively"),
        ("split", "", "split"),
        ("population", "everything", "population"),
        ("rallies", [{"start_s": 1, "end_s": 12}], "outside"),
    ],
)
def test_incompatible_evidence_is_rejected(sample, key, value, error):
    session, labels, path = sample
    labels[key] = value
    path.write_text(json.dumps(labels))
    with pytest.raises(ValueError, match=error):
        load_annotations(path, session, allow_draft=True)


def test_reviewed_heldout_manifest_accepts_rational_media_timebase(sample):
    session, labels, path = sample
    labels.update(status="reviewed", split="held_out", review={"human_verified": True})
    path.write_text(json.dumps(labels))
    assert load_annotations(path, session)["window_s"] == [0, 10]


@pytest.mark.parametrize("review", [None, {}, {"human_verified": False}, {"human_verified": "true"}])
def test_reviewed_rally_labels_require_explicit_human_attestation(sample, review):
    session, labels, path = sample
    labels.update(status="reviewed", split="held_out", review=review)
    path.write_text(json.dumps(labels))
    with pytest.raises(ValueError, match="human verification"):
        load_annotations(path, session, allow_draft=True)


def test_unrecognized_annotation_status_is_not_admitted_as_draft(sample):
    session, labels, path = sample
    labels["status"] = "unverified"
    path.write_text(json.dumps(labels))
    with pytest.raises(ValueError, match="status must be reviewed or draft"):
        load_annotations(path, session, allow_draft=True)


def test_v1_preserves_descriptive_metadata_without_changing_review_scope(sample):
    session, labels, path = sample
    labels.update(
        boundary_uncertainty_s=0.5,
        notes="One fully reviewed window; winner remains unobservable.",
        provenance={"annotation_revision": "manual-v1"},
        review={"human_verified": False, "method": "frame stepping", "limitations": ["blur"]},
    )
    labels["rallies"][0].update(notes="Exact winner unknown", provenance={"reviewer": "reviewer-1"})
    path.write_text(json.dumps(labels))

    actual = load_annotations(path, session, allow_draft=True)

    assert actual["boundary_uncertainty_s"] == 0.5
    assert actual["notes"] == "One fully reviewed window; winner remains unobservable."
    assert actual["provenance"] == {"annotation_revision": "manual-v1"}
    assert actual["review"]["limitations"] == ["blur"]
    assert actual["rallies"][0]["provenance"] == {"reviewer": "reviewer-1"}


@pytest.mark.parametrize(
    "key,value",
    [
        ("reviewed_windows_s", [[0, 4], [6, 10]]),
        ("unreviewed_intervals_s", [[4, 6]]),
        ("excluded_intervals_s", [[4, 6]]),
        ("unknown_intervals_s", [[4, 6]]),
        ("unreviewed", True),
        ("exhaustive_for_window", False),
        ("unexpected_semantics", "unknown"),
    ],
)
def test_v1_rejects_unsupported_temporal_coverage_instead_of_scoring_it_as_negative(sample, key, value):
    session, labels, path = sample
    labels.update(status="reviewed", review={"human_verified": True}, rallies=[])
    labels[key] = value
    path.write_text(json.dumps(labels))

    with pytest.raises(ValueError):
        load_annotations(path, session)


@pytest.mark.parametrize(
    "key,value",
    [
        ("status", "unknown"),
        ("review_status", "unreviewed"),
        ("existence", "unknown"),
        ("occurrence_status", "uncertain"),
        ("contact_status", "possible_not_confirmed"),
        ("unreviewed", True),
        ("unknown", True),
        ("unexpected_semantics", "unknown"),
    ],
)
def test_v1_rejects_unsupported_row_semantics_instead_of_creating_positive_truth(sample, key, value):
    session, labels, path = sample
    labels.update(status="reviewed", review={"human_verified": True})
    labels["rallies"][0][key] = value
    path.write_text(json.dumps(labels))

    with pytest.raises(ValueError):
        load_annotations(path, session)


@pytest.mark.parametrize("winner", ["unknown", "", "P3", False, 1, {}, []])
def test_rally_winner_requires_score_slot_or_null(sample, winner):
    session, labels, path = sample
    labels["rallies"][0]["winner"] = winner
    path.write_text(json.dumps(labels))

    with pytest.raises(ValueError, match="winner"):
        load_annotations(path, session, allow_draft=True)


@pytest.mark.parametrize("winner", ["P1", "P2", None])
def test_supported_winner_values_are_preserved(sample, winner):
    session, labels, path = sample
    labels["rallies"][0]["winner"] = winner
    path.write_text(json.dumps(labels))

    assert load_annotations(path, session, allow_draft=True)["rallies"][0]["winner"] == winner


def test_unknown_truth_winner_is_excluded_without_discarding_known_rally_existence(sample):
    from bai_engine.evaluation import Interval, evaluate_intervals

    session, labels, path = sample
    labels["rallies"][0]["winner"] = None
    path.write_text(json.dumps(labels))
    row = load_annotations(path, session, allow_draft=True)["rallies"][0]

    result = evaluate_intervals([Interval(row["start_s"], row["end_s"], row["winner"])], [Interval(1, 8, "P2")])

    assert result["matched"] == 1
    assert result["winner_evaluated"] == 0
    assert result["winner_unresolved"] == 0
    assert result["winner_accuracy"] is None
    assert result["winner_resolution_rate"] is None


@pytest.mark.parametrize("document", [None, [], "unreviewed", 1])
def test_manifest_requires_a_json_object(sample, document):
    session, _, path = sample
    path.write_text(json.dumps(document))

    with pytest.raises(ValueError):
        load_annotations(path, session, allow_draft=True)


@pytest.mark.parametrize("version", [True, 1.0, "1", 2])
def test_manifest_schema_version_requires_integer_one(sample, version):
    session, labels, path = sample
    labels["schema_version"] = version
    path.write_text(json.dumps(labels))

    with pytest.raises(ValueError, match="schema_version"):
        load_annotations(path, session, allow_draft=True)


@pytest.mark.parametrize(
    "window",
    [None, [], [0], [0, 10, "unknown"], "01", {"start": 0, "end": 10}, [False, 10], [0, True],
     ["0", 10], [0, None], [float("nan"), 10], [0, float("inf")], [-1, 10], [10, 10]],
)
def test_window_requires_exactly_two_finite_nonboolean_numbers(sample, window):
    session, labels, path = sample
    labels.update(window_s=window, rallies=[])
    path.write_text(json.dumps(labels))

    with pytest.raises(ValueError):
        load_annotations(path, session, allow_draft=True)


@pytest.mark.parametrize(
    "row",
    [None, [], "unknown", {}, {"start_s": 0}, {"end_s": 8}, {"start_s": False, "end_s": 8},
     {"start_s": 0, "end_s": True}, {"start_s": "1", "end_s": 8}, {"start_s": 1, "end_s": None},
     {"start_s": float("nan"), "end_s": 8}, {"start_s": 1, "end_s": float("inf")}],
)
def test_rally_rows_require_objects_with_finite_nonboolean_boundaries(sample, row):
    session, labels, path = sample
    labels["rallies"] = [row]
    path.write_text(json.dumps(labels))

    with pytest.raises(ValueError):
        load_annotations(path, session, allow_draft=True)


@pytest.mark.parametrize("rows", [None, {}, "unknown", 1])
def test_rallies_require_a_list(sample, rows):
    session, labels, path = sample
    labels["rallies"] = rows
    path.write_text(json.dumps(labels))

    with pytest.raises(ValueError):
        load_annotations(path, session, allow_draft=True)


def test_optional_declared_session_and_media_metadata_accept_exact_binding(sample):
    session, labels, path = sample
    labels.update(session_id="EVAL", fps_num=30000, fps_den=1001, n_frames=300, proxy_sha256="b" * 64)
    path.write_text(json.dumps(labels))

    actual = load_annotations(path, session, allow_draft=True)

    assert actual["session_id"] == "EVAL"
    assert actual["fps_num"] == 30000
    assert actual["fps_den"] == 1001
    assert actual["n_frames"] == 300
    assert actual["proxy_sha256"] == "b" * 64


@pytest.mark.parametrize(
    "key,value",
    [("session_id", "OTHER"), ("session_id", None), ("fps_num", 30001), ("fps_num", 30000.0),
     ("fps_den", 1000), ("fps_den", True), ("n_frames", 301), ("n_frames", 300.0),
     ("n_frames", "300"), ("proxy_sha256", "B" * 64), ("proxy_sha256", "not-a-hash"),
     ("proxy_sha256", None)],
)
def test_optional_source_binding_is_validated_when_declared(sample, key, value):
    session, labels, path = sample
    labels[key] = value
    path.write_text(json.dumps(labels))

    with pytest.raises(ValueError):
        load_annotations(path, session, allow_draft=True)


@pytest.fixture
def stored_media(sample, tmp_path):
    session, labels, annotation_path = sample
    source_bytes, proxy_bytes = b"original container bytes", b"canonical proxy bytes"
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    proxy_hash = hashlib.sha256(proxy_bytes).hexdigest()
    data_dir = tmp_path / "data"
    media_dir = data_dir / "media" / source_hash
    media_dir.mkdir(parents=True)
    source_path, proxy_path = media_dir / "source.mkv", media_dir / "proxy.mp4"
    source_path.write_bytes(source_bytes)
    proxy_path.write_bytes(proxy_bytes)
    session.source.uri, session.source.sha256 = str(source_path), source_hash
    labels.update(media_sha256=source_hash, proxy_sha256=proxy_hash)
    return data_dir, session, labels, annotation_path, source_path, proxy_path


def test_media_byte_verification_supports_the_stored_source_extension(stored_media):
    from research.evaluate_session import verify_media_binding

    data_dir, session, labels, _, _, _ = stored_media

    actual = verify_media_binding(data_dir, session, labels)

    assert actual["source_sha256"] == labels["media_sha256"]
    assert actual["proxy_sha256"] == labels["proxy_sha256"]
    assert actual["proxy_label_bound"] is True


@pytest.mark.parametrize("changed_file", ["source", "proxy"])
def test_media_byte_verification_rejects_changed_files(stored_media, changed_file):
    from research.evaluate_session import verify_media_binding

    data_dir, session, labels, _, source_path, proxy_path = stored_media
    (source_path if changed_file == "source" else proxy_path).write_bytes(b"different bytes")

    with pytest.raises(ValueError, match=changed_file):
        verify_media_binding(data_dir, session, labels)


@pytest.mark.parametrize("missing_file", ["source", "proxy"])
def test_media_byte_verification_does_not_silently_accept_missing_files(stored_media, missing_file):
    from research.evaluate_session import verify_media_binding

    data_dir, session, labels, _, source_path, proxy_path = stored_media
    (source_path if missing_file == "source" else proxy_path).unlink()

    with pytest.raises(ValueError, match=missing_file):
        verify_media_binding(data_dir, session, labels)


def test_legacy_labels_report_unbound_proxy_without_inventing_annotation_binding(stored_media):
    from research.evaluate_session import verify_media_binding

    data_dir, session, labels, _, _, proxy_path = stored_media
    labels.pop("proxy_sha256")

    actual = verify_media_binding(data_dir, session, labels)

    assert actual["proxy_label_bound"] is False
    assert actual["proxy_sha256"] == hashlib.sha256(proxy_path.read_bytes()).hexdigest()


@pytest.fixture
def stored_evaluation(stored_media, monkeypatch):
    data_dir, session, labels, annotation_path, _, _ = stored_media
    annotation_path.write_bytes(json.dumps(labels, indent=2).encode())
    with sqlite3.connect(data_dir / "sessions.sqlite") as connection:
        connection.execute("CREATE TABLE sessions (session_id TEXT PRIMARY KEY, body TEXT NOT NULL)")
        connection.execute("INSERT INTO sessions VALUES (?,?)", (session.session_id, session.model_dump_json()))
    event_dir = data_dir / "sessions" / session.session_id
    event_dir.mkdir(parents=True)
    with sqlite3.connect(event_dir / "events.sqlite") as connection:
        connection.execute("CREATE TABLE events (seq INTEGER PRIMARY KEY, body TEXT NOT NULL)")
    monkeypatch.setattr(
        sys, "argv",
        ["evaluate_session.py", "--data-dir", str(data_dir), "--session", session.session_id,
         "--annotations", str(annotation_path), "--allow-draft"],
    )
    return stored_media


@pytest.mark.parametrize("changed_file", ["source", "proxy"])
def test_cli_refuses_to_report_metrics_for_changed_media(stored_evaluation, capsys, changed_file):
    from research import evaluate_session

    _, _, _, _, source_path, proxy_path = stored_evaluation
    (source_path if changed_file == "source" else proxy_path).write_bytes(b"different bytes")

    with pytest.raises(SystemExit) as error:
        evaluate_session.main()

    captured = capsys.readouterr()
    assert error.value.code == 2
    assert changed_file in captured.err
    assert captured.out == ""


def test_cli_hashes_the_annotation_bytes_it_evaluated_even_if_file_changes(stored_evaluation, monkeypatch, capsys):
    from research import evaluate_session

    _, _, labels, annotation_path, _, _ = stored_evaluation
    original_bytes = annotation_path.read_bytes()

    real_current_view = evaluate_session.current_view

    def replace_annotations_after_parsing(events):
        annotation_path.write_text(json.dumps({**labels, "rallies": []}))
        return real_current_view(events)

    monkeypatch.setattr(evaluate_session, "current_view", replace_annotations_after_parsing)

    evaluate_session.main()
    report = json.loads(capsys.readouterr().out)

    assert report["truth_count"] == 1
    assert report["provenance"]["annotation_sha256"] == hashlib.sha256(original_bytes).hexdigest()
    assert report["provenance"]["annotation_sha256"] != hashlib.sha256(annotation_path.read_bytes()).hexdigest()
    assert report["provenance"]["accuracy_claim_eligible"] is False
