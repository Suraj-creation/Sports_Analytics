"""Portable schema-only catalogue/decoder compatibility; no video or model inference."""

import copy
import json
from dataclasses import asdict
from pathlib import Path

import msgpack
import pytest

from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.scene_change import ForegroundRegion
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.plugin import CODEC_VERSION, BadmintonSession
from bai_engine.config import Profile
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import MediaInfo, Session, Source, SourceKind
from bai_engine.schema.session import ParticipantRoster
from bai_engine.store import EventStore


@pytest.fixture
def closed_cache(tmp_path):
    profile = Profile.model_validate(
        {
            "name": "schema-only-test",
            "shuttle": {"model": "none", "backend": "none"},
            "player_detector": {"model": "none", "backend": "none"},
            "pose": {"model": "none", "backend": "none"},
            "stroke": {"model": "none", "backend": "none"},
            "components": {"stroke": {"model": "none", "backend": "none", "implementation": "stroke-rules-v0"}},
        }
    )
    record = Session(
        title="schema-only",
        source=Source(kind=SourceKind.UPLOAD, uri="synthetic.mp4"),
        media=MediaInfo(fps_num=25, fps_den=1, n_frames=100, width=1280, height=720, duration_us=4000000),
        roster=ParticipantRoster(match_format="singles"),
    )
    session = BadmintonSession(
        record,
        EventStore(tmp_path / "events.sqlite", record.session_id),
        profile,
        ModelRegistry(Path("models").resolve()),
        lambda _: None,
    )
    output = tmp_path / "run"
    directory = output / "data/sessions" / session.session.session_id / "perception"
    directory.mkdir(parents=True)
    frames = [
        FramePerception(
            f,
            None,
            0.0,
            view="main",
            calibration_state=CalibrationState.VALID,
            detector_observed=True,
            pose_stride=0,
            foreground_regions=(ForegroundRegion(f, "image-only", (10.0, 20.0, 40.0, 80.0), True, True),),
        )
        for f in range(100)
    ]
    value = msgpack.unpackb(
        session.encode_perception(ChunkPerception(0, 99, frames, models=dict(session.perception.models))), raw=False
    )
    assert value["v"] == CODEC_VERSION
    cache = directory / "seg_00000.msgpack"
    bindings = {
        "session_id": session.session.session_id,
        "source_sha256": "a" * 64,
        "proxy_sha256": "b" * 64,
        "media": {"n_frames": 100, "width": 1280, "height": 720, "fps_num": 25, "fps_den": 1},
    }

    def save(codec):
        record = copy.deepcopy(value)
        record["v"] = codec
        if codec < 22:
            for frame in record["frames"]:
                frame.pop("fg", None)
        cache.write_bytes(msgpack.packb(record, use_bin_type=True))
        return record

    yield output, cache, bindings, save
    session.close()


@pytest.fixture
def api():
    from research import pipeline_repair_completion as completed
    from research import production_external_stress as catalogue

    return catalogue, completed


def publish(catalogue, output, bindings, versions=None, other_limit=False):
    record = catalogue.perception_catalog(output, **bindings)
    if versions is not None:
        record["limits"]["accepted_codec_versions"] = versions
    if other_limit:
        record["limits"]["max_files"] -= 1
    path = output / catalogue.PERCEPTION_CATALOG_NAME
    path.write_text(json.dumps(record, indent=2) + "\n")
    return catalogue._perception_receipt(record, catalogue.digest(path))


@pytest.mark.parametrize("codec,versions", [(20, [20]), (20, [20, 21]), (21, [20, 21]), (22, [20, 21, 22]), (23, None)])
def test_original_catalogue_limits_are_preserved_for_matching_population(api, closed_cache, codec, versions):
    catalog, _ = api
    output, _, bindings, save = closed_cache
    save(codec)
    receipt = publish(catalog, output, bindings, versions)
    path = output / catalog.PERCEPTION_CATALOG_NAME
    original = path.read_bytes()
    checked = catalog.verify_perception_catalog(output, receipt, **bindings)
    assert checked["limits"]["accepted_codec_versions"] == (versions or [20, 21, 22, 23])
    assert checked["frame_count"] == 100 and path.read_bytes() == original


