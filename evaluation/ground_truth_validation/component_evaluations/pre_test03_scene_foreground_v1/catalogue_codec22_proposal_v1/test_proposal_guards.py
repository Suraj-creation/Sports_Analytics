"""Unit-test an UNAPPLIED patch's pure functions with native frozen codec22.

No module ROOT is assigned/rebased. AST extraction tests only the named pure
functions; this is not a candidate full-run completion or inference receipt.
"""

import ast
import copy
import hashlib
import inspect
import json
import math
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

import msgpack
import pytest

from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.scene_change import ForegroundRegion
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.plugin import BadmintonSession
from bai_engine.config import Profile
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import MediaInfo, Session, Source, SourceKind
from bai_engine.schema.session import ParticipantRoster
from bai_engine.store import EventStore

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parents[5] / "test03-scene-continuity-20261112"
FUNCTIONS = {"digest", "_perception_receipt", "perception_catalog", "verify_perception_catalog"}
CONSTANTS = {"PERCEPTION_CATALOG_SCHEMA", "PERCEPTION_CATALOG_NAME", "PERCEPTION_CATALOG_LIMITS"}


def extracted(path, names, constants=()):
    nodes = []
    for node in ast.parse(path.read_text()).body:
        if (isinstance(node, ast.FunctionDef) and node.name in names) or (
            isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in constants for t in node.targets)
        ):
            nodes.append(node)
    namespace = {
        "Path": Path,
        "copy": copy,
        "hashlib": hashlib,
        "json": json,
        "math": math,
        "SimpleNamespace": SimpleNamespace,
    }
    # Execute only explicitly selected pure functions from the pinned proposal;
    # never substitute a live module's ROOT or claim full-run validation.
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)  # noqa: S102
    assert "ROOT" not in namespace
    return SimpleNamespace(**namespace)


@pytest.fixture
def validators():
    # Fail instead of silently validating codec22 with MAIN's historical plugin.
    assert Path(inspect.getfile(BadmintonSession)).resolve().is_relative_to(CANDIDATE)
    proposed = HERE / "proposed_sources/research"
    catalogue = extracted(proposed / "production_external_stress.py", FUNCTIONS, CONSTANTS)
    completed = extracted(
        proposed / "pipeline_repair_completion.py",
        {"_validate_cache_context", "validate_cache21", "validate_completed_cache"},
    )
    original = extracted(HERE / "original_sources/research/pipeline_repair_completion.py", {"validate_cache21"})
    return catalogue, completed, original


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
    assert value["v"] == 22
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


def publish(catalogue, output, bindings, *, historical_versions=None, changed_limit=False):
    value = catalogue.perception_catalog(output, **bindings)
    if historical_versions is not None:
        value["limits"]["accepted_codec_versions"] = historical_versions
    if changed_limit:
        value["limits"]["max_files"] -= 1
    path = output / catalogue.PERCEPTION_CATALOG_NAME
    path.write_text(json.dumps(value, indent=2) + "\n")
    return catalogue._perception_receipt(value, catalogue.digest(path))


@pytest.mark.parametrize("codec,versions", [(20, [20]), (20, [20, 21]), (21, [20, 21]), (22, None)])
def test_published_catalogue_limits_keep_original_contract_when_population_fits(
    validators, closed_cache, codec, versions
):
    catalogue, _, _ = validators
    output, _, bindings, save = closed_cache
    save(codec)
    receipt = publish(catalogue, output, bindings, historical_versions=versions)
    before = (output / catalogue.PERCEPTION_CATALOG_NAME).read_bytes()
    checked = catalogue.verify_perception_catalog(output, receipt, **bindings)
    assert checked["frame_count"] == 100
    assert checked["limits"]["accepted_codec_versions"] == (versions or [20, 21, 22])
    assert (output / catalogue.PERCEPTION_CATALOG_NAME).read_bytes() == before


@pytest.mark.parametrize("versions", [[20], [20, 21], [21]])
def test_codec22_cannot_be_laundered_into_historical_acceptance_limits(validators, closed_cache, versions):
    catalogue, _, _ = validators
    output, _, bindings, save = closed_cache
    save(22)
    receipt = publish(catalogue, output, bindings, historical_versions=versions)
    with pytest.raises(ValueError, match="population/bytes/header"):
        catalogue.verify_perception_catalog(output, receipt, **bindings)


