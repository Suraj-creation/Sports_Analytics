"""Reference evaluation must score machine events without rebinding named people."""

from __future__ import annotations

import hashlib
import importlib
import json
import sqlite3
import subprocess
import sys

import pytest

from bai_engine.schema.events import Actors, Event, EventStatus, Provenance
from bai_engine.schema.session import MediaInfo, Session, SessionStatus, Source, SourceKind
from research.finebadminton_reference import convert_reference


def fixture(tmp_path):
    source = b"synthetic source video"
    sha = hashlib.sha256(source).hexdigest()
    media_dir = tmp_path / "data" / "media" / sha
    media_dir.mkdir(parents=True)
    (media_dir / "source.mp4").write_bytes(source)
    (media_dir / "proxy.mp4").write_bytes(b"synthetic canonical proxy")
    rows = []
    for start, end, families, names, sides in [
        (0, 100, ["cross-court net shot", "clear", "smash"], ["Alice", "Bob", "Alice"], ["bottom", "top", "bottom"]),
        (100, 200, ["clear", "drive"], ["Alice", "Bob"], ["top", "bottom"]),
    ]:
        hits = []
        for index, (family, name, side) in enumerate(zip(families, names, sides, strict=True)):
            frame = start + index * 25
            hits.append(
                {
                    "start_frame": frame,
                    "end_frame": frame + 25 if index + 1 < len(families) else end,
                    "player": name,
                    "Foundational Actions Level": {"hit type": family, "subtype": [], "hitter": side},
                }
            )
        rows.append(
            {
                "video": "0044.mp4",
                "resolution": {"width": 1280, "height": 720},
                "fps": 25.0,
                "duration_frames": end - start,
                "start_frame": start,
                "end_frame": end,
                "hitting": hits,
                "playerList": [{"name": "Alice", "role": "server"}, {"name": "Bob", "role": "receiver"}],
            }
        )
    raw = json.dumps(rows).encode()
    labels = convert_reference(
        raw,
        session_id="S1",
        video_name="0044.mp4",
        media_sha256=sha,
        expected_media_sha256=sha,
        expected_source_sha256=hashlib.sha256(raw).hexdigest(),
        fps_num=25,
        fps_den=1,
        n_frames=250,
        width=1280,
        height=720,
        accept_published_review=True,
        split="held_out",
        held_out_reserved_before_tuning=True,
    )
    annotations = tmp_path / "annotations"
    annotations.mkdir()
    for index, label in enumerate(labels):
        (annotations / f"rally-{index}.json").write_text(json.dumps(label), encoding="utf-8")
    data = tmp_path / "data"
    session = Session(
        session_id="S1",
        title="Synthetic reference fixture",
        source=Source(kind=SourceKind.UPLOAD, uri="source.mp4", sha256=sha),
        status=SessionStatus.ANALYSED,
        frontier_frame=249,
        analysed_frames=250,
        media=MediaInfo(fps_num=25, fps_den=1, n_frames=250, width=1280, height=720, duration_us=10000000),
    )
    with sqlite3.connect(data / "sessions.sqlite") as connection:
        connection.execute("CREATE TABLE sessions(session_id TEXT PRIMARY KEY, body TEXT)")
        connection.execute("INSERT INTO sessions VALUES(?,?)", ("S1", session.model_dump_json()))
    event_dir = data / "sessions" / "S1"
    event_dir.mkdir(parents=True)
    events = [
        event(0, "cross_net", [0, -3], "provisional_track_episode"),
        event(25, "clear", [0, -3], "named_player"),
        event(50, "smash", None, "named_player"),
        event(100, "unknown", [0, 3], None),
        event(125, "drive", [0, -3], "provisional_track_episode"),
        event(175, "clear", [0, 3], "named_player"),
    ]
    with sqlite3.connect(event_dir / "events.sqlite") as connection:
        connection.execute("CREATE TABLE events(seq INTEGER PRIMARY KEY, body TEXT)")
        connection.executemany(
            "INSERT INTO events VALUES(?,?)", [(i, e.model_dump_json()) for i, e in enumerate(events, 1)]
        )
    return data, annotations, events, media_dir


def event(frame, family, xy, context):
    return Event(
        session_id="S1",
        type="stroke",
        frame_start=frame,
        frame_end=frame,
        pts_us=frame * 40000,
        actors=Actors(player_id="Alice"),
        status=EventStatus.CONFIRMED,
        provenance=Provenance(model="stroke_rules_v0"),
        payload={"stroke": family, "hitter_court_xy": xy, "classification_context_source": context},
    )


