"""Small source/receipt/cache fixtures; no real test videos, models or inference."""

import argparse
import csv
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path

import av
import msgpack
import numpy as np
import pytest

SPEC = importlib.util.spec_from_file_location(
    "visual_evidence", Path(__file__).with_name("render_validation_evidence.py")
)
tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tool)


def write(path, value):
    path.write_text(json.dumps(value))


def movie(path):
    with av.open(str(path), "w") as container:
        stream = container.add_stream("mpeg4", rate=24)
        stream.width, stream.height, stream.pix_fmt = 64, 48, "yuv420p"
        for i in range(4):
            frame = av.VideoFrame.from_ndarray(np.full((48, 64, 3), i * 50, dtype=np.uint8), format="bgr24")
            frame.pts, frame.time_base = i, Fraction(1, 24)
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)


def make_run(tmp, name, source, *, codec=21):
    parent = tmp / name
    run, protocol, code = parent / "run", parent / "protocol", tmp / "recorded_checkout"
    run.mkdir(parents=True)
    protocol.mkdir()
    code.mkdir(exist_ok=True)
    source_models = code / "models"
    (source_models / "cache").mkdir(parents=True, exist_ok=True)
    (source_models / "manifest.yaml").write_text("models: {}\n")
    pins = {"fixture_model": "a" * 64}
    (source_models / "cache/lock.json").write_text(json.dumps(pins, indent=4) + "\n")
    staged_models = run / "models"
    (staged_models / "cache").mkdir(parents=True)
    (staged_models / "manifest.yaml").write_bytes((source_models / "manifest.yaml").read_bytes())
    (staged_models / "cache/lock.json").write_text(json.dumps(pins, indent=2) + "\n")
    media = dict(n_frames=4, width=64, height=48, fps_num=24, fps_den=1, source_width=64, source_height=48)
    source_sha = tool.sha(source)
    sid = "SYNTHETICDOUBLES"
    original = protocol / "source_session.json"
    session = {
        "session_id": sid,
        "status": "analysed",
        "frontier_frame": 3,
        "media": media,
        "source": {"uri": str(source), "sha256": source_sha},
    }
    write(original, session)
    write(run / "session.json", session)
    proxy = run / "data/media" / source_sha / "proxy.mp4"
    proxy.parent.mkdir(parents=True)
    proxy.write_bytes(source.read_bytes())
    cache_dir = run / "data/sessions" / sid / "perception"
    cache_dir.mkdir(parents=True)
    people = [
        {
            "t": i,
            "rt": i,
            "b": [i * 12, 10, i * 12 + 9, 35],
            "c": 0.9,
            "dm": True,
            "pf": 1,
            "rf": None,
            "k": None,
            "rk": None,
        }
        for i in range(4)
    ]
    chunk = {
        "v": codec,
        "start": 0,
        "end": 3,
        "cr": "fixture",
        "ci": {"frame_size": [64, 48], "fps": 24, "profile": {}, "loaded_models": {}},
        "models": {},
        "frames": [
            {
                "f": i,
                "p": people,
                "s": None,
                "sa": {"status": "missing", "association_status": "unknown"},
                "v": "main",
                "cs": "VALID",
                "ce": 0,
            }
            for i in range(4)
        ],
    }
    if codec >= 22:
        for frame in chunk["frames"]:
            frame["fg"] = [
                {
                    "frame": frame["f"],
                    "key": f"image-context:{i}",
                    "bbox": [i * 10, 2, i * 10 + 8, 20],
                    "detector_matched": None,
                    "detector_observed": False,
                }
                for i in range(3)
            ]
    cache = cache_dir / "seg_00000.msgpack"
    cache.write_bytes(msgpack.packb(chunk))
    header = {k: chunk.get(k) for k in ("v", "start", "end", "cr", "ci", "models")}
    import hashlib

    item = {
        "path": str(cache.relative_to(run)),
        "bytes": cache.stat().st_size,
        "sha256": tool.sha(cache),
        "codec_version": codec,
        "start": 0,
        "end": 3,
        "frame_count": 4,
        "header_sha256": hashlib.sha256(json.dumps(header, sort_keys=True, allow_nan=False).encode()).hexdigest(),
    }
    catalogue = {
        "schema": "production-perception-completion-catalog:v1",
        "snapshot_stage": "after_analysis_before_worker_completion_receipt",
        "session_id": sid,
        "source_sha256": source_sha,
        "proxy_sha256": source_sha,
        "media": {k: media[k] for k in ("n_frames", "width", "height", "fps_num", "fps_den")},
        "frame_count": 4,
        "file_count": 1,
        "total_bytes": item["bytes"],
        "files": [item],
    }
    write(run / "perception_completion_catalog.json", catalogue)
    receipt = {k: catalogue[k] for k in ("schema", "snapshot_stage", "frame_count", "file_count")}
    receipt.update(
        path="perception_completion_catalog.json", sha256=tool.sha(run / "perception_completion_catalog.json")
    )
    info = {
        "status": "completed",
        "cached_perception_used": False,
        "media": media,
        "frames_processed": 4,
        "frontier_frame": 3,
        "source_sha256": source_sha,
        "proxy_sha256": source_sha,
        "profile": {},
        "models": {
            "manifest_sha256": tool.sha(source_models / "manifest.yaml"),
            "pins_sha256": hashlib.sha256(json.dumps(pins, sort_keys=True, allow_nan=False).encode()).hexdigest(),
        },
        "perception_cache_catalog": receipt,
    }
    write(run / "inference.json", info)
    plan = {
        "cases": {
            "fixture": {
                "kind": "production_upload",
                "session": str(original),
                "source": str(source),
                "source_sha256": source_sha,
                "frames": 4,
            }
        },
        "input_files_sha256": {
            str(original): tool.sha(original),
            str(source): source_sha,
            str(source_models / "cache/lock.json"): tool.sha(source_models / "cache/lock.json"),
        },
        "source_files_sha256": {str(code / "engine/src/example.py"): "fixture-source-digest"},
        "code_commit": "synthetic_fixture",
    }
    write(protocol / "plan.json", plan)
    executor = {
        "status": "completed",
        "worker_exit_code": 0,
        "frozen_source_inputs_unchanged": True,
        "worker_report_sha256": tool.sha(run / "inference.json"),
        "output_proxy_sha256": source_sha,
        "command": ["python", "worker.py", "--plan", str(protocol / "plan.json")],
        "plan_sha256": tool.sha(protocol / "plan.json"),
        "case": "fixture",
        "perception_cache_catalog_verification": {
            "status": "verified",
            "catalog_sha256": receipt["sha256"],
            "frames": 4,
            "files": 1,
        },
    }
    write(run.with_suffix(".executor.json"), executor)
    (run / "events.jsonl").write_text(
        json.dumps(
            {
                "type": "contact",
                "frame_start": 1,
                "frame_end": 1,
                "payload": {"physical_status": "unknown", "stroke": "unknown"},
            }
        )
        + "\n"
    )
    timestamps = parent / "timestamps"
    timestamps.mkdir()
    pts = timestamps / "source_frame_pts.csv"
    with av.open(str(source)) as container, pts.open("w") as stream:
        writer = csv.writer(stream)
        writer.writerow(["source_frame", "pts", "time_base_num", "time_base_den", "source_time_sec"])
        for i, frame in enumerate(container.decode(video=0)):
            writer.writerow(
                [
                    i,
                    frame.pts,
                    frame.time_base.numerator,
                    frame.time_base.denominator,
                    float(frame.pts * frame.time_base),
                ]
            )
    audit = {
        "source_sha256": source_sha,
        "proxy_sha256": source_sha,
        "source_pts_csv_sha256": tool.sha(pts),
        "frames_decoded": 4,
        "exact_pts_frames": 4,
        "source_proxy_full_rational_pts_equal": True,
        "origin_rational_seconds": "0",
        "input_sha256": {str(run / "inference.json"): tool.sha(run / "inference.json")},
    }
    write(timestamps / "timestamp_audit.json", audit)
    return run, pts, code


