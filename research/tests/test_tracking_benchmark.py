"""Tracking quality must use a single identity mapping over the sampled window."""

from copy import deepcopy

import pytest

from research.tracking_benchmark import evaluate_tracking


def documents():
    common = {
        "schema_version": 1,
        "session_id": "S1",
        "media_sha256": "a" * 64,
        "proxy_sha256": "b" * 64,
        "fps_num": 25,
        "fps_den": 1,
        "width": 1280,
        "height": 720,
        "window_frames": [0, 20],
        "timebase": "analysis_proxy_frames",
        "sampled_frames": [0, 5, 10, 15],
    }
    labels = {
        **common,
        "status": "reviewed",
        "split": "held_out",
        "review": {"human_verified": True, "blind_to_predictions": True},
        "frames": [
            {
                "frame_idx": f,
                "exhaustive": True,
                "persons": [{"person_id": f"P{i}", "bbox": [i * 100, 100, i * 100 + 50, 200]} for i in range(4)],
            }
            for f in common["sampled_frames"]
        ],
    }
    predictions = {
        **common,
        "analysis_generation": "run1",
        "event_log_sha256": "c" * 64,
        "track_chunks": [{"path": "players/0.parquet", "sha256": "d" * 64}],
        "frames": [
            {
                "frame_idx": row["frame_idx"],
                "persons": [
                    {"identity_key": f"birth-{i}", "bbox": person["bbox"], "detector_observed": True}
                    for i, person in enumerate(row["persons"])
                ],
            }
            for row in labels["frames"]
        ],
    }
    return labels, predictions


def test_four_perfect_tracks():
    labels, predictions = documents()
    result = evaluate_tracking(labels, predictions)
    assert result["localization"]["precision"] == result["localization"]["recall"] == 1
    assert result["identity"]["idf1"] == 1
    assert result["identity"]["sampled_switches"] == 0
    assert result["four_player"]["distinct_matched_fraction"] == 1
    assert result["accuracy_claim_eligible"] is True


def test_smooth_partner_swap_keeps_localization_but_penalizes_global_identity():
    labels, predictions = documents()
    for row in predictions["frames"][2:]:
        row["persons"][0]["identity_key"], row["persons"][1]["identity_key"] = "birth-1", "birth-0"
    result = evaluate_tracking(labels, predictions)
    assert result["localization"]["recall"] == 1
    assert result["identity"]["idf1"] == 0.75
    assert result["identity"]["sampled_switches"] == 2


def test_new_episode_every_frame_is_fragmentation_not_identity_success():
    labels, predictions = documents()
    for row in predictions["frames"]:
        for person in row["persons"]:
            person["identity_key"] += f"-{row['frame_idx']}"
    result = evaluate_tracking(labels, predictions)
    assert result["localization"]["recall"] == 1
    assert result["identity"]["idf1"] == 0.25
    assert result["identity"]["sampled_switches"] == 12


def test_absent_prediction_frame_is_not_dropped_from_denominator():
    labels, predictions = documents()
    predictions["frames"].pop()
    result = evaluate_tracking(labels, predictions)
    assert result["localization"]["false_negatives"] == 4
    assert result["localization"]["recall"] == 0.75
    assert result["missing_prediction_frames"] == 1
    assert result["identity"]["idf1"] == pytest.approx(24 / 28)


def test_unknown_truth_identity_keeps_localization_support_only():
    labels, predictions = documents()
    for row in labels["frames"]:
        row["persons"][0]["person_id"] = None
    result = evaluate_tracking(labels, predictions)
    assert result["localization"]["truth_count"] == 16
    assert result["identity"]["labelled_truth"] == 12
    assert result["identity"]["ambiguous_truth_boxes"] == 4
    assert result["identity"]["idf1"] == 1


def test_spurious_duplicate_boxes_are_false_positives_not_extra_matches():
    labels, predictions = documents()
    duplicate = deepcopy(predictions["frames"][0]["persons"][0])
    duplicate["identity_key"] = "spurious"
    predictions["frames"][0]["persons"].append(duplicate)
    result = evaluate_tracking(labels, predictions)
    assert result["localization"]["true_positives"] == 16
    assert result["localization"]["false_positives"] == 1
    assert result["identity"]["idf1"] == pytest.approx(32 / 33)


def test_delivery_with_unknown_identity_does_not_claim_identified_four_people():
    labels, predictions = documents()
    for row in predictions["frames"]:
        row["persons"][0]["identity_key"] = None
    result = evaluate_tracking(labels, predictions)
    assert result["localization"]["recall"] == 1
    assert result["four_player"]["distinct_matched_fraction"] == 0
    assert result["identity"]["idf1"] == 0.75


def test_draft_needs_opt_in_and_cannot_be_accuracy_evidence():
    labels, predictions = documents()
    labels.update(status="draft", split="diagnostic")
    labels["review"]["human_verified"] = False
    with pytest.raises(ValueError, match="draft"):
        evaluate_tracking(labels, predictions)
    assert evaluate_tracking(labels, predictions, allow_draft=True)["accuracy_claim_eligible"] is False


