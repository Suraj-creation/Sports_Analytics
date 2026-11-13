"""Catalogue21 contracts; candidate mode executes copied source, never edits workers.

Before the guarded workers close, CATALOG_CODEC21_CANDIDATE may point to the
external proposed source snapshot. Normal execution always tests the real tool.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from types import ModuleType, SimpleNamespace

import msgpack
import numpy as np
import pytest

from bai_badminton.perception.association import ShuttleObservationEvidence
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.content import SceneDecisionEvidence
from bai_badminton.perception.diagnostics import FrameDiagnostic
from bai_badminton.perception.scene_change import ForegroundRegion, RegionContinuity, SceneChangeEvidence
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs
from bai_badminton.plugin import BadmintonSession
from bai_engine.config import ModelChoice, Profile
from research import production_external_stress as actual_tool


@pytest.fixture
def tool():
    path = Path(actual_tool.__file__)
    original_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    candidate_path = os.environ.get("CATALOG_CODEC21_CANDIDATE")
    if candidate_path:
        # Explicit preparation-only opt-in. Ordinary tests never repair or
        # replace the implementation under test, so a later regression is red.
        module = ModuleType("isolated_catalog_codec21_candidate")
        module.__file__ = str(path)
        source = Path(candidate_path).read_text()
        exec(compile(source, str(path), "exec"), module.__dict__)
    else:
        module = actual_tool
    yield module
    assert hashlib.sha256(path.read_bytes()).hexdigest() == original_sha


@pytest.fixture
def completed(tmp_path):
    output = tmp_path / "run"
    directory = output / "data/sessions/Controlled/perception"
    directory.mkdir(parents=True)
    models = {"player_detector": "detector@1", "shuttle": "shuttle@1"}
    profile = Profile(
        name="catalogue-contract",
        components={
            "content_continuity": ModelChoice(
                model="none",
                backend="none",
                implementation="foreground-content-continuity-v2",
                params={"mode": "barrier_detector_layout_v2"},
            ),
        },
    )
    identity = {
        "fps": 30.0,
        "frame_size": [640, 360],
        "loaded_models": models,
        "profile": profile.model_dump(mode="json"),
    }
    receiver = SimpleNamespace(_isolation_id=lambda: identity)
    boxes = ((100.0, 100.0, 200.0, 300.0), (400.0, 100.0, 500.0, 300.0))
    regions = tuple(
        RegionContinuity(ForegroundRegion(0, f"track:{i}", box, True, True), 10, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0)
        for i, box in enumerate(boxes)
    )
    raw = SceneChangeEvidence(1, 0, "hypothesis", True, ("appearance_discontinuity",), regions)
    decision = SceneDecisionEvidence(
        1,
        0,
        "no_barrier",
        "current_layout_matches",
        True,
        1,
        models["player_detector"],
        "a" * 64,
        (360, 640, 3),
        boxes,
        (0.9, 0.9),
        (0, 1),
        ((0, 0), (1, 1)),
        previous_region_count=2,
    )
    first = FramePerception(
        0, None, 0.0, view="main", calibration_state=CalibrationState.VALID, detector_observed=False, pose_stride=0
    )
    last = FramePerception(
        1,
        None,
        0.0,
        view="main",
        calibration_state=CalibrationState.VALID,
        detector_observed=True,
        pose_stride=1,
        content_change=raw,
        content_decision=decision,
        persons=[
            PersonObs(
                1,
                np.asarray(boxes[0]),
                0.9,
                raw_track_id=1,
                detector_matched=True,
                pose_frame_idx=1,
                racket_frame_idx=1,
            )
        ],
        diagnostic=FrameDiagnostic(1, 1 / 30, 0, "main", "VALID", None, "model_ran", models["shuttle"]),
        shuttle_observation=ShuttleObservationEvidence(1, 0, "missing", "unknown", None, None, 0.0),
    )
    payload = BadmintonSession.encode_perception(receiver, ChunkPerception(0, 1, [first, last], models=models))
    value = msgpack.unpackb(payload, raw=False)
    # Construct controlled SYNTHETIC historical21 wire data independently of
    # the latest writer version. This is not real-run header rewriting or
    # recovery: no source footage, worker receipt or observation is reused.
    assert value["v"] in (21, 22, 23)
    value["v"] = 21
    for frame in value["frames"]:
        frame.pop("fg", None)
        if frame.get("cc"):
            frame["cc"].pop("supporting_region_keys", None)
            frame["cc"].pop("witness_parameters", None)
            frame["cc"].pop("acquisition_region_keys", None)
            frame["cc"].pop("relative_region_keys", None)
        if frame.get("cd"):
            frame["cd"].pop("supporting_region_keys", None)
            frame["cd"].pop("layout_indices", None)
            for field in (
                "acquisition_region_keys",
                "relative_region_keys",
                "court_polygon",
                "court_indices",
                "expected_participants",
                "geometry_valid",
                "previous_to_current",
                "previous_camera",
            ):
                frame["cd"].pop(field, None)
    payload = msgpack.packb(value, use_bin_type=True)
    assert value["v"] == 21
    path = directory / "seg_00000.msgpack"
    path.write_bytes(payload)
    bindings = {
        "session_id": "Controlled",
        "source_sha256": "b" * 64,
        "proxy_sha256": "c" * 64,
        "media": {"n_frames": 2, "width": 640, "height": 360, "fps_num": 30, "fps_den": 1},
    }
    return output, path, value, bindings


def save(path, value):
    path.write_bytes(msgpack.packb(value, use_bin_type=True))


def test_real_codec21_decoder_is_used_and_roundtrip_catalog_is_bound(tool, completed, monkeypatch):
    output, path, _, bindings = completed
    calls = []
    decode = BadmintonSession.decode_perception

    def record(receiver, data, *, diagnostic=False):
        calls.append((data, diagnostic))
        return decode(receiver, data, diagnostic=diagnostic)

    monkeypatch.setattr(BadmintonSession, "decode_perception", record)
    receipt = tool.write_perception_catalog(output, **bindings)
    verified = tool.verify_perception_catalog(output, receipt, **bindings)
    assert len(calls) == 2 and all(data == path.read_bytes() and diagnostic for data, diagnostic in calls)
    assert verified["files"][0]["codec_version"] == 21
    assert verified["limits"]["accepted_codec_versions"] == [20, 21, 22, 23]
    assert verified["source_sha256"] == bindings["source_sha256"]
    assert verified["files"][0]["sha256"] == tool.digest(path)


def test_codec20_legacy_header_contract_remains_supported(tool, completed):
    output, path, value, bindings = completed
    value["v"] = 20
    value["ci"] = {"fps": 30.0, "frame_size": [640, 360]}
    value["frames"] = [{"f": 0}, {"f": 1}]
    save(path, value)
    assert tool.perception_catalog(output, **bindings)["frame_count"] == 2


@pytest.mark.parametrize("version", [17, 19, 24, 999, True])
def test_no_legacy_or_future_codec_allowlist_bypass(tool, completed, version):
    output, path, value, bindings = completed
    value["v"] = version
    save(path, value)
    with pytest.raises(ValueError, match=r"cache.*(version|header)"):
        tool.perception_catalog(output, **bindings)


@pytest.mark.parametrize(
    "field,bad",
    [
        ("frame", 2),
        ("previous_frame", 1),
        ("detector_frame", 0),
        ("detector_model", "foreign@2"),
        ("detector_image_sha256", "invalid"),
        ("detector_image_shape", [720, 1280, 3]),
        ("raw_hypothesis", False),
        ("previous_region_count", 3),
        ("detector_boxes", [[250.0, 100.0, 300.0, 300.0], [550.0, 100.0, 600.0, 300.0]]),
    ],
)
def test_codec21_production_decoder_rejects_false_decision_provenance(tool, completed, field, bad):
    output, path, value, bindings = completed
    value["frames"][1]["cd"][field] = bad
    save(path, value)
    with pytest.raises(ValueError, match="bounded perception diagnostic"):
        tool.perception_catalog(output, **bindings)


@pytest.mark.parametrize("field", ["cd", "dg", "sa", "ce"])
def test_codec21_required_schema_cannot_be_dropped(tool, completed, field):
    output, path, value, bindings = completed
    del value["frames"][1][field]
    save(path, value)
    with pytest.raises(ValueError, match=r"perception|metadata"):
        tool.perception_catalog(output, **bindings)


def test_selected_layout_policy_cannot_drop_required_source_decision(tool, completed):
    output, path, value, bindings = completed
    value["frames"][1]["cd"] = None
    save(path, value)
    with pytest.raises(ValueError, match="mandatory source decision"):
        tool.perception_catalog(output, **bindings)


@pytest.mark.parametrize("field,bad", [("provider", "foreign@2"), ("canonical_time_sec", 42.0)])
def test_diagnostic_model_and_clock_stay_bound(tool, completed, field, bad):
    output, path, value, bindings = completed
    value["frames"][1]["dg"][field] = bad
    save(path, value)
    with pytest.raises(ValueError, match=r"diagnostic.*(provider|timestamp)"):
        tool.perception_catalog(output, **bindings)


def test_association_must_match_raw_source_frame(tool, completed):
    output, path, value, bindings = completed
    value["frames"][1]["sa"]["frame_idx"] = 0
    save(path, value)
    with pytest.raises(ValueError, match="association provenance"):
        tool.perception_catalog(output, **bindings)


@pytest.mark.parametrize("field", ["pf", "rf"])
def test_pose_racket_future_source_provenance_is_rejected(tool, completed, field):
    output, path, value, bindings = completed
    value["frames"][1]["p"][0][field] = 2
    save(path, value)
    with pytest.raises(ValueError, match="source-frame provenance"):
        tool.perception_catalog(output, **bindings)


@pytest.mark.parametrize("field", ["loaded_models", "profile", "fps", "frame_size"])
def test_cache_identity_fields_are_validated_not_echoed_as_proof(tool, completed, field):
    output, path, value, bindings = completed
    value["ci"][field] = {"different": "model@2"} if field == "loaded_models" else None
    save(path, value)
    with pytest.raises(ValueError):
        tool.perception_catalog(output, **bindings)


@pytest.mark.parametrize("field", ["source_sha256", "proxy_sha256"])
def test_external_source_receipt_binding_cannot_be_reassigned(tool, completed, field):
    output, _, _, bindings = completed
    receipt = tool.write_perception_catalog(output, **bindings)
    changed = copy.deepcopy(bindings)
    changed[field] = "d" * 64
    with pytest.raises(ValueError, match="binding mismatch"):
        tool.verify_perception_catalog(output, receipt, **changed)


def old_codec20_catalog(tool, completed):
    output, path, value, bindings = completed
    value["v"] = 20
    save(path, value)
    receipt = tool.write_perception_catalog(output, **bindings)
    target = output / tool.PERCEPTION_CATALOG_NAME
    recorded = json.loads(target.read_text())
    recorded["limits"]["accepted_codec_versions"] = [20]
    target.write_text(json.dumps(recorded))
    receipt["sha256"] = tool.digest(target)
    return receipt, target, recorded


def test_old_published_codec20_catalog_remains_verifiable_without_rewriting(tool, completed):
    output, _, _, bindings = completed
    receipt, target, recorded = old_codec20_catalog(tool, completed)
    before = target.read_bytes()
    assert tool.verify_perception_catalog(output, receipt, **bindings) == recorded
    assert target.read_bytes() == before
    assert tool.PERCEPTION_CATALOG_LIMITS["accepted_codec_versions"] == [20, 21, 22, 23]


@pytest.mark.parametrize("change", ["bounds", "schema", "source", "cache_bytes"])
def test_legacy_metadata_normalization_does_not_weaken_other_guards(tool, completed, change):
    output, path, value, bindings = completed
    receipt, target, recorded = old_codec20_catalog(tool, completed)
    if change == "bounds":
        recorded["limits"]["max_cache_bytes"] -= 1
    elif change == "schema":
        recorded["schema"] = "foreign-catalogue:v1"
    elif change == "source":
        recorded["source_sha256"] = "e" * 64
    else:
        value["v"] = 20
        value["models"]["player_detector"] = "changed_after_receipt@2"
        save(path, value)
    target.write_text(json.dumps(recorded))
    receipt["sha256"] = tool.digest(target)
    with pytest.raises(ValueError, match="binding mismatch"):
        tool.verify_perception_catalog(output, receipt, **bindings)


@pytest.mark.parametrize("mixed", [False, True])
def test_codec21_or_mixed_population_cannot_claim_legacy20_limits(tool, completed, mixed):
    output, path, value, bindings = completed
    if mixed:
        first = copy.deepcopy(value)
        first.update(v=20, end=0, frames=value["frames"][:1])
        second = copy.deepcopy(value)
        second.update(start=1, frames=value["frames"][1:])
        save(path, first)
        save(path.with_name("seg_00001.msgpack"), second)
    receipt = tool.write_perception_catalog(output, **bindings)
    target = output / tool.PERCEPTION_CATALOG_NAME
    recorded = json.loads(target.read_text())
    recorded["limits"]["accepted_codec_versions"] = [20]
    target.write_text(json.dumps(recorded))
    receipt["sha256"] = tool.digest(target)
    with pytest.raises(ValueError, match="binding mismatch"):
        tool.verify_perception_catalog(output, receipt, **bindings)