@pytest.fixture
def fixture(tmp_path):
    source = tmp_path / "original.mp4"
    movie(source)
    run, pts, code = make_run(tmp_path, "current", source)
    args = argparse.Namespace(
        run=run,
        source_video=source,
        source_pts=pts,
        output=tmp_path / "NEW_evidence",
        dataset_label="Synthetic four-player set",
        pipeline_root=code,
        pts_audit=None,
        baseline_run=None,
        baseline_pipeline_root=None,
        baseline_pts_audit=None,
        frames_json=None,
        frames="1",
    )
    return args


def test_valid_render_preserves_four_players_exact_pts_and_inputs(fixture, tmp_path):
    args = fixture
    before = {str(p): tool.sha(p) for p in tmp_path.rglob("*") if p.is_file()}
    tool.main(args)
    completion = tool.read(args.output / "completion.json")
    assert completion["dataset_label"] == "Synthetic four-player set"
    assert not completion["neural_inference_performed"] and not completion["physical_gt_created"]
    raw = tool.read(args.output / "frame_0000001/current_raw_frame.json")
    assert len(raw["p"]) == 4
    evidence = tool.read(args.output / "frame_0000001/evidence.json")
    assert evidence["source_decode"]["seconds_rational"] == "1/24"
    assert evidence["arms"]["current"]["proxy_decode"]["seconds_rational"] == "1/24"
    assert all(tool.sha(path) == digest for path, digest in before.items())
    assert (args.output / "executed_tool.py.source").read_bytes() == Path(tool.__file__).read_bytes()
    assert all(tool.sha(args.output / name) == digest for name, digest in completion["artifact_sha256"].items())
    sentinel = (args.output / "index.md").read_bytes()
    with pytest.raises(ValueError, match="NEW output"):
        tool.main(args)
    assert (args.output / "index.md").read_bytes() == sentinel


