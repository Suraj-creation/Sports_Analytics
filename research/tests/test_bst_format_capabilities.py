"""A singles-only shadow model must not turn missing format into singles.

All model/media boundaries use spies. No checkpoint or video is read. Run only
on the configured GPU server, including this synthetic regression suite.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from bai_engine.schema.events import Event, EventStatus, Provenance
from bai_engine.schema.session import MediaInfo, ParticipantRoster, Session, SessionStatus, Source, SourceKind
from research.evaluation import bst_shadow as shadow
from research.evaluation import bst_shadow_session as session_shadow


def fixture_session(match_format=None, *, meta=None):
    return Session(
        session_id="FORMATFIXTURE1",
        title="Synthetic format guard fixture",
        source=Source(kind=SourceKind.UPLOAD, uri="unused-source.mp4", sha256="a" * 64),
        media=MediaInfo(fps_num=30, fps_den=1, n_frames=120, width=1280, height=720, duration_us=4_000_000),
        roster=ParticipantRoster(match_format=match_format) if match_format is not None else None,
        status=SessionStatus.ANALYSED,
        frontier_frame=119,
        meta={} if meta is None else meta,
    )


def stroke_event():
    return Event(
        event_id="stroke60",
        session_id="FORMATFIXTURE1",
        type="stroke",
        frame_start=60,
        frame_end=60,
        pts_us=2_000_000,
        status=EventStatus.CONFIRMED,
        provenance=Provenance(model="format_fixture_rules"),
        payload={"stroke": "unknown"},
    )


def install_spies(monkeypatch, session):
    calls = {name: [] for name in ("digest", "events", "cache", "registry", "checkpoint", "model", "prepare", "predict")}
    event = stroke_event()
    catalogue = session.model_dump_json()
    rows = [(1, event.model_dump_json())]
    frames = {index: object() for index in range(45, 75)}
    sequence = SimpleNamespace(usable_frames=30, video_len=30, source_frames=tuple(range(45, 75)))

    def predict_stub(value):
        calls["predict"].append(value)
        return SimpleNamespace(
            prediction=SimpleNamespace(top=("smash", 0.8), probs={"smash": 0.8, "unknown": 0.2}),
            side_probabilities={"far": 0.8, "near": 0.2, "unknown": 0.0},
            class_probabilities=(0.0,) * 25,
        )

    def prepare_sequence(observations, frame_size, *, match_format):
        calls["prepare"].append((observations, frame_size, match_format))
        return sequence

    class Checkpoint:
        def stat(self):
            return SimpleNamespace(st_size=123)

    checkpoint = Checkpoint()

    class Registry:
        def __init__(self, directory):
            calls["registry"].append(directory)

        def path(self, name, *, fetch):
            calls["checkpoint"].append((name, fetch))
            return checkpoint

    class Classifier:
        name = "synthetic_format_spy"

        def __init__(self, artifact, *, device):
            calls["model"].append((artifact, device))

        predict_sequence = staticmethod(predict_stub)

    def digest(path):
        calls["digest"].append(path)
        return {"source.mp4": "a" * 64, "proxy.mp4": "b" * 64}.get(Path(path).name, "c" * 64)

    def event_rows(*_):
        calls["events"].append(True)
        return rows

    def extract_frames(*args):
        calls["cache"].append(args)
        return frames, {"cache_sha256": {}, "codec_chunks": {}, "frame_calibration": {}}

    for module in (shadow, session_shadow):
        monkeypatch.setattr(module, "_catalogue", lambda *_: catalogue)
        monkeypatch.setattr(module, "_event_rows", event_rows)
        monkeypatch.setattr(module, "digest", digest)
        monkeypatch.setattr(module, "extract_frames", extract_frames)
        monkeypatch.setattr(module, "ModelRegistry", Registry)
        monkeypatch.setattr(module, "BSTClassifier", Classifier)
    monkeypatch.setattr(shadow, "prepare_sequence", prepare_sequence)
    return calls, event, frames, SimpleNamespace(predict_sequence=predict_stub), rows


def assert_format_reason(error, match_format):
    reason = str(error).lower()
    if match_format is None:
        assert "format" in reason and ("unknown" in reason or "unresolved" in reason)
        assert "configure" in reason or "confirm" in reason
    else:
        assert "doubles" in reason and "unsupported" in reason


def write_snapshot(directory, session, rows):
    directory.mkdir()
    event_hash = hashlib.sha256("\n".join(body for _, body in rows).encode()).hexdigest()
    (directory / "benchmark.json").write_text(json.dumps({
        "session_id": session.session_id,
        "rallies": [],
        "aggregate": {"shot_family": {"known_family": {"macro_f1": None}}},
        "provenance": {"event_log_sha256": event_hash},
    }), encoding="utf-8")


@pytest.mark.parametrize("meta", [{}, {"match_format": "singles"},
                                  {"format": {"value": "singles", "status": "inferred", "score": 0.99}}])
def test_unresolved_format_cannot_invoke_singles_preprocessing_or_prediction(monkeypatch, meta):
    session = fixture_session(meta=meta)
    calls, event, frames, classifier, _ = install_spies(monkeypatch, session)
    with pytest.raises(ValueError) as error:
        shadow.infer_strokes(session, [event], frames, classifier)
    assert_format_reason(error.value, None)
    assert calls["prepare"] == [] and calls["predict"] == []
    assert event.actors.player_id is None


def test_explicit_doubles_is_unsupported_without_using_a_two_player_model(monkeypatch):
    session = fixture_session("doubles")
    calls, event, frames, classifier, _ = install_spies(monkeypatch, session)
    with pytest.raises(ValueError) as error:
        shadow.infer_strokes(session, [event], frames, classifier)
    assert_format_reason(error.value, "doubles")
    assert calls["prepare"] == [] and calls["predict"] == []


def test_explicit_singles_keeps_detected_context_prediction_and_actor_uncertainty(monkeypatch):
    session = fixture_session("singles")
    calls, event, frames, classifier, _ = install_spies(monkeypatch, session)
    predictions, reasons = shadow.infer_strokes(session, [event], frames, classifier)
    prediction = predictions["stroke60"]
    assert prediction["status"] == "inferred" and prediction["family"] == "smash"
    assert prediction["context"] == [45, 75]
    assert prediction["court_side"] == "top"
    assert prediction["previous_detected_contact"] is None and prediction["following_detected_contact"] is None
    assert dict(reasons) == {"inferred": 1}
    assert len(calls["prepare"]) == len(calls["predict"]) == 1
    assert calls["prepare"][0][1:] == ((1280, 720), "singles")
    assert event.actors.player_id is None and event.payload["stroke"] == "unknown"


@pytest.mark.parametrize("match_format", [None, "doubles"])
@pytest.mark.parametrize("entry_point", ["session", "snapshot"])
def test_format_guard_precedes_media_cache_registry_and_model_access(monkeypatch, tmp_path, match_format, entry_point):
    session = fixture_session(match_format)
    calls, _, _, _, rows = install_spies(monkeypatch, session)
    output = tmp_path / "shadow.json"
    if entry_point == "snapshot":
        snapshot = tmp_path / "snapshot"
        write_snapshot(snapshot, session, rows)
        invoke = lambda: shadow.run(snapshot, output, tmp_path / "models")
    else:
        invoke = lambda: session_shadow.run_session(tmp_path / "data", session.session_id, output, tmp_path / "models")
    with pytest.raises(ValueError) as error:
        invoke()
    assert_format_reason(error.value, match_format)
    assert all(not values for values in calls.values())
    assert not output.exists()


@pytest.mark.parametrize("entry_point", ["session", "snapshot"])
def test_explicit_singles_entry_points_still_emit_read_only_shadow_predictions(monkeypatch, tmp_path, entry_point):
    session = fixture_session("singles")
    calls, _, _, _, rows = install_spies(monkeypatch, session)
    output = tmp_path / "shadow.json"
    if entry_point == "snapshot":
        snapshot = tmp_path / "snapshot"
        write_snapshot(snapshot, session, rows)
        report = shadow.run(snapshot, output, tmp_path / "models")
        predictions = report["all_stroke_predictions"]
        assert report["default_pipeline_changed"] is False
    else:
        report = session_shadow.run_session(tmp_path / "data", session.session_id, output, tmp_path / "models")
        predictions = report["predictions"]
        assert report["source_session_modified"] is False
    assert len(predictions) == 1 and predictions[0]["family"] == "smash"
    assert predictions[0]["event_id"] == "stroke60"
    assert calls["checkpoint"] == [("bst_cg_ap_shuttleset", False)]
    assert len(calls["model"]) == len(calls["predict"]) == 1
    assert json.loads(output.read_text())["session_id"] == session.session_id


@pytest.mark.parametrize("match_format", [None, "doubles"])
@pytest.mark.parametrize("entry_point", ["session", "snapshot"])
def test_cli_explains_unsupported_or_unresolved_format_without_a_traceback_or_model_access(
    monkeypatch, tmp_path, capsys, match_format, entry_point,
):
    session = fixture_session(match_format)
    calls, _, _, _, rows = install_spies(monkeypatch, session)
    output = tmp_path / "shadow.json"
    if entry_point == "snapshot":
        snapshot = tmp_path / "snapshot"
        write_snapshot(snapshot, session, rows)
        module = shadow
        arguments = ["bst_shadow", "--snapshot", str(snapshot), "--output", str(output)]
    else:
        module = session_shadow
        arguments = ["bst_shadow_session", "--data-dir", str(tmp_path / "data"),
                     "--session", session.session_id, "--output", str(output)]
    monkeypatch.setattr(sys, "argv", arguments)
    with pytest.raises(SystemExit) as error:
        module.main()
    assert error.value.code == 2
    assert_format_reason(capsys.readouterr().err, match_format)
    assert all(not values for values in calls.values())
    assert not output.exists()
