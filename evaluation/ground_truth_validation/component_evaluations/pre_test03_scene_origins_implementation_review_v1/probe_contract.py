"""Independent synthetic contract probe; no neural or media inference.

Flow returns are controlled to isolate feature-origin and cache-binding logic.
They are not measurements of a real athlete or video.
"""
import argparse
import hashlib
import json
import sys
from copy import deepcopy
from dataclasses import asdict, replace
from pathlib import Path
from types import SimpleNamespace


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--pipeline-root", type=Path, required=True)
    args.add_argument("--output", type=Path, required=True)
    cfg = args.parse_args()
    root = cfg.pipeline_root.resolve()
    cfg.output.mkdir(exist_ok=False)
    sys.path[:0] = [str(root / p) for p in ["sports/badminton/src", "engine/src", "sports/badminton/tests"]]
    import msgpack
    import numpy as np
    import pytest
    from test_perception_diagnostic_provenance import _non30_cache_session

    from bai_badminton.perception import content, scene_change as scene
    from bai_badminton.perception.calibration_state import CalibrationState
    from bai_badminton.perception.players import PlayerDetectionProbe, strict_court_indices
    from bai_badminton.perception_types import ChunkPerception, FramePerception
    from bai_badminton.plugin import BadmintonSession, StaleCacheError

    source_paths = ["sports/badminton/src/bai_badminton/perception/scene_change.py",
                    "sports/badminton/src/bai_badminton/perception/content.py",
                    "sports/badminton/src/bai_badminton/perception/components.py",
                    "sports/badminton/src/bai_badminton/plugin.py"]
    snapshots = {}
    for relative in source_paths:
        data = (root / relative).read_bytes()
        dest = cfg.output / "source_snapshot" / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        snapshots[relative] = hashlib.sha256(data).hexdigest()
    assert Path(scene.__file__).resolve().is_relative_to(root)
    assert Path(content.__file__).resolve().is_relative_to(root)

    boxes = ((200., 100., 500., 500.), (400., 200., 700., 550.), (800., 100., 1000., 500.))
    state = {"frame": 0, "call": 0}

    def flow(_p, _q, mask):
        index = state["call"] % 4
        state["call"] += 1
        if not mask.any():
            return 0, None, None, None
        if index == 0:
            return 40, 1., 0., 0.
        changed = state["frame"] == 3 and index != 3
        return min(20, int(np.count_nonzero(mask))), 0. if changed else 1., 40. if changed else 1., 10. if changed else 0.

    mp = pytest.MonkeyPatch()
    mp.setattr(scene, "_flow", flow)
    observer = scene.SceneContinuityDetectorV5()
    image = np.random.default_rng(919).integers(0, 256, (720, 1280, 3), dtype=np.uint8)
    for f in range(4):
        state.update(frame=f, call=0)
        previous = tuple(scene.ForegroundRegion(f - 1, f"region:{i}", box, True, True)
                         for i, box in enumerate(boxes)) if f else ()
        raw = observer.observe(f, image, previous_regions=previous, previous_view_valid=f > 0, current_view_valid=True)
    mp.undo()
    raw = content.scene_change_from_dict(content.scene_change_to_dict(raw))
    provider = content.ContentContinuityProviderV2(mode="barrier_detector_layout_v2")
    polygon = ((0., 0.), (1280., 0.), (1280., 720.), (0., 720.))
    current_boxes = ((200., 100., 700., 550.), boxes[2])
    probe = PlayerDetectionProbe(3, (720, 1280, 3), "a" * 64, current_boxes, (.9, .9),
                                 (0, 0, 1280, 720), (0, 1), polygon,
                                 strict_court_indices(current_boxes, polygon))
    decision = provider.layout_decision(raw, probe, detector_model="controlled-detector@1",
                                        geometry_valid=True, expected_participants=2)
    content.validate_scene_decision_binding(decision, raw)
    overlap = {"raw": asdict(raw), "decision": asdict(decision),
               "tracking_barrier": provider.tracking_barrier_for_decision(decision),
               "interpretation": "One moving actor represented by two partial overlapping fragments, plus one static actor; controlled flow, not physical GT."}
    identity = tuple(float(v) for v in np.eye(3).ravel())
    variants = {}
    for name, variant_boxes, expected, valid, camera in [
        ("partial_duplicate_complete_ambiguous", current_boxes, 2, True, identity),
        ("partial_duplicate_one_actor_displaced_other_static", ((20., 100., 180., 550.), boxes[2]), 2, True, identity),
        ("unknown_format", current_boxes, None, True, identity),
        ("missing_camera", current_boxes, 2, True, None),
        ("invalid_geometry", current_boxes, 2, False, identity),
        ("doubles_incomplete", current_boxes, 4, True, identity),
    ]:
        variant = PlayerDetectionProbe(3, (720, 1280, 3), "a" * 64, variant_boxes, (.9,) * len(variant_boxes),
                                       (0, 0, 1280, 720), tuple(range(len(variant_boxes))), polygon,
                                       strict_court_indices(variant_boxes, polygon))
        actual = provider.layout_decision(raw, variant, detector_model="controlled-detector@1", geometry_valid=valid,
                                          expected_participants=expected, previous_to_current=camera,
                                          previous_camera=camera)
        content.validate_scene_decision_binding(actual, raw)
        variants[name] = {"decision": asdict(actual), "tracking_barrier": provider.tracking_barrier_for_decision(actual)}

    def frame(f, *, fg=(), cc=None, cd=None):
        return FramePerception(f, None, 0., cam=np.eye(3), view="main", calibration_state=CalibrationState.VALID,
                               detector_observed=False, pose_stride=0, foreground_regions=fg,
                               content_change=cc, content_decision=cd)

    fixture = cfg.output / "fixture"
    fixture.mkdir()
    session = _non30_cache_session(fixture)

    def record(evidence):
        cd = provider.layout_decision(evidence, None, detector_model=None, geometry_valid=True, expected_participants=2)
        rows = [frame(2, fg=previous), frame(3, cc=evidence, cd=cd)]
        value = msgpack.unpackb(session.encode_perception(ChunkPerception(2, 3, rows, models={})), raw=False)
        value["ci"]["profile"]["components"]["content_continuity"] = {
            "implementation": "foreground-content-continuity-v2",
            "params": {"mode": "barrier_detector_layout_v2", "analysis_width": 480}}
        return value

    def decode(value):
        receiver = SimpleNamespace(perception=SimpleNamespace(ref_id=value["cr"]),
                                   _isolation_id=lambda: deepcopy(value["ci"]))
        try:
            result = BadmintonSession.decode_perception(receiver, msgpack.packb(value, use_bin_type=True), diagnostic=True)
            return {"accepted": True, "frames": len(result.frames)}
        except StaleCacheError as error:
            return {"accepted": False, "error": str(error), "cause": str(error.__cause__)}

    results = {"actual_positive": decode(record(raw))}
    for damage in ["omit_static", "relabel_static", "shift_static", "reorder_static"]:
        regions = list(raw.regions)
        if damage == "omit_static":
            regions.pop()
        elif damage == "relabel_static":
            regions[-1] = replace(regions[-1], region=replace(regions[-1].region, key="invented-static"))
        elif damage == "shift_static":
            box = regions[-1].region.bbox
            regions[-1] = replace(regions[-1], region=replace(regions[-1].region, bbox=tuple(v + 20 for v in box)))
        else:
            regions = [regions[2], regions[0], regions[1]]
        _, masks = scene.exclusive_feature_origin_masks([r.region for r in regions], raw.source_frame_size,
                                                        raw.analysis_frame_size)
        altered = replace(raw, regions=tuple(regions), origin_masks=masks)
        # Read-only static-region changes preserve current channel/supporting values;
        # adjust cohort order to match deterministic raw sequence when reordered.
        for key in ["supporting_region_keys", "acquisition_region_keys", "relative_region_keys"]:
            original = getattr(altered, key)
            altered = replace(altered, **{key: tuple(r.region.key for r in regions if r.region.key in original)})
        try:
            altered = content.scene_change_from_dict(content.scene_change_to_dict(altered))
            value = record(altered)
            results[damage] = {"raw_self_consistent": True, **decode(value)}
            (cfg.output / f"{damage}.msgpack").write_bytes(msgpack.packb(value, use_bin_type=True))
        except ValueError as error:
            results[damage] = {"raw_self_consistent": False, "error": str(error)}
    session.close()
    unchanged = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
                 for name, digest in snapshots.items()}
    report = {"pipeline_root": str(root), "source_sha256": snapshots, "source_unchanged_during_probe": unchanged,
              "native_imports": {"scene": scene.__file__, "content": content.__file__},
              "partial_actor_fragments": overlap, "layout_variants": variants, "same_packet_source_binding": results,
              "new_neural_inference": False, "physical_ground_truth": None}
    (cfg.output / "result.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"partial_overlap": {"raw_hypothesis": raw.hypothesis, "layout": decision.decision,
                                         "tracking_barrier": overlap["tracking_barrier"]},
                      "bindings": results, "source_unchanged": unchanged}))


if __name__ == "__main__":
    main()