def test_baseline_has_own_receipts_and_caption_reference(fixture, tmp_path):
    args = fixture
    baseline, _, root = make_run(tmp_path, "baseline", args.source_video)
    args.baseline_run, args.baseline_pipeline_root = baseline, root
    reference = tmp_path / "supplied.json"
    write(
        reference,
        {
            "source_sha256": tool.sha(args.source_video),
            "comparison": [{"expected_start": 1, "actual_start": 2, "role": "generated reference"}],
        },
    )
    frames = tmp_path / "frames.json"
    write(
        frames,
        {
            "source_sha256": tool.sha(args.source_video),
            "frames": [
                {
                    "frame": 1,
                    "caption": "<script>not HTML</script>",
                    "reference_rows": [
                        {
                            "file": str(reference),
                            "pointer": "/comparison/0",
                            "role": "legacy_generated_reference_agreement",
                        }
                    ],
                }
            ],
        },
    )
    args.frames_json, args.frames = frames, None
    tool.main(args)
    result = tool.read(args.output / "completion.json")
    assert result["arms"] == ["current", "baseline"]
    assert "&lt;script&gt;" in (args.output / "index.html").read_text()
    assert "<script>not HTML</script>" not in (args.output / "index.html").read_text()
    assert "expected_start" in (args.output / "index.md").read_text()
    assert (args.output / "baseline/selected_events.json").is_file()


@pytest.mark.parametrize("frames", ["-1", "4", "true", "1,1"])
def test_bad_frame_request_refuses_before_output(fixture, frames):
    fixture.frames = frames
    with pytest.raises((ValueError, TypeError)):
        tool.main(fixture)
    assert not fixture.output.exists()


@pytest.mark.parametrize("value", [[True], [None], list(range(129)), {"source_sha256": "foreign", "frames": [1]}])
def test_manifest_wrong_source_types_and_curated_limit(value):
    with pytest.raises(ValueError):
        tool.requested_frames(value, 200, "exact-source")


def test_wrong_source_and_pipeline_root_rejected(fixture, tmp_path):
    other = tmp_path / "wrong.mp4"
    other.write_bytes(fixture.source_video.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="Source SHA"):
        tool.verify_run(fixture.run, other, fixture.pipeline_root)
    with pytest.raises(ValueError, match="recorded source root"):
        tool.verify_run(fixture.run, fixture.source_video, tmp_path / "foreign_checkout")


@pytest.mark.parametrize("target", ["worker", "parent", "cache", "catalogue", "session"])
def test_incomplete_or_changed_receipts_and_bytes(fixture, target):
    run = fixture.run
    if target == "worker":
        doc = tool.read(run / "inference.json")
        doc["status"] = "running"
        write(run / "inference.json", doc)
    elif target == "parent":
        doc = tool.read(run.with_suffix(".executor.json"))
        doc["worker_exit_code"] = 1
        write(run.with_suffix(".executor.json"), doc)
    elif target == "cache":
        p = next((run / "data/sessions/SYNTHETICDOUBLES/perception").glob("*.msgpack"))
        p.write_bytes(p.read_bytes() + b"bad")
    elif target == "catalogue":
        p = run / "perception_completion_catalog.json"
        p.write_text(p.read_text() + " ")
    else:
        doc = tool.read(run / "session.json")
        doc["frontier_frame"] = 2
        write(run / "session.json", doc)
    with pytest.raises(ValueError):
        tool.main(fixture)
    assert not fixture.output.exists()


