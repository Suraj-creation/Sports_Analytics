"""Cross-packet structural rules after a decoder; raw pixel decoding is tested separately."""

from copy import deepcopy
from types import SimpleNamespace

import pytest

from bai_badminton.perception.scene_change import ForegroundRegion
from research import scene_epoch_audit_v3 as audit
from research.tests.test_scene_epoch_audit_v3 import frame, packet, typed_stub, weak_pair


def source_pair():
    regions = [
        dict(frame=0, key="a", bbox=[0, 0, 20, 20], detector_matched=True, detector_observed=True),
        dict(frame=0, key="b", bbox=[10, 10, 30, 30], detector_matched=True, detector_observed=True),
    ]
    first, second = frame(0), frame(1)
    first["fg"], first["cc"] = regions, None
    second["fg"] = []
    second["cc"] = {
        "version": "foreground-scene-hypothesis:v5",
        "hypothesis": False,
        "status": "measured",
        "previous_frame": 0,
        "regions": deepcopy(regions),
    }
    packets = [packet([first]), packet([second])]
    for value in packets:
        value["v"] = 24
    return packets


def decoded_stub(value):
    """Only the already-decoded interface; deliberately not a pixel/native validation fixture."""
    rows = []
    for f in value["frames"]:
        raw = f.get("cc")
        rows.append(
            SimpleNamespace(
                frame_idx=f["f"],
                foreground_regions=tuple(ForegroundRegion(**r) for r in f.get("fg", [])),
                content_change=SimpleNamespace(
                    hypothesis=raw["hypothesis"],
                    regions=tuple(SimpleNamespace(region=ForegroundRegion(**r)) for r in raw.get("regions", [])),
                )
                if raw
                else None,
                content_decision=SimpleNamespace(**f["cd"]) if f.get("cd") else None,
            )
        )
    return SimpleNamespace(frames=rows)


def test_full_timeline_binds_origins_across_cache_boundary():
    packets = source_pair()
    frames = [f for p in packets for f in p["frames"]]
    proof = audit.validate_scene_epoch_proofs(frames, packets, decode_packet=decoded_stub)
    assert proof["native_decoded_frames"] == 2


@pytest.mark.parametrize("change", ["omit", "relabel", "box", "order"])
def test_cross_packet_source_origin_binding_cannot_be_replaced_by_self_consistency(change):
    packets = source_pair()
    rows = packets[1]["frames"][0]["cc"]["regions"]
    if change == "omit":
        rows.pop()
    elif change == "relabel":
        rows[0]["key"] = "new-key"
    elif change == "box":
        rows[0]["bbox"][0] = 1
    else:
        rows.reverse()
    frames = [f for p in packets for f in p["frames"]]
    with pytest.raises(ValueError, match="actual previous-frame foreground"):
        audit.validate_scene_epoch_proofs(frames, packets, decode_packet=decoded_stub)


def test_v5_v4_weak_reset_is_version_paired_and_camera_bound():
    packets = weak_pair()
    for p in packets:
        p["v"] = 24
    row = packets[1]["frames"][0]
    row["cc"]["version"] = "foreground-scene-hypothesis:v5"
    row["cc"]["regions"] = []
    row["cd"]["version"] = "detector-layout-scene-decision:v4"
    frames = [f for p in packets for f in p["frames"]]
    report, _, proof = audit.audit_frames(frames, 2, packets=packets, decode_packet=decoded_stub)
    assert proof["weak_barrier_frames"] == [1]
    assert report["counts"]["scene_raw_hypotheses"] == 0
    bad = deepcopy(packets)
    bad[1]["frames"][0]["cd"]["version"] = "detector-layout-scene-decision:v3"
    with pytest.raises(ValueError, match="version-paired"):
        audit.audit_frames([f for p in bad for f in p["frames"]], 2, packets=bad, decode_packet=decoded_stub)


@pytest.mark.parametrize("epoch", [0, 1])
def test_overlap_dependent_unknown_is_an_abstention_never_an_epoch_reset(epoch):
    first, second = frame(0), frame(1, epoch=epoch, raw=True)
    second["cd"] = {
        "version": "detector-layout-scene-decision:v4",
        "decision": "unknown",
        "reason": "partial_layout",
        "raw_hypothesis": True,
        "feature_origin_overlap_dependent": True,
    }
    value = packet([first, second])
    value["v"] = 24
    if epoch:
        with pytest.raises(ValueError, match="Uncorroborated overlap-dependent"):
            audit.audit_frames([first, second], 2, packets=[value], decode_packet=typed_stub)
    else:
        report, _, proof = audit.audit_frames([first, second], 2, packets=[value], decode_packet=typed_stub)
        assert proof["overlap_dependent_abstentions"] == [1]
        assert report["counts"]["scene_raw_hypotheses"] == 1
        assert report["counts"]["actual_content_epoch_increments"] == 0