@pytest.mark.parametrize("versions", [[20], [20, 21], [21]])
def test_modern_population_cannot_acquire_an_old_acceptance_policy(api, closed_cache, versions):
    catalog, _ = api
    output, _, bindings, save = closed_cache
    save(22)
    receipt = publish(catalog, output, bindings, versions)
    with pytest.raises(ValueError, match="population/bytes/header"):
        catalog.verify_perception_catalog(output, receipt, **bindings)


def test_other_limits_are_not_normalized(api, closed_cache):
    catalog, _ = api
    output, _, bindings, save = closed_cache
    save(21)
    receipt = publish(catalog, output, bindings, [20, 21], other_limit=True)
    with pytest.raises(ValueError, match="population/bytes/header"):
        catalog.verify_perception_catalog(output, receipt, **bindings)
    expected = {
        "max_files": 10000,
        "max_source_frames": 2000000,
        "max_frames_per_cache": 4096,
        "max_cache_bytes": 16 * 1024 * 1024,
        "max_total_cache_bytes": 8 * 1024**3,
        "max_catalog_bytes": 8 * 1024 * 1024,
    }
    assert {k: catalog.PERCEPTION_CATALOG_LIMITS[k] for k in expected} == expected


def test_historical_public_wrapper_stays_strict21_while_completed_accepts22(api, closed_cache):
    _, completed = api
    _, cache, bindings, save = closed_cache
    record = save(22)
    payload = cache.read_bytes()
    with pytest.raises(ValueError, match="codec21 source profile/model/media identity mismatch"):
        completed.validate_cache21(payload, record["ci"]["profile"], bindings["media"])
    value, decoded = completed.validate_completed_cache(payload, record["ci"]["profile"], bindings["media"])
    assert value["v"] == 22 and len(decoded.frames[0].foreground_regions) == 1
    assert cache.read_bytes() == payload
    record = save(21)
    payload = cache.read_bytes()
    historical = completed.validate_cache21(payload, record["ci"]["profile"], bindings["media"])
    normal = completed.validate_completed_cache(payload, record["ci"]["profile"], bindings["media"])
    assert historical[0] == normal[0] and asdict(historical[1]) == asdict(normal[1])
    assert historical[1].frames[0].foreground_regions == ()


def test_unsupported_versions_stay_rejected(api, closed_cache):
    catalog, completed = api
    output, cache, bindings, save = closed_cache
    record = save(24)
    with pytest.raises(ValueError, match="unsupported cache codec"):
        catalog.perception_catalog(output, **bindings)
    for validator in [completed.validate_cache21, completed.validate_completed_cache]:
        with pytest.raises(ValueError):
            validator(cache.read_bytes(), record["ci"]["profile"], bindings["media"])


@pytest.mark.parametrize("kind", ["missing_fg", "stale_fg", "bool_coordinate", "duplicate_fg", "frame_gap"])
def test_current_source_observation_and_frame_contract_remains_checked(api, closed_cache, kind):
    catalog, completed = api
    output, cache, bindings, save = closed_cache
    record = save(22)
    frame = record["frames"][5]
    if kind == "missing_fg":
        frame.pop("fg")
    elif kind == "stale_fg":
        frame["fg"][0]["frame"] = 4
    elif kind == "bool_coordinate":
        frame["fg"][0]["bbox"][0] = True
    elif kind == "duplicate_fg":
        frame["fg"] *= 2
    else:
        frame["f"] = 6
    cache.write_bytes(msgpack.packb(record, use_bin_type=True))
    with pytest.raises(ValueError):
        catalog.perception_catalog(output, **bindings)
    if kind != "frame_gap":
        with pytest.raises(ValueError):
            completed.validate_completed_cache(cache.read_bytes(), record["ci"]["profile"], bindings["media"])