def test_full_pts_mapping_and_other_run_audit_rejected(fixture, tmp_path):
    bound = tool.verify_run(fixture.run, fixture.source_video, fixture.pipeline_root)
    audit = fixture.source_pts.parent / "timestamp_audit.json"
    value = tool.read(audit)
    value["source_pts_csv_sha256"] = "bad"
    write(audit, value)
    with pytest.raises(ValueError, match="PTS audit"):
        tool.verify_pts(fixture.source_pts, audit, bound)
    value["source_pts_csv_sha256"] = tool.sha(fixture.source_pts)
    rows = list(csv.reader(fixture.source_pts.open()))
    rows[2][1] = str(int(rows[2][1]) + 1)
    with fixture.source_pts.open("w") as stream:
        csv.writer(stream).writerows(rows)
    value["source_pts_csv_sha256"] = tool.sha(fixture.source_pts)
    write(audit, value)
    with pytest.raises(ValueError, match="fully map"):
        tool.verify_pts(fixture.source_pts, audit, bound)


@pytest.mark.parametrize("corruption", ["frame_id", "models", "dimensions"])
def test_rehashed_cache_still_requires_real_header_extent_identity(fixture, corruption):
    """A consistent outer digest chain cannot excuse malformed inner coverage."""
    import hashlib

    run = fixture.run
    cache = next((run / "data/sessions/SYNTHETICDOUBLES/perception").glob("*.msgpack"))
    chunk = msgpack.unpackb(cache.read_bytes(), raw=False)
    if corruption == "frame_id":
        chunk["frames"][1]["f"] = 2
    elif corruption == "models":
        chunk["models"] = {"foreign": "model"}
    else:
        chunk["ci"]["frame_size"] = [999, 48]
    cache.write_bytes(msgpack.packb(chunk))
    catalog_path = run / "perception_completion_catalog.json"
    catalog = tool.read(catalog_path)
    row = catalog["files"][0]
    row["sha256"], row["bytes"] = tool.sha(cache), cache.stat().st_size
    header = {k: chunk.get(k) for k in ("v", "start", "end", "cr", "ci", "models")}
    row["header_sha256"] = hashlib.sha256(json.dumps(header, sort_keys=True, allow_nan=False).encode()).hexdigest()
    catalog["total_bytes"] = row["bytes"]
    write(catalog_path, catalog)
    info = tool.read(run / "inference.json")
    info["perception_cache_catalog"]["sha256"] = tool.sha(catalog_path)
    write(run / "inference.json", info)
    parent_path = run.with_suffix(".executor.json")
    parent = tool.read(parent_path)
    parent["worker_report_sha256"] = tool.sha(run / "inference.json")
    parent["perception_cache_catalog_verification"]["catalog_sha256"] = tool.sha(catalog_path)
    write(parent_path, parent)
    with pytest.raises(ValueError, match="header/models/profile/frame extent"):
        tool.verify_run(run, fixture.source_video, fixture.pipeline_root)


def test_failed_baseline_never_creates_output(fixture, tmp_path):
    baseline, _, root = make_run(tmp_path, "baseline", fixture.source_video)
    fixture.baseline_run, fixture.baseline_pipeline_root = baseline, root
    p = baseline.with_suffix(".executor.json")
    value = tool.read(p)
    value["status"] = "failed"
    write(p, value)
    with pytest.raises(ValueError, match="worker"):
        tool.main(fixture)
    assert not fixture.output.exists()


def test_exact_decoder_rejects_nonexistent_pts_and_wrong_shape(fixture):
    with pytest.raises(ValueError):
        tool.exact_frame(fixture.source_video, Fraction(1, 23), (48, 64, 3))
    with pytest.raises(ValueError, match="dimensions"):
        tool.exact_frame(fixture.source_video, Fraction(1, 24), (50, 64, 3))