def benchmark(data, annotations, **kwargs):
    module = importlib.import_module("research.evaluation.benchmark_reference_session")
    return module.benchmark_session(data, "S1", annotations, **kwargs)


def replace_event(data, events, index, *, payload):
    replacement = events[index].model_copy(update={"payload": payload})
    with sqlite3.connect(data / "sessions" / "S1" / "events.sqlite") as connection:
        connection.execute("UPDATE events SET body=? WHERE seq=?", (replacement.model_dump_json(), index + 1))


def test_real_event_extraction_aggregates_counts_and_scores_court_side_only(tmp_path):
    data, annotations, _, _ = fixture(tmp_path)
    report = benchmark(data, annotations)
    aggregate = report["aggregate"]
    contacts = aggregate["contact_detection"]
    assert contacts["truth_count"] == 5 and contacts["prediction_count"] == 6
    assert contacts["matched"] == 5 and contacts["false_positives"] == 1
    assert contacts["precision"] == pytest.approx(5 / 6) and contacts["recall"] == 1
    assert aggregate["shot_family"]["known_family"]["macro_f1"] == 0.875
    assert aggregate["shot_family"]["known_family"]["per_class"]["clear"]["support"] == 2
    assert aggregate["shot_family"]["known_family"]["per_class"]["clear"]["predicted"] == 2
    sides = aggregate["court_side"]
    assert sides["correct"] == 2 and sides["wrong"] == 1 and sides["unresolved_matched"] == 2
    assert sides["accuracy_all_labelled_truth"] == 0.4
    assert sides["per_side"]["bottom"]["false_positives"] == 1
    assert sides["per_side"]["top"]["false_positives"] == 1
    joint = aggregate["joint_contact_family_court_side"]
    assert joint["true_positives"] == 2 and joint["false_positives"] == 4 and joint["false_negatives"] == 3
    assert report["scope"] == "published_singles_rally_windows_with_court_side_only"
    assert report["durable_person_accuracy_evaluated"] is False
    assert report["pretrained_training_overlap"] == "unknown"
    prediction = report["rallies"][0]["predictions"][0]
    assert prediction["original_family"] == "cross_net" and prediction["family"] == "net_shot"
    assert prediction["placement"] == "cross_court" and prediction["court_side"] == "bottom"
    assert "per_person" not in aggregate and "hitter_accuracy" not in aggregate


def test_timestamp_metrics_disclose_published_anchor_semantics_and_unverified_contact_precision(tmp_path):
    data, annotations, _, _ = fixture(tmp_path)
    report = benchmark(data, annotations)
    semantics = report["metric_semantics"]
    assert semantics["comparison_kind"] == "published_hit_anchor_agreement"
    assert semantics["reference_timestamp_field"] == "hitting.start_frame"
    assert semantics["matching_tolerance_frames"] == 5
    assert semantics["physical_contact_frames_independently_verified"] is False
    assert report["physical_contact_accuracy_claim_eligible"] is False
    assert "published hit anchors" in report["aggregate"]["contact_detection"]["metric_label"]


@pytest.mark.parametrize(
    "xy,context",
    [
        ([0, 3], None),
        ([0, 3], "position_guess"),
        (None, "named_player"),
        ([0, float("nan")], "named_player"),
        ([0, 0], "named_player"),
        ([True, 3], "named_player"),
        ([0, 3, 4], "named_player"),
    ],
)
def test_side_abstains_without_supported_finite_geometry_even_when_actor_matches_name(tmp_path, xy, context):
    data, annotations, events, _ = fixture(tmp_path)
    replace_event(
        data,
        events,
        0,
        payload={"stroke": "cross_net", "hitter_court_xy": xy, "classification_context_source": context},
    )
    report = benchmark(data, annotations)
    assert report["rallies"][0]["predictions"][0]["court_side"] is None
    assert report["aggregate"]["court_side"]["correct"] == 1


def test_missed_hits_remain_in_court_side_and_joint_denominators(tmp_path):
    data, annotations, _, _ = fixture(tmp_path)
    with sqlite3.connect(data / "sessions" / "S1" / "events.sqlite") as connection:
        connection.execute("DELETE FROM events WHERE seq=5")
    report = benchmark(data, annotations)["aggregate"]
    assert report["contact_detection"]["false_negatives"] == 1
    assert report["court_side"]["unmatched_labelled_truth"] == 1
    assert report["court_side"]["accuracy_all_labelled_truth"] == 0.2
    assert report["joint_contact_family_court_side"]["false_negatives"] == 4


