"""GT-free audit controls; fixtures are structural examples, not contact labels."""

import hashlib
import json
from collections import Counter
from copy import deepcopy

import pytest

from research.production_contact_result_audit import (
    Issues,
    audit_run,
    cache_frames,
    completed_run,
    evidence_issues,
    fold_events,
    resolve_current,
)


def event(identity, *, supersedes=None, status="confirmed", actor="arbitrary-person"):
    return {"event_id": identity, "supersedes": supersedes, "status": status, "actors": {"player_id": actor}}


def test_fold_resolves_correction_retraction_even_when_frame_export_orders_child_first():
    rows = [
        event("new", supersedes="old"),
        event("old"),
        event("removed"),
        event("withdrawal", supersedes="removed", status="retracted"),
    ]
    by_id, current, successors = fold_events(rows)
    assert [r["event_id"] for r in current] == ["new"]
    assert resolve_current("old", by_id, successors)["event_id"] == "new"
    assert resolve_current("removed", by_id, successors) is None


def test_fold_retains_all_four_arbitrary_actor_identifiers():
    actors = ["visitor-A", "visitor-B", "home-C", "home-D"]
    _, current, _ = fold_events([event(str(i), actor=actor) for i, actor in enumerate(actors)])
    assert [r["actors"]["player_id"] for r in current] == actors


@pytest.mark.parametrize(
    "rows",
    [
        [event("a"), event("a")],
        [event("a", supersedes="b"), event("b", supersedes="a")],
        [event("a", supersedes="missing")],
    ],
)
def test_malformed_lineage_cannot_produce_an_apparently_clean_event_count(rows):
    with pytest.raises(ValueError):
        fold_events(rows)


def test_branching_parent_is_not_silently_resolved_to_one_child():
    by_id, _, successors = fold_events([event("a"), event("b", supersedes="a"), event("c", supersedes="a")])
    assert resolve_current("a", by_id, successors) is None


def test_unfinished_run_is_refused_before_cache_reads_or_output_creation(tmp_path):
    run, output = tmp_path / "run", tmp_path / "output"
    run.mkdir()
    (run / "benchmark_metadata.json").write_text(json.dumps({"status": "running"}))
    with pytest.raises(ValueError, match="unfinished"):
        audit_run(run, output)
    assert not output.exists()


def test_completed_flag_requires_matching_full_frontier_and_prediction_hash(tmp_path):
    inference = {"status": "analysed", "frontier_frame": 7, "media": {"n_frames": 8}}
    prediction = b"Start_Frame,End_Frame,Start_Time_sec,End_Time_sec,Duration_sec,Start_Time,End_Time\n"
    metadata = {
        "status": "completed",
        "frame_count": 8,
        "inference": inference,
        "prediction_sha256": hashlib.sha256(prediction).hexdigest(),
    }
    (tmp_path / "benchmark_metadata.json").write_text(json.dumps(metadata))
    (tmp_path / "inference.json").write_text(json.dumps(inference))
    (tmp_path / "predicted_rallies.csv").write_bytes(prediction)
    assert completed_run(tmp_path)[1] == inference
    metadata["frame_count"] = 9
    (tmp_path / "benchmark_metadata.json").write_text(json.dumps(metadata))
    with pytest.raises(ValueError, match="frontier"):
        completed_run(tmp_path)


def fixture_evidence():
    event_row = {"event_id": "contact", "frame_start": 4}
    evidence = {
        "inputs": {
            "frame": 4,
            "context_start": 0,
            "context_stop": 8,
            "available_through": 7,
            "motion": {"before_frames": [2, 3, 4], "after_frames": [4, 5, 6, 7]},
            "player_observation_frames": [4],
            "pose_observation_frames": [6],
            "racket_observation_frames": [6],
        },
        "impact": {"reliability": "probable"},
    }
    frames = {
        frame: {
            "people": {17: {"pf": frame, "rf": frame, "valid_wrists": True, "dm": True, "racket": True}},
            "pose_stride": 2,
            "detector_observed": True,
        }
        for frame in (4, 6)
    }
    return event_row, evidence, frames


def test_declared_post_contact_lookahead_with_exact_source_is_allowed():
    row, evidence, frames = fixture_evidence()
    issues, counts = Issues(), Counter()
    evidence_issues(row, evidence, 7, frames, 17, issues, counts)
    assert not issues.counts
    assert counts["pose_cue_identity_checked"] == counts["racket_cue_identity_checked"] == 1


def test_stale_pose_and_future_racket_are_distinct_from_valid_lookahead():
    row, evidence, frames = fixture_evidence()
    frames[6]["people"][17].update(pf=5, rf=7)
    issues = Issues()
    evidence_issues(row, evidence, 7, frames, 17, issues, Counter())
    assert issues.counts == {"pose_cue_without_exact_fresh_source": 1, "racket_cue_without_exact_fresh_source": 1}


def test_unknown_target_is_explicitly_unverifiable_not_borrowed_from_another_person():
    row, evidence, frames = fixture_evidence()
    issues, counts = Issues(), Counter()
    evidence_issues(row, evidence, 7, frames, None, issues, counts)
    assert not issues.counts
    assert counts["pose_cue_identity_unverifiable"] == 1
    assert not counts["pose_cue_identity_checked"]


def test_confirmation_requires_matching_frame_and_media_review():
    row, evidence, frames = fixture_evidence()
    evidence["impact"]["reliability"] = "confirmed"
    evidence["inputs"]["review"] = {"frame": 4, "physical_impact": True, "source_sha256": "a" * 64}
    issues = Issues()
    evidence_issues(row, evidence, 7, frames, 17, issues, Counter(), "b" * 64)
    assert issues.counts["physical_confirmation_without_matching_external_review"] == 1


def test_player_cue_needs_actual_detector_execution_as_well_as_match_flag():
    row, evidence, frames = fixture_evidence()
    frames[4]["detector_observed"] = False
    issues = Issues()
    evidence_issues(row, evidence, 7, frames, 17, issues, Counter())
    assert issues.counts["player_cue_without_detector_match"] == 1


@pytest.mark.parametrize("field", ["pose_observation_frames", "racket_observation_frames", "player_observation_frames"])
def test_cue_outside_available_context_is_reported(field):
    row, evidence, frames = fixture_evidence()
    evidence["inputs"][field] = [8]
    issues = Issues()
    evidence_issues(row, evidence, 7, frames, 17, issues, Counter())
    assert issues.counts["cue_sample_frontier_violation"] == 1


def test_legacy_cache_cannot_gain_pose_identity_from_a_new_field_without_its_schema(tmp_path):
    import msgpack

    path = tmp_path / "runtime/sessions/arbitrary-session/perception"
    path.mkdir(parents=True)
    row = {
        "f": 0,
        "s": None,
        "c": 0.0,
        "ps": 1,
        "p": [{"t": 17, "pf": 0, "rf": 0, "k": [[0, 0, 0]] * 17, "rk": None, "dm": True}],
    }
    (path / "seg.msgpack").write_bytes(msgpack.packb({"v": 18, "frames": [row]}))
    frames, _, counts = cache_frames(tmp_path, "arbitrary-session", 0, Issues())
    assert frames[0]["people"][17]["pf"] is None
    assert counts["pose_source_unknown"] == 1
    row2 = deepcopy(row)
    row2["f"] = 1
    (path / "seg2.msgpack").write_bytes(msgpack.packb({"v": 18, "frames": [row2]}))
    with pytest.raises(ValueError, match="indices"):
        cache_frames(tmp_path, "arbitrary-session", 0, Issues())