@pytest.mark.parametrize(
    "problem",
    [
        "source",
        "proxy",
        "fps",
        "duplicate",
        "nan",
        "bounds",
        "missing_labels",
        "chunks",
        "event_hash",
        "identity_duplicate",
    ],
)
def test_invalid_or_unbound_documents_fail_closed(problem):
    labels, predictions = documents()
    if problem == "source":
        predictions["media_sha256"] = "e" * 64
    elif problem == "proxy":
        predictions["proxy_sha256"] = "e" * 64
    elif problem == "fps":
        predictions["fps_num"] = 30
    elif problem == "duplicate":
        labels["frames"].append(deepcopy(labels["frames"][0]))
    elif problem == "nan":
        labels["frames"][0]["persons"][0]["bbox"][0] = float("nan")
    elif problem == "bounds":
        predictions["frames"][0]["persons"][0]["bbox"][2] = 2000
    elif problem == "missing_labels":
        labels["frames"].pop()
    elif problem == "chunks":
        predictions.pop("track_chunks")
    elif problem == "event_hash":
        predictions["event_log_sha256"] = "bad"
    else:
        predictions["frames"][0]["persons"][1]["identity_key"] = "birth-0"
    with pytest.raises(ValueError):
        evaluate_tracking(labels, predictions)


def test_session_extractor_namespaces_reused_track_ids_by_birth(tmp_path, monkeypatch):
    import hashlib
    import sqlite3

    from bai_engine.schema import Event, EventStatus, Provenance, TrackObject, TrackSample
    from bai_engine.schema.session import MediaInfo, Session, Source, SourceKind
    from bai_engine.schema.tracks import samples_to_table
    from bai_engine.store import EventStore, TrackStore
    from research.tracking_benchmark import predictions_from_session

    source, proxy = b"source", b"proxy"
    sha = hashlib.sha256(source).hexdigest()
    media = tmp_path / "media" / sha
    media.mkdir(parents=True)
    (media / "source.mp4").write_bytes(source)
    (media / "proxy.mp4").write_bytes(proxy)
    session = Session(
        session_id="S1",
        title="test",
        source=Source(kind=SourceKind.UPLOAD, uri="old/location.mp4", sha256=sha),
        media=MediaInfo(fps_num=25, fps_den=1, n_frames=20, width=1280, height=720, duration_us=800000),
    )
    with sqlite3.connect(tmp_path / "sessions.sqlite") as conn:
        conn.execute("CREATE TABLE sessions (session_id TEXT, body TEXT)")
        conn.execute("INSERT INTO sessions VALUES (?,?)", ("S1", session.model_dump_json()))
    directory = tmp_path / "sessions/S1"
    store = EventStore(directory / "events.sqlite", "S1")
    events = [
        store.append(
            Event(
                session_id="S1",
                type="participant_observation",
                frame_start=f,
                frame_end=f,
                pts_us=f * 40000,
                status=EventStatus.PROVISIONAL,
                provenance=Provenance(model="participant_tracker_v1"),
                payload={
                    "kind": "PARTICIPANT_FIRST_OBSERVED",
                    "track_id": 7,
                    "participant_id": f"participant-abc-{f:06d}",
                },
            )
        )
        for f in (0, 10)
    ]
    tracks = TrackStore(directory / "tracks")
    tracks.write_chunk(
        TrackObject.PLAYER,
        0,
        19,
        samples_to_table(
            [
                TrackSample(
                    frame_idx=f,
                    obj=TrackObject.PLAYER,
                    track_id=7,
                    bbox=(10, 10, 50, 100),
                    conf=0.9,
                    detector_observed=True,
                    participant_observation_id=events[int(f >= 10)].event_id,
                )
                for f in (0, 5, 10, 15)
            ]
        ),
    )
    labels, _ = documents()
    labels.update(media_sha256=sha, proxy_sha256=hashlib.sha256(proxy).hexdigest())
    pred = predictions_from_session(tmp_path, "S1", labels)
    keys = [row["persons"][0]["identity_key"] for row in pred["frames"]]
    assert keys[0] == keys[1] and keys[2] == keys[3] and keys[0] != keys[2]
    assert (
        pred["track_chunks"][0]["sha256"]
        == hashlib.sha256(next((directory / "tracks/player").glob("*.parquet")).read_bytes()).hexdigest()
    )
    # Old birth references after reuse must not manufacture continuity.
    tracks.write_chunk(
        TrackObject.PLAYER,
        0,
        19,
        samples_to_table(
            [
                TrackSample(
                    frame_idx=f,
                    obj=TrackObject.PLAYER,
                    track_id=7,
                    bbox=(10, 10, 50, 100),
                    conf=0.9,
                    detector_observed=True,
                    participant_observation_id=events[0].event_id,
                )
                for f in (0, 5, 10, 15)
            ]
        ),
    )
    stale = predictions_from_session(tmp_path, "S1", labels)
    assert stale["frames"][0]["persons"][0]["identity_key"] is not None
    assert stale["frames"][3]["persons"][0]["identity_key"] is None
    store.append(events[0].retract(Provenance(model="human"), "old birth revoked"))
    assert predictions_from_session(tmp_path, "S1", labels)["frames"][0]["persons"][0]["identity_key"] is None
    original_read = TrackStore.read

    def concurrent_revision(self, *args):
        table = original_read(self, *args)
        self.write_chunk(TrackObject.PLAYER, 0, 19, table)
        return table

    monkeypatch.setattr(TrackStore, "read", concurrent_revision)
    with pytest.raises(ValueError, match="snapshot changed"):
        predictions_from_session(tmp_path, "S1", labels)
    labels["proxy_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="proxy"):
        predictions_from_session(tmp_path, "S1", labels)


def test_overlapping_compatible_boxes_do_not_depend_on_prediction_row_order():
    labels, predictions = documents()
    for row in labels["frames"]:
        row["persons"][1]["bbox"] = row["persons"][0]["bbox"]
    for i, row in enumerate(predictions["frames"]):
        row["persons"][1]["bbox"] = row["persons"][0]["bbox"]
        if i % 2:
            row["persons"].reverse()
    result = evaluate_tracking(labels, predictions)
    assert result["identity"]["idf1"] == 1
    assert result["identity"]["sampled_switches"] == 0
    assert result["identity"]["ambiguous_assignment_truth_boxes"] == 8