def test_events_outside_reference_rallies_are_not_spurious_predictions(tmp_path):
    data, annotations, _, _ = fixture(tmp_path)
    with sqlite3.connect(data / "sessions" / "S1" / "events.sqlite") as connection:
        connection.execute(
            "INSERT INTO events VALUES(?,?)", (100, event(225, "smash", [0, 3], "named_player").model_dump_json())
        )
    assert benchmark(data, annotations)["aggregate"]["contact_detection"]["prediction_count"] == 6


@pytest.mark.parametrize(
    "problem",
    [
        "source_bytes",
        "session_fps",
        "label_session",
        "label_fps",
        "frame_time",
        "mixed_revision",
        "overlap",
        "human_correction",
        "unfinished_analysis",
    ],
)
def test_invalid_source_or_machine_snapshot_is_rejected(tmp_path, problem):
    data, annotations, events, media = fixture(tmp_path)
    path = annotations / "rally-0.json"
    labels = json.loads(path.read_text())
    if problem == "source_bytes":
        (media / "source.mp4").write_bytes(b"another video")
    elif problem in ("session_fps", "unfinished_analysis"):
        with sqlite3.connect(data / "sessions.sqlite") as connection:
            raw = json.loads(connection.execute("SELECT body FROM sessions").fetchone()[0])
            if problem == "session_fps":
                raw["media"]["fps_num"] = 30
            else:
                raw["status"] = "analysing"
            connection.execute("UPDATE sessions SET body=?", (json.dumps(raw),))
    elif problem == "human_correction":
        correction = events[0].correct(provenance=Provenance(model="human"))
        with sqlite3.connect(data / "sessions" / "S1" / "events.sqlite") as connection:
            connection.execute("INSERT INTO events VALUES(?,?)", (100, correction.model_dump_json()))
    else:
        if problem == "label_session":
            labels["session_id"] = "S2"
        elif problem == "label_fps":
            labels["fps_num"] = 30
        elif problem == "frame_time":
            labels["shots"][0]["time_s"] = 0.1
        elif problem == "mixed_revision":
            labels["reference_provenance"]["dataset_revision"] = "a" * 40
        else:
            labels = json.loads((annotations / "rally-1.json").read_text())
        path.write_text(json.dumps(labels))
    with pytest.raises(ValueError):
        benchmark(data, annotations)


@pytest.mark.parametrize("mutation", ["event_log", "source", "proxy", "annotation", "catalogue"])
def test_inputs_changed_during_scoring_fail_closed(tmp_path, monkeypatch, mutation):
    data, annotations, _, media = fixture(tmp_path)
    module = importlib.import_module("research.evaluation.benchmark_reference_session")
    original = module.automatic_predictions_from_session
    changed = False

    def changing_extraction(*args, **kwargs):
        nonlocal changed
        result = original(*args, **kwargs)
        if not changed:
            changed = True
            if mutation == "event_log":
                with sqlite3.connect(data / "sessions" / "S1" / "events.sqlite") as connection:
                    connection.execute(
                        "INSERT INTO events VALUES(?,?)",
                        (99, event(225, "clear", [0, 3], "named_player").model_dump_json()),
                    )
            elif mutation in ("source", "proxy"):
                (media / f"{mutation}.mp4").write_bytes(b"replacement")
            elif mutation == "annotation":
                path = annotations / "rally-0.json"
                path.write_bytes(path.read_bytes() + b"\n")
            else:
                with sqlite3.connect(data / "sessions.sqlite") as connection:
                    value = json.loads(connection.execute("SELECT body FROM sessions").fetchone()[0])
                    value["title"] = "changed while evaluating"
                    connection.execute("UPDATE sessions SET body=?", (json.dumps(value),))
        return result

    monkeypatch.setattr(module, "automatic_predictions_from_session", changing_extraction)
    with pytest.raises(ValueError, match=r"changed|snapshot"):
        benchmark(data, annotations)


def test_cli_writes_frozen_report_and_never_overwrites_output(tmp_path):
    data, annotations, _, _ = fixture(tmp_path)
    output = tmp_path / "report.json"
    command = [
        sys.executable,
        "-m",
        "research.evaluation.benchmark_reference_session",
        "--annotations-dir",
        str(annotations),
        "--data-dir",
        str(data),
        "--session",
        "S1",
        "--output",
        str(output),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    assert completed.returncode == 0, completed.stderr
    report = json.loads(output.read_text())
    assert len(report["provenance"]["annotation_files"]) == 2
    assert len(report["provenance"]["event_log_sha256"]) == 64
    before = output.read_bytes()
    repeated = subprocess.run(command, capture_output=True, text=True, check=False)
    assert repeated.returncode != 0 and "exists" in repeated.stderr
    assert output.read_bytes() == before