def test_all_other_catalogue_size_limits_remain_exact(validators, closed_cache):
    catalogue, _, _ = validators
    output, _, bindings, save = closed_cache
    save(21)
    receipt = publish(catalogue, output, bindings, historical_versions=[20, 21], changed_limit=True)
    with pytest.raises(ValueError, match="population/bytes/header"):
        catalogue.verify_perception_catalog(output, receipt, **bindings)
    original = extracted(HERE / "original_sources/research/production_external_stress.py", FUNCTIONS, CONSTANTS)
    for key, value in original.PERCEPTION_CATALOG_LIMITS.items():
        if key != "accepted_codec_versions":
            assert catalogue.PERCEPTION_CATALOG_LIMITS[key] == value


def test_unsupported_cache_version_remains_rejected(validators, closed_cache):
    catalogue, completed, original = validators
    output, cache, bindings, save = closed_cache
    record = save(23)
    with pytest.raises(ValueError, match="unsupported cache codec"):
        catalogue.perception_catalog(output, **bindings)
    for validate in [completed.validate_cache21, completed.validate_completed_cache, original.validate_cache21]:
        with pytest.raises(ValueError):
            validate(cache.read_bytes(), record["ci"]["profile"], bindings["media"])


def test_public_historical_validator_stays_strict21_and_completed_wrapper_accepts22(validators, closed_cache):
    _, completed, original = validators
    _, cache, bindings, save = closed_cache
    record = save(22)
    payload = cache.read_bytes()
    for validate in [completed.validate_cache21, original.validate_cache21]:
        with pytest.raises(ValueError, match="codec21 source profile/model/media identity mismatch"):
            validate(payload, record["ci"]["profile"], bindings["media"])
    value, decoded = completed.validate_completed_cache(payload, record["ci"]["profile"], bindings["media"])
    assert value["v"] == 22 and len(decoded.frames[0].foreground_regions) == 1
    assert cache.read_bytes() == payload
    record = save(21)
    payload = cache.read_bytes()
    before = original.validate_cache21(payload, record["ci"]["profile"], bindings["media"])
    after = completed.validate_cache21(payload, record["ci"]["profile"], bindings["media"])
    normal = completed.validate_completed_cache(payload, record["ci"]["profile"], bindings["media"])
    assert before[0] == after[0] == normal[0]
    assert asdict(before[1]) == asdict(after[1]) == asdict(normal[1])
    assert after[1].frames[0].foreground_regions == ()


@pytest.mark.parametrize("corruption", ["missing_fg", "stale_fg", "bool_coordinate", "duplicate_fg", "frame_gap"])
def test_native_codec22_decoder_still_rejects_corrupted_observation_contract(validators, closed_cache, corruption):
    catalogue, completed, _ = validators
    output, cache, bindings, save = closed_cache
    record = save(22)
    frame = record["frames"][5]
    if corruption == "missing_fg":
        frame.pop("fg")
    elif corruption == "stale_fg":
        frame["fg"][0]["frame"] = 4
    elif corruption == "bool_coordinate":
        frame["fg"][0]["bbox"][0] = True
    elif corruption == "duplicate_fg":
        frame["fg"] *= 2
    else:
        frame["f"] = 6
    cache.write_bytes(msgpack.packb(record, use_bin_type=True))
    with pytest.raises(ValueError):
        catalogue.perception_catalog(output, **bindings)
    if corruption != "frame_gap":
        with pytest.raises(ValueError):
            completed.validate_completed_cache(cache.read_bytes(), record["ci"]["profile"], bindings["media"])


def test_normal_timestamp_method_changes_only_validator_selection():
    old = ast.parse((HERE / "original_sources/research/normal_timestamp_audit.py").read_text())
    new = ast.parse((HERE / "proposed_sources/research/normal_timestamp_audit.py").read_text())
    for node in ast.walk(new):
        if isinstance(node, ast.alias) and node.name == "validate_completed_cache":
            node.name = "validate_cache21"
        if isinstance(node, ast.Name) and node.id == "validate_completed_cache":
            node.id = "validate_cache21"
    assert ast.dump(old) == ast.dump(new)
    old_tree = ast.parse((HERE / "original_sources/research/pipeline_repair_completion.py").read_text())
    new_tree = ast.parse((HERE / "proposed_sources/research/pipeline_repair_completion.py").read_text())
    for name in ["decode_source_pts", "verify_proxy", "cache_catalog"]:
        before = next(n for n in old_tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
        after = next(n for n in new_tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
        assert ast.dump(before) == ast.dump(after)
