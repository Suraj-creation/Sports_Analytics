"""Read-only entry points of the fresh real-video validation command."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from bai_engine.schema import MediaInfo, Session, Source, SourceKind
from bai_engine.store import SessionRepository

SCRIPT = Path(__file__).resolve().parents[1] / "validate_real_video_runtime.py"


def test_cropped_validation_preserves_only_verified_media_transform_metadata():
    from research.validate_real_video_runtime import validation_input_metadata

    media = MediaInfo(fps_num=30, fps_den=1, n_frames=120, width=1280, height=720, duration_us=4_000_000)
    mapping = {
        "source_decode_frames": [12000, 12120], "source_decode_start": 12000,
        "proxy_frames": [0, 120], "proxy_fps_num": 30, "proxy_fps_den": 1,
        "proxy_sha256": "a" * 64,
        "source_frame_for_proxy_frame": "source_decode_start + proxy_frame",
        "source_timestamps_preserved": False,
        "source_pts_mapping": "decode-index translation only",
        "annotation_labels": [{"winner": "P1"}],
    }
    meta = {"source_window": mapping, "reviewed_intervals": [[0, 120]], "accepted_points": ["P1"],
            "annotation_alignment": "human_verified", "roster_binding": {"near": "P1"}}
    result = validation_input_metadata(meta, media=media, proxy_sha256="a" * 64)
    assert set(result) == {"source_window"}
    assert "annotation_labels" not in result["source_window"]
    assert result["source_window"]["source_decode_start"] == 12000
    result["source_window"]["source_decode_frames"][0] = 1
    assert mapping["source_decode_frames"] == [12000, 12120]


@pytest.mark.parametrize(("key", "value"), [
    ("source_decode_frames", [12000, 12119]),
    ("source_decode_start", True),
    ("proxy_frames", [1, 120]),
    ("proxy_fps_den", 2),
    ("proxy_sha256", "b" * 64),
])
def test_cropped_validation_rejects_inconsistent_media_transform_metadata(key, value):
    from research.validate_real_video_runtime import validation_input_metadata

    media = MediaInfo(fps_num=30, fps_den=1, n_frames=120, width=1280, height=720, duration_us=4_000_000)
    mapping = {"source_decode_frames": [12000, 12120], "source_decode_start": 12000,
               "proxy_frames": [0, 120], "proxy_fps_num": 30, "proxy_fps_den": 1, "proxy_sha256": "a" * 64}
    mapping[key] = value
    with pytest.raises(ValueError, match="source.window|transform"):
        validation_input_metadata({"source_window": mapping}, media=media, proxy_sha256="a" * 64)


def test_full_video_validation_does_not_copy_source_review_metadata():
    from research.validate_real_video_runtime import validation_input_metadata

    assert validation_input_metadata({"reviewed_intervals": [[0, 12]]}, media=None, proxy_sha256="a" * 64) == {}


def test_catalogue_listing_requires_no_inference_or_durable_source_mutation(tmp_path):
    source = tmp_path / "source"
    repo = SessionRepository(source)
    session = repo.save(Session(
        title="Controlled SampleRally",
        source=Source(kind=SourceKind.UPLOAD, uri="missing-video-is-not-opened", sha256="a" * 64),
        media=MediaInfo(fps_num=30, fps_den=1, n_frames=480, width=640, height=360, duration_us=16_000_000),
    ))
    repo.close()
    before = {path.relative_to(source): path.read_bytes() for path in source.rglob("*") if path.is_file()}
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--data-dir", str(source), "--list"],
        capture_output=True, text=True, check=False, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    listing = json.loads(result.stdout)
    assert [(row["session_id"], row["title"], row["n_frames"]) for row in listing] == [
        (session.session_id, "Controlled SampleRally", 480),
    ]
    after = {path.relative_to(source): path.read_bytes() for path in source.rglob("*") if path.is_file()}
    assert {path: after[path] for path in before} == before
    # A mode=ro reader can create these SQLite-owned files even after the last
    # writer closed its WAL catalogue. Do not use immutable mode here: an active
    # source catalogue can have committed rows that exist only in its WAL.
    assert set(after) - set(before) <= {Path("sessions.sqlite-wal"), Path("sessions.sqlite-shm")}
    if Path("sessions.sqlite-wal") not in before and Path("sessions.sqlite-wal") in after:
        assert after[Path("sessions.sqlite-wal")] == b"", "Read-only listing appended WAL records"


def test_catalogue_listing_includes_committed_rows_in_an_active_wal(tmp_path):
    source = tmp_path / "source"
    repo = SessionRepository(source)
    try:
        session = repo.save(Session(title="Initial", source=Source(kind=SourceKind.UPLOAD, uri="fixture")))
        repo.update(session.session_id, title="Committed in active WAL")
        assert (source / "sessions.sqlite-wal").stat().st_size > 0
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--data-dir", str(source), "--list"],
            capture_output=True, text=True, check=False, timeout=30,
        )
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)[0]["title"] == "Committed in active WAL"
    finally:
        repo.close()


def test_validation_refuses_output_inside_source_data_before_loading_models(tmp_path):
    source = tmp_path / "source"
    repo = SessionRepository(source)
    session = repo.save(Session(title="Controlled", source=Source(kind=SourceKind.UPLOAD, uri="fixture")))
    repo.close()
    destination = source / "new-results"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--data-dir", str(source), "--session", session.session_id,
         "--output-dir", str(destination)],
        capture_output=True, text=True, check=False, timeout=30,
    )
    assert result.returncode != 0
    assert "outside" in result.stderr.lower() and "source" in result.stderr.lower()
    assert not destination.exists()


def test_model_staging_uses_existing_pins_and_leaves_source_untouched(tmp_path):
    from research.validate_real_video_runtime import prepare_models

    source = tmp_path / "models"
    artifact = source / "cache" / "controlled" / "weights.pt"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"preexisting controlled artifact, not an executable checkpoint")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    (source / "manifest.yaml").write_text(
        "models:\n  controlled:\n    task: shuttle\n    format: torch\n"
        "    source: {file: weights.pt}\n    sha256: pin-on-first-fetch\n    license: test\n",
        encoding="utf-8",
    )
    (source / "cache/lock.json").write_text(json.dumps({"controlled": digest}), encoding="utf-8")
    before = {path.relative_to(source): path.read_bytes() for path in source.rglob("*") if path.is_file()}
    profile = SimpleNamespace(shuttle=SimpleNamespace(model="controlled", backend="torch-cpu"))
    registry, report = prepare_models(source, tmp_path / "isolated", [profile])
    with registry.open_verified("controlled") as verified:
        assert verified.sha256 == digest
        assert verified.stream.read() == artifact.read_bytes()
    assert report["artifacts"]["controlled"]["status"] == "verified_copy"
    assert {path.relative_to(source): path.read_bytes() for path in source.rglob("*") if path.is_file()} == before


def test_missing_pins_are_not_trusted_or_downloaded(tmp_path):
    from bai_engine.runtime.registry import ModelError
    from research.validate_real_video_runtime import prepare_models

    source = tmp_path / "models"
    source.mkdir()
    (source / "manifest.yaml").write_text(
        "models:\n  controlled:\n    task: shuttle\n    format: torch\n"
        "    source: {url: 'https://invalid.example/weights.pt'}\n"
        "    sha256: pin-on-first-fetch\n    license: test\n", encoding="utf-8",
    )
    profile = SimpleNamespace(shuttle=SimpleNamespace(model="controlled", backend="torch-cpu"))
    registry, report = prepare_models(source, tmp_path / "isolated", [profile])
    with pytest.raises(ModelError, match="downloads disabled"):
        registry.path("controlled", fetch=True)
    assert report["artifacts"]["controlled"]["status"] == "missing_artifact_or_existing_pin"
    assert not (source / "cache").exists()


def _score_fixture(tmp_path, monkeypatch, *, score_rules=None, analytics=None):
    from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, _PendingRally
    from bai_badminton.events.match_phase import RallyEvidence
    from bai_badminton.events.rally_fsm import RallySegment
    from bai_engine.store import EventStore

    session = Session(
        title="Canonical score check", source=Source(kind=SourceKind.UPLOAD, uri="controlled"),
        media=MediaInfo(fps_num=30, fps_den=1, n_frames=1000, width=1280, height=720, duration_us=33_333_333),
    )
    store = EventStore(tmp_path / "canonical-check.sqlite", session.session_id)
    engine = BadmintonMatchEngine(
        session.session_id, EngineConfig(fps=30, frame_width=1280, frame_height=720), store,
        score_rules=score_rules, analytics=analytics,
    )
    monkeypatch.setattr(engine, "_outcome", lambda seg: ("winner", "far", "fixture_observed_rest", .8))
    monkeypatch.setattr(engine, "_phase_evidence", lambda seg, until: RallyEvidence(scoreboard="changed"))
    return session, store, engine, _PendingRally(RallySegment(10, 20, None, "stationary"), [], None)


def test_public_format_projection_does_not_invalidate_a_real_canonical_score_check(tmp_path, monkeypatch):
    from research.validate_real_video_runtime import score_checks

    session, store, engine, pending = _score_fixture(tmp_path, monkeypatch)
    with store:
        engine._pending = [pending]
        engine._finalize_pending(100)
        view = {**engine.public_state(), "format": {"match_format": "singles", "source": "configured"}}
        sport = SimpleNamespace(engine=engine, public_state=lambda: view)
        report = score_checks(sport, store, session, 1000)
        assert report["consistent"] is True
        assert report["live_state"] == report["restored_state"] == engine.public_state()
        assert report["public_view_state"] == view
        assert "format" not in report["live_state"]


def test_canonical_state_without_a_durable_point_still_fails_even_when_public_view_hides_it(tmp_path, monkeypatch):
    from research.validate_real_video_runtime import score_checks

    session, store, engine, _ = _score_fixture(tmp_path, monkeypatch)
    with store:
        hidden = engine.public_state()
        engine.state = engine.score_rules.apply(engine.state, "P1", engine.match_cfg).after
        assert engine.state.score == {"P1": 1, "P2": 0}
        sport = SimpleNamespace(engine=engine, public_state=lambda: {**hidden, "format": {"match_format": "unknown"}})
        report = score_checks(sport, store, session, 1000)
        assert report["consistent"] is False
        assert {"reason": "live_vs_restored_public_score_state_mismatch"} in report["issues"]
        assert report["live_state"]["score"] == {"P1": 1, "P2": 0}
        assert report["restored_state"]["score"] == {"P1": 0, "P2": 0}


def test_score_restore_uses_selected_stateless_rules_without_touching_live_analytics(tmp_path, monkeypatch):
    from bai_badminton.components import TransactionalAnalytics
    from bai_badminton.rules import apply_rally, initial_state
    from research.validate_real_video_runtime import score_checks

    class ConfiguredRules:
        def initial(self, config):
            return initial_state(config).model_copy(update={"score": {"P1": 7, "P2": 3}})

        def apply(self, before, winner, config):
            return apply_rally(before, winner, config)

    class LiveAnalytics(TransactionalAnalytics):
        def __init__(self):
            self.reset_calls = 0
            super().__init__(30)

        def reset(self):
            self.reset_calls += 1
            super().reset()

    live_analytics = LiveAnalytics()
    session, store, engine, pending = _score_fixture(
        tmp_path, monkeypatch, score_rules=ConfiguredRules(), analytics=live_analytics,
    )
    with store:
        engine._pending = [pending]
        engine._finalize_pending(100)
        # Physical tracks do not implicitly bind score slots. An explicit human
        # decision supplies this fixture winner independently of visual identity.
        from bai_engine.schema import Provenance
        rally = store.query(types=["rally_end"])[0]
        engine.correct_rally_winner(rally.event_id, "P1", Provenance(model="human"))
        assert engine.state.score == {"P1": 8, "P2": 3}
        reset_calls = live_analytics.reset_calls
        before_analytics = live_analytics.to_public()
        report = score_checks(SimpleNamespace(engine=engine, public_state=engine.public_state), store, session, 1000)
        assert report["consistent"] is True
        assert report["restored_state"]["score"] == {"P1": 8, "P2": 3}
        assert engine.analytics is live_analytics
        assert live_analytics.reset_calls == reset_calls
        assert live_analytics.to_public() == before_analytics


def _pinned_model_source(tmp_path, names):
    source = tmp_path / "models"
    source.mkdir()
    entries = []
    pins = {}
    for name in names:
        artifact = source / "cache" / name / "weights.pt"
        artifact.parent.mkdir(parents=True)
        artifact.write_bytes(f"controlled artifact {name}".encode())
        pins[name] = hashlib.sha256(artifact.read_bytes()).hexdigest()
        entries.append(f"  {name}:\n    task: shuttle\n    format: torch\n    source: {{file: weights.pt}}\n    sha256: pin-on-first-fetch\n    license: test\n")
    (source / "manifest.yaml").write_text("models:\n" + "".join(entries) if entries else "models: {}\n")
    if pins:
        (source / "cache/lock.json").write_text(json.dumps(pins))
    return source


def test_model_staging_honors_component_override_and_never_copies_unused_legacy_artifact(tmp_path):
    from bai_engine.config import ModelChoice, Profile
    from research.validate_real_video_runtime import prepare_models

    source = _pinned_model_source(tmp_path, ["legacy_unused", "selected_override"])
    profile = Profile(name="override", shuttle=ModelChoice(model="legacy_unused", backend="torch-cpu"), components={
        "shuttle": ModelChoice(model="selected_override", backend="torch-cpu"),
    })
    registry, report = prepare_models(source, tmp_path / "isolated", [profile])
    assert set(report["artifacts"]) == {"selected_override"}
    with registry.open_verified("selected_override") as artifact:
        assert artifact.stream.read() == b"controlled artifact selected_override"
    assert not (tmp_path / "isolated/cache/legacy_unused").exists()


def test_weightless_custom_component_override_needs_no_manifest_entry_or_unused_legacy_weights(tmp_path):
    from bai_engine.config import ModelChoice, Profile
    from research.validate_real_video_runtime import prepare_models

    source = _pinned_model_source(tmp_path, [])
    profile = Profile(name="weightless", shuttle=ModelChoice(model="must_not_load", backend="torch-cpu"), components={
        "shuttle": ModelChoice(model="in-memory-features", backend="none", implementation="custom-weightless"),
        "stroke": ModelChoice(model="stroke_rules_v0", backend="none"),
    })
    _, report = prepare_models(source, tmp_path / "isolated", [profile])
    assert report["artifacts"] == {}


def test_model_staging_includes_artifacts_for_selected_domain_components(tmp_path):
    from bai_engine.config import ModelChoice, Profile
    from research.validate_real_video_runtime import prepare_models

    source = _pinned_model_source(tmp_path, ["selected_classifier"])
    profile = Profile(name="domain-model", components={
        "stroke": ModelChoice(model="selected_classifier", backend="torch-cpu", implementation="custom-classifier"),
    })
    registry, report = prepare_models(source, tmp_path / "isolated", [profile])
    assert report["artifacts"]["selected_classifier"]["status"] == "verified_copy"
    with registry.open_verified("selected_classifier") as artifact:
        assert artifact.stream.read() == b"controlled artifact selected_classifier"


@pytest.mark.parametrize("match_format", [None, "singles", "doubles"])
def test_validation_roster_metadata_preserves_unknown_instead_of_silently_defaulting_singles(match_format):
    from bai_engine.schema.session import ParticipantRoster
    from research.validate_real_video_runtime import validation_roster_metadata

    roster = ParticipantRoster(match_format=match_format) if match_format is not None else None
    session = Session(title="Format provenance", source=Source(kind=SourceKind.UPLOAD, uri="fixture"), roster=roster)
    result = validation_roster_metadata(session)
    assert result["discipline"] == (match_format or "unknown")
    assert result["roster"] == (roster.model_dump(mode="json") if roster is not None else None)


def test_precision_override_changes_the_selected_component_instead_of_unused_legacy_choice():
    from bai_engine.config import ModelChoice, Profile
    from research.validate_real_video_runtime import override_shuttle_precision

    profile = Profile(name="precision", shuttle=ModelChoice(model="unused", backend="torch-cpu", precision="fp32"), components={
        "shuttle": ModelChoice(model="actual", backend="torch-cpu", precision="fp32"),
    })
    changed = override_shuttle_precision(profile, "fp16")
    assert changed.components["shuttle"].precision == "fp16"
    assert profile.components["shuttle"].precision == "fp32"


def _retention_sport():
    import msgpack

    class Sport:
        def __init__(self):
            self.calls = []

        def encode_perception(self, chunk):
            self.calls.append("encode")
            return msgpack.packb({
                "v": 15, "start": chunk.start, "end": chunk.end, "cr": chunk.cam_ref,
                "ci": {"court": "controlled-geometry", "fps": 30.0}, "models": chunk.models,
                "frames": [{"f": frame.frame_idx, "s": list(frame.shuttle_xy)} for frame in chunk.frames],
                "ocr": [],
            }, use_bin_type=True)

        def capabilities(self):
            return {"shuttle": {"status": "available", "model": "controlled@1"}}

        def ingest(self, chunk):
            self.calls.append("ingest")
            chunk.frames[0].shuttle_xy = (99.0, 88.0)

    return Sport()


def _retention_chunk():
    from bai_badminton.perception_types import ChunkPerception, FramePerception

    return ChunkPerception(0, 0, [FramePerception(0, (3.0, 4.0), .9)],
                           models={"shuttle": "controlled@1"}, cam_ref=17)


def test_optional_retention_encodes_before_ingest_mutation_and_records_replay_identity(tmp_path):
    import msgpack
    from research.validate_real_video_runtime import PerceptionRetention, ingest_with_retention

    root = tmp_path / "private-result"
    root.mkdir()
    sport, chunk = _retention_sport(), _retention_chunk()
    retained = PerceptionRetention(root, enabled=True)
    record, elapsed = ingest_with_retention(sport, chunk, retained)
    assert sport.calls == ["encode", "ingest"]
    assert chunk.frames[0].shuttle_xy == (99.0, 88.0)
    artifact = root / record["path"]
    payload = msgpack.unpackb(artifact.read_bytes(), raw=False)
    assert payload["frames"][0]["s"] == [3.0, 4.0]
    assert record["sha256"] == hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert record["canonical_frame_bounds"] == [0, 1]
    assert record["codec_version"] == 15 and record["cam_ref"] == 17
    assert record["codec_identity"] == {"court": "controlled-geometry", "fps": 30.0}
    assert record["capabilities"]["shuttle"]["status"] == "available"
    assert elapsed >= 0
    summary = retained.describe()
    assert summary["saved_chunks"] == 1
    assert summary["cached_perception_used"] is False
    assert summary["private_perception_state_restored"] is False
    assert summary["manifest_sha256"] == hashlib.sha256((root / summary["manifest"]).read_bytes()).hexdigest()
    assert set(path.suffix for path in (root / "perception").iterdir()) == {".msgpack", ".jsonl"}


def test_perception_retention_is_off_by_default_and_does_not_skip_real_ingest(tmp_path):
    from research.validate_real_video_runtime import PerceptionRetention, ingest_with_retention

    root = tmp_path / "default-result"
    root.mkdir()
    retained = PerceptionRetention(root)
    sport, chunk = _retention_sport(), _retention_chunk()
    record, _ = ingest_with_retention(sport, chunk, retained)
    assert record is None and sport.calls == ["ingest"]
    assert list(root.iterdir()) == []
    assert retained.describe()["enabled"] is False


def test_perception_retention_refuses_an_existing_output_directory(tmp_path):
    from research.validate_real_video_runtime import PerceptionRetention

    directory = tmp_path / "perception"
    directory.mkdir()
    kept = directory / "accepted-evidence.msgpack"
    kept.write_bytes(b"preserve existing evidence")
    with pytest.raises(FileExistsError):
        PerceptionRetention(tmp_path, enabled=True)
    assert kept.read_bytes() == b"preserve existing evidence"


def test_perception_retention_never_overwrites_a_segment_or_its_receipt(tmp_path):
    from research.validate_real_video_runtime import PerceptionRetention

    retained = PerceptionRetention(tmp_path, enabled=True)
    sport, chunk = _retention_sport(), _retention_chunk()
    record = retained.capture(sport, chunk)
    before = {path.name: path.read_bytes() for path in (tmp_path / "perception").iterdir()}
    with pytest.raises(FileExistsError):
        retained.capture(sport, chunk)
    assert {path.name: path.read_bytes() for path in (tmp_path / "perception").iterdir()} == before
    assert record["path"].endswith(".msgpack")


def test_perception_retention_rejects_invalid_frame_bounds_before_encoding(tmp_path):
    from research.validate_real_video_runtime import PerceptionRetention

    retained = PerceptionRetention(tmp_path, enabled=True)
    sport, chunk = _retention_sport(), _retention_chunk()
    chunk.end = 2
    with pytest.raises(ValueError, match="frame|bounds"):
        retained.capture(sport, chunk)
    assert sport.calls == []
    assert not list((tmp_path / "perception").glob("*.msgpack"))
