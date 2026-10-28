import json
import sqlite3

import msgpack
import pytest

from bai_badminton.perception.calibration_state import CalibrationState
from research import replay_cached_observations as replay


def encoded_frame(**extra):
    frame = {"f": 0, "p": [], "s": None, "c": 0.0, "r": False, "sh": 0, **extra}
    return msgpack.packb({"v": 7, "frames": [frame], "models": {}}, use_bin_type=True)


def test_v7_validity_and_observation_flags_survive_decode():
    chunk = replay.decode_observations(encoded_frame(cs="VALID", do=False), 1)
    assert chunk is not None
    assert chunk.frames[0].calibration_state is CalibrationState.VALID
    assert chunk.frames[0].detector_observed is False


def test_historical_missing_flags_are_unknown_not_false_or_valid():
    chunk = replay.decode_observations(encoded_frame(), 1)
    assert chunk is not None
    assert chunk.frames[0].calibration_state is None
    assert chunk.frames[0].detector_observed is None


@pytest.mark.parametrize("values", [{"cs": "made_up"}, {"do": 1}])
def test_invalid_encoded_validity_is_rejected(values):
    with pytest.raises(ValueError):
        replay.decode_observations(encoded_frame(**values), 1)


def test_explicit_doubles_session_mapping_and_provenance(tmp_path, monkeypatch):
    data = tmp_path / "source"
    data.mkdir()
    with sqlite3.connect(data / "sessions.sqlite") as db:
        db.execute("CREATE TABLE sessions (session_id TEXT, body TEXT)")
        for sid in ("A1", "B2", "C3"):
            db.execute("INSERT INTO sessions VALUES (?, ?)", (sid, json.dumps({"session_id": sid})))
    calls = []

    def fake_replay(session, _data, _output, *, discipline, persist_tracks=False):
        calls.append((session["session_id"], discipline))
        return {"session_id": session["session_id"], "discipline": discipline}

    monkeypatch.setattr(replay, "replay_session", fake_replay)
    output = tmp_path / "out"
    replay.main(
        [
            "--output-dir",
            str(output),
            "--data-dir",
            str(data),
            "--doubles-session-id",
            "C3",
            "--doubles-session-id",
            "A1",
        ]
    )
    assert calls == [("A1", "doubles"), ("B2", "singles"), ("C3", "doubles")]
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["doubles_session_ids"] == ["A1", "C3"]
    assert manifest["default_discipline"] == "singles"
    assert manifest["status"] == "complete"


def test_unrecognised_doubles_id_cannot_be_silently_ignored(tmp_path):
    data = tmp_path / "source"
    data.mkdir()
    with sqlite3.connect(data / "sessions.sqlite") as db:
        db.execute("CREATE TABLE sessions (session_id TEXT, body TEXT)")
        db.execute("INSERT INTO sessions VALUES (?, ?)", ("A1", json.dumps({"session_id": "A1"})))
    with pytest.raises(ValueError, match="unknown doubles session"):
        replay.main(["--output-dir", str(tmp_path / "out"), "--data-dir", str(data), "--doubles-session-id", "TYPO"])


def test_replay_constructs_doubles_court_config_and_counts_missing_metadata(tmp_path, monkeypatch):
    data = tmp_path / "data"
    source = data / "sessions" / "A1"
    perception = source / "perception"
    perception.mkdir(parents=True)
    (perception / "000.msgpack").write_bytes(encoded_frame(cs="VALID", do=True))
    with sqlite3.connect(source / "events.sqlite") as db:
        db.execute("CREATE TABLE events (type TEXT, body TEXT, seq INTEGER)")

    captured = []

    class Store:
        def __init__(self, *_args):
            pass

        def query(self, **_kwargs):
            return []

    class Engine:
        def __init__(self, _sid, config, _store, **_kwargs):
            captured.append(config)

        def ingest(self, _chunk):
            pass

        def flush(self):
            pass

        def public_state(self):
            return {"score": {"P1": 0, "P2": 0}}

    monkeypatch.setattr(replay, "EventStore", Store)
    monkeypatch.setattr(replay, "BadmintonMatchEngine", Engine)
    session = {
        "session_id": "A1",
        "title": "Doubles",
        "media": {"fps_num": 30, "fps_den": 1, "width": 1280, "height": 720, "n_frames": 1},
        "players": [],
        "source": {"sha256": "abc"},
    }
    result = replay.replay_session(session, data, tmp_path, discipline="doubles")
    assert captured[0].match.discipline == "doubles"
    assert result is not None and result["discipline"] == "doubles"
    assert result["cached_frame_metadata"]["calibration_state_present"] == 1
    assert result["cached_frame_metadata"]["detector_observed_present"] == 1


def test_opt_in_persists_tracks_only_in_fresh_isolated_replay_output(tmp_path, monkeypatch):
    from bai_engine.schema import TrackObject, TrackSample
    from bai_engine.store import TrackStore

    data = tmp_path / "source"
    source = data / "sessions" / "A1"
    (source / "perception").mkdir(parents=True)
    (source / "perception" / "000.msgpack").write_bytes(encoded_frame(cs="VALID", do=True))
    with sqlite3.connect(source / "events.sqlite") as db:
        db.execute("CREATE TABLE events (type TEXT, body TEXT, seq INTEGER)")

    class Store:
        def __init__(self, *_args):
            pass

        def query(self, **_kwargs):
            return []

    class Engine:
        def __init__(self, *_args, **_kwargs):
            self.pending = []

        def ingest(self, _chunk):
            self.pending.append(
                TrackSample(
                    frame_idx=0,
                    obj=TrackObject.PLAYER,
                    track_id=3,
                    bbox=(1, 1, 20, 30),
                    conf=0.9,
                    participant_observation_id="birth-1",
                )
            )

        def drain_tracks(self):
            result, self.pending = self.pending, []
            return result

        def flush(self):
            pass

        def public_state(self):
            return {"score": {"P1": 0, "P2": 0}}

    monkeypatch.setattr(replay, "EventStore", Store)
    monkeypatch.setattr(replay, "BadmintonMatchEngine", Engine)
    session = {
        "session_id": "A1",
        "title": "Doubles",
        "media": {"fps_num": 30, "fps_den": 1, "width": 1280, "height": 720, "n_frames": 1},
        "players": [],
        "source": {"sha256": "abc"},
    }
    output = tmp_path / "output"
    output.mkdir()
    result = replay.replay_session(session, data, output, discipline="doubles", persist_tracks=True)
    assert result["tracks_persisted"] is True
    rows = TrackStore(output / "A1-tracks").read([TrackObject.PLAYER], 0, 0).to_pylist()
    assert len(rows) == 1 and rows[0]["participant_observation_id"] == "birth-1"
    assert not (source / "tracks").exists()


@pytest.mark.parametrize('stride', [None, 0, 2])
def test_pose_schedule_survives_historical_replay_decode(stride):
    chunk = replay.decode_observations(encoded_frame(ps=stride), 1)
    assert chunk is not None and chunk.frames[0].pose_stride == stride


@pytest.mark.parametrize('stride', [-1, True, 1.5, '2'])
def test_replay_rejects_invalid_pose_schedule(stride):
    with pytest.raises(ValueError):
        replay.decode_observations(encoded_frame(ps=stride), 1)


def test_missing_historical_pose_schedule_remains_unknown():
    chunk = replay.decode_observations(encoded_frame(), 1)
    assert chunk is not None and chunk.frames[0].pose_stride is None