def test_symlink_artifact_and_output_rejected(fixture, tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        tool.new_output(alias / "new", [fixture.run])
    with pytest.raises(ValueError, match="inside"):
        tool.new_output(fixture.run / "new", [fixture.run])
    cache = next((fixture.run / "data/sessions/SYNTHETICDOUBLES/perception").glob("*.msgpack"))
    real = tmp_path / "saved.msgpack"
    cache.rename(real)
    cache.symlink_to(real)
    with pytest.raises(ValueError, match="non-symlink"):
        tool.verify_run(fixture.run, fixture.source_video, fixture.pipeline_root)


def test_failed_decode_retains_originals_and_partial_evidence(fixture, monkeypatch):
    digest = tool.sha(fixture.source_video)

    def fail(*args):
        raise ValueError("intentional decoder failure")

    monkeypatch.setattr(tool, "exact_frame", fail)
    with pytest.raises(ValueError, match="intentional"):
        tool.main(fixture)
    assert tool.sha(fixture.source_video) == digest
    assert tool.read(fixture.output / "failure.json")["status"] == "failed_evidence_preserved"
    assert (fixture.output / "executed_tool.py.source").exists()
    assert not (fixture.output / "completion.json").exists()


@pytest.mark.parametrize("indent", [None, 0, 4])
def test_model_pins_use_producer_value_hash_with_separate_byte_binding(fixture, indent):
    arm = tool.verify_run(fixture.run, fixture.source_video, fixture.pipeline_root)
    path = fixture.run / "models/cache/lock.json"
    pins = tool.read(path)
    path.write_text(json.dumps(pins, indent=indent) + "\n")
    metadata = tool.verify_model_metadata(arm)
    pin = next(x for x in metadata if x["label"] == "model_pins")
    assert pin["verified_value_sha256"] == arm["info"]["models"]["pins_sha256"]
    assert pin["file_binding"]["sha256"] == tool.sha(path)
    assert pin["file_binding"]["sha256"] != pin["verified_value_sha256"]
    assert pin["original_source_file_binding"]["sha256"] == tool.sha(fixture.pipeline_root / "models/cache/lock.json")


@pytest.mark.parametrize(
    "corruption", ["staged_pins", "source_bytes", "manifest", "forged_value", "missing_source_pin"]
)
def test_model_metadata_still_rejects_changed_values_or_original_pin_bytes(fixture, corruption):
    arm = tool.verify_run(fixture.run, fixture.source_video, fixture.pipeline_root)
    staged = fixture.run / "models/cache/lock.json"
    source = fixture.pipeline_root / "models/cache/lock.json"
    if corruption in ("staged_pins", "forged_value"):
        changed = {"fixture_model": "b" * 64}
        staged.write_text(json.dumps(changed, indent=2) + "\n")
        if corruption == "forged_value":
            arm["info"]["models"]["pins_sha256"] = hashlib.sha256(
                json.dumps(changed, sort_keys=True, allow_nan=False).encode()
            ).hexdigest()
    elif corruption == "source_bytes":
        source.write_text(json.dumps(tool.read(source)) + "\n")
    elif corruption == "manifest":
        path = fixture.run / "models/manifest.yaml"
        path.write_text(path.read_text() + "# changed bytes\n")
    else:
        del arm["plan"]["input_files_sha256"][str(source)]
    with pytest.raises(ValueError, match=r"model metadata changed|source pin|Staged pins"):
        tool.verify_model_metadata(arm)


@pytest.mark.parametrize("codec", [22, 23])
def test_current_codec_renders_detached_context_without_turning_it_into_people(fixture, tmp_path, codec):
    run, pts, root = make_run(tmp_path, f"codec{codec}", fixture.source_video, codec=codec)
    fixture.run, fixture.source_pts, fixture.pipeline_root = run, pts, root
    tool.main(fixture)
    folder = fixture.output / "frame_0000001"
    raw = tool.read(folder / "current_raw_frame.json")
    evidence = tool.read(folder / "evidence.json")
    assert len(raw["p"]) == 4 and len(raw["fg"]) == 3
    context = evidence["arms"]["current"]["scene_foreground"]
    assert context["status"] == "explicit_scene_only_context"
    assert context["athlete_or_GT_authority"] is False
    assert context["regions"] == raw["fg"]
    assert not tool.read(fixture.output / "completion.json")["physical_gt_created"]


@pytest.mark.parametrize("codec", [20, 21])
def test_legacy_codec_context_remains_unknown(codec, fixture, tmp_path):
    run, pts, root = make_run(tmp_path, f"codec{codec}", fixture.source_video, codec=codec)
    fixture.run, fixture.source_pts, fixture.pipeline_root = run, pts, root
    tool.main(fixture)
    evidence = tool.read(fixture.output / "frame_0000001/evidence.json")
    assert evidence["arms"]["current"]["scene_foreground"] == {
        "status": "unknown_legacy_codec",
        "regions": None,
        "athlete_or_GT_authority": False,
    }


@pytest.mark.parametrize(
    "case", ["missing", "duplicate", "extra", "wrong_frame", "bool_coordinate", "freshness", "overflow"]
)
def test_codec22_foreground_metadata_is_typed_bounded_and_frame_bound(case):
    frame = {
        "f": 7,
        "fg": [
            {
                "frame": 7,
                "key": "image-only",
                "bbox": [1.0, 2.0, 3.0, 4.0],
                "detector_matched": True,
                "detector_observed": True,
            }
        ],
    }
    if case == "missing":
        del frame["fg"]
    elif case == "duplicate":
        frame["fg"] *= 2
    elif case == "extra":
        frame["fg"][0]["athlete"] = "invented"
    elif case == "wrong_frame":
        frame["fg"][0]["frame"] = 6
    elif case == "bool_coordinate":
        frame["fg"][0]["bbox"][0] = True
    elif case == "freshness":
        frame["fg"][0]["detector_observed"] = 1
    else:
        frame["fg"] = [{**frame["fg"][0], "key": str(i)} for i in range(9)]
    with pytest.raises(ValueError, match="foreground"):
        tool.scene_foreground(frame, 22)


def test_legacy_extra_context_field_does_not_acquire_new_schema_authority():
    assert tool.scene_foreground({"f": 7, "fg": "not a codec22 declaration"}, 21) is None


def test_context_overlay_preserves_raw_v3_witness_and_layout_metadata():
    import copy

    frame = {
        "f": 7,
        "p": [],
        "cc": {"supporting_region_keys": ["image:a", "image:b"], "witness_parameters": [4.0, 19.0]},
        "cd": {"layout_indices": [0, 1, 2], "matched_pairs": [[1, 2], [2, 0]]},
        "fg": [
            {
                "frame": 7,
                "key": "scene-only",
                "bbox": [10.0, 20.0, 40.0, 80.0],
                "detector_matched": None,
                "detector_observed": False,
            }
        ],
    }
    before = copy.deepcopy(frame)
    output = tool.render(
        np.zeros((120, 320, 3), dtype=np.uint8), frame, "synthetic context", foreground=tool.scene_foreground(frame, 22)
    )
    assert frame == before
    assert output[80, 40].tolist() == [255, 180, 0]
    assert frame["p"] == []  # Context never becomes an athlete population.


@pytest.mark.parametrize("codec", [22, 23])
def test_current_codec_checks_foreground_on_unselected_frames_too(fixture, tmp_path, codec):
    run, _, root = make_run(tmp_path, f"codec{codec}_corrupt", fixture.source_video, codec=codec)
    cache = next((run / "data/sessions/SYNTHETICDOUBLES/perception").glob("*.msgpack"))
    chunk = msgpack.unpackb(cache.read_bytes(), raw=False)
    chunk["frames"][2]["fg"][0]["frame"] = 1
    cache.write_bytes(msgpack.packb(chunk))
    catalog_path = run / "perception_completion_catalog.json"
    catalog = tool.read(catalog_path)
    row = catalog["files"][0]
    row["sha256"], row["bytes"] = tool.sha(cache), cache.stat().st_size
    catalog["total_bytes"] = row["bytes"]
    write(catalog_path, catalog)
    info = tool.read(run / "inference.json")
    info["perception_cache_catalog"]["sha256"] = tool.sha(catalog_path)
    write(run / "inference.json", info)
    parent_path = run.with_suffix(".executor.json")
    parent = tool.read(parent_path)
    parent["worker_report_sha256"] = tool.sha(run / "inference.json")
    parent["perception_cache_catalog_verification"]["catalog_sha256"] = tool.sha(catalog_path)
    write(parent_path, parent)
    with pytest.raises(ValueError, match="foreground"):
        tool.verify_run(run, fixture.source_video, root)
