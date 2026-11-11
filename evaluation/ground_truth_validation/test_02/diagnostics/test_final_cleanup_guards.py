"""Deletion checks use tiny temporary fixtures, never real videos or datasets."""

from __future__ import annotations

import copy
import hashlib
import json
import sys

import pytest

from evaluation.ground_truth_validation.orchestration import verify_and_cleanup_test02 as cleanup


@pytest.fixture
def owned(tmp_path, monkeypatch):
    test = tmp_path / "test_02"
    (test / "inputs").mkdir(parents=True)
    video = test / "inputs/Test2_Full_Rev.mp4"
    payload = b"small owned video fixture"
    video.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    monkeypatch.setattr(cleanup, "TEST", test)
    monkeypatch.setattr(cleanup, "VIDEO", video)
    monkeypatch.setattr(cleanup, "SOURCE_BYTES", len(payload))
    monkeypatch.setattr(cleanup, "SOURCE_SHA", digest)
    download = {"name": video.name, "file_id": cleanup.DRIVE_FILE_ID, "verified_bytes": len(payload), "sha256": digest}
    return test, video, download


def test_exact_owned_download_identity_is_verified(owned):
    _, video, download = owned
    identity = cleanup.validate_video(video, download)
    assert identity["sha256"] == download["sha256"]
    assert identity["bytes"] == len(video.read_bytes())


def test_another_video_is_never_eligible_even_with_identical_bytes(owned):
    test, video, download = owned
    other = test / "inputs/Test1_Full_Rev.mp4"
    other.write_bytes(video.read_bytes())
    with pytest.raises(ValueError, match="exact regular"):
        cleanup.validate_video(other, download)
    assert other.exists() and video.exists()


def test_symlink_video_target_refused(owned):
    test, video, download = owned
    original = test / "original.mp4"
    video.rename(original)
    video.symlink_to(original)
    with pytest.raises(ValueError, match="no links"):
        cleanup.validate_video(video, download)
    assert original.exists()


def test_symlink_parent_path_escape_refused(owned):
    test, video, download = owned
    actual = test / "elsewhere"
    (test / "inputs").rename(actual)
    (test / "inputs").symlink_to(actual, target_is_directory=True)
    with pytest.raises(ValueError, match="path escapes"):
        cleanup.validate_video(video, download)
    assert (actual / video.name).exists()


@pytest.mark.parametrize(
    ("key", "value"), [("file_id", "different-drive-file"), ("verified_bytes", 9999), ("sha256", "foreign-hash")]
)
def test_original_drive_pairing_cannot_be_substituted(owned, key, value):
    _, video, download = owned
    download[key] = value
    with pytest.raises(ValueError, match="Drive download"):
        cleanup.validate_video(video, download)
    assert video.exists()


def deletion_fixture(owned):
    test, video, download = owned
    annotation = test / "keep_annotation.csv"
    annotation.write_text("original annotation")
    other = test / "inputs/keep_other_video.mp4"
    other.write_bytes(b"never remove other video")
    report = test.parent / "final_report.md"
    report.write_text("reviewed report")
    retention = test / "retention/new_verification"
    retention.mkdir(parents=True)
    manifest = cleanup.inventory(test, [video, retention])
    cleanup.dump(retention / "workspace_manifest.json", manifest)
    cleanup.dump(retention / "required_reports_manifest.json", {str(report): cleanup.sha(report)})
    identity = cleanup.validate_video(video, download)
    identity.update(all_final_gates_passed=True, download_receipt=download)
    return identity, [manifest], retention / "cleanup_receipt.json", annotation, other, report


def test_only_exact_download_is_unlinked_after_all_checks(owned):
    _, video, _ = owned
    identity, manifests, receipt, annotation, other, report = deletion_fixture(owned)
    value = cleanup.delete_exact_download(video, identity, manifests, receipt)
    assert not video.exists()
    assert annotation.read_text() == "original annotation"
    assert other.read_bytes() == b"never remove other video"
    assert report.exists()
    assert value["deleted_paths"] == [str(video)]
    assert json.loads(receipt.read_text())["status"] == "deleted_only_downloaded_test2_video"


def test_incomplete_final_gate_refuses_unlink(owned):
    _, video, _ = owned
    identity, manifests, receipt, *_ = deletion_fixture(owned)
    identity["all_final_gates_passed"] = False
    with pytest.raises(ValueError, match="completed final verification"):
        cleanup.delete_exact_download(video, identity, manifests, receipt)
    assert video.exists() and not receipt.exists()


def test_retained_artifact_mutation_blocks_deletion(owned):
    _, video, _ = owned
    identity, manifests, receipt, annotation, *_ = deletion_fixture(owned)
    annotation.write_text("unexpected change")
    with pytest.raises(ValueError, match="artifact population"):
        cleanup.delete_exact_download(video, identity, manifests, receipt)
    assert video.exists()


def test_report_mutation_blocks_deletion(owned):
    _, video, _ = owned
    identity, manifests, receipt, _, _, report = deletion_fixture(owned)
    report.write_text("unreviewed report")
    with pytest.raises(ValueError, match="report changed"):
        cleanup.delete_exact_download(video, identity, manifests, receipt)
    assert video.exists()


def test_existing_cleanup_receipt_is_never_overwritten(owned):
    _, video, _ = owned
    identity, manifests, receipt, *_ = deletion_fixture(owned)
    receipt.write_text("existing immutable cleanup receipt")
    with pytest.raises(ValueError, match="overwrite"):
        cleanup.delete_exact_download(video, identity, manifests, receipt)
    assert receipt.read_text() == "existing immutable cleanup receipt"
    assert video.exists()


def test_inventory_checks_new_files_and_records_alias_without_traversal(owned):
    test, video, _ = owned
    external = test.parent / "external"
    external.mkdir()
    (external / "data.json").write_text("{}")
    (test / "alias").symlink_to(external, target_is_directory=True)
    manifest = cleanup.inventory(test, [video])
    assert manifest["entries"]["alias"]["kind"] == "symlink"
    assert "alias/data.json" not in manifest["entries"]
    (test / "new_evidence.json").write_text("{}")
    with pytest.raises(ValueError, match="artifact population"):
        cleanup.verify_inventory(manifest)


def test_required_local_links_are_verified_without_fetching_external_urls(owned):
    test, video, _ = owned
    evidence = test / "evidence.json"
    evidence.write_text("{}")
    document = test / "report.md"
    document.write_text(
        "[Evidence](evidence.json) [Remote](https://invalid.example/no-fetch) "
        "[Original raw input](inputs/Test2_Full_Rev.mp4)"
    )
    result = cleanup.local_document_links([document])
    assert result["network_urls_checked"] is False
    assert len(result["verified_retained_links"]) == 1
    assert result["raw_input_references_intentionally_retired_after_cleanup"][0]["target"] == str(video)
    evidence.unlink()
    with pytest.raises(ValueError, match="link missing"):
        cleanup.local_document_links([document])


def test_review_requires_concrete_final_hashes_and_complete_disposition(owned):
    test, _, download = owned
    report = test / "reviewed.md"
    report.write_text("reviewed")
    review = {
        "schema": "test2-final-evaluation-review:v1",
        "test": 2,
        "source_sha256": download["sha256"],
        "final_disposition": "complete_with_documented_limitations",
        "reviewer_type": "agent_orchestrator",
        "approved_cleanup": "delete_only_downloaded_test2_video",
        "diagnostic_review_completed": True,
        "fresh_metrics_reviewed": True,
        "test1_semantic_regression_reviewed": True,
        "all_annotation_families_accounted_for": True,
        "remaining_limitations_recorded": True,
        "reviewed_files_sha256": {str(report.resolve()): cleanup.sha(report)},
    }
    cleanup.validate_review(review, [report])
    bad = copy.deepcopy(review)
    bad["fresh_metrics_reviewed"] = False
    with pytest.raises(ValueError, match="review is incomplete"):
        cleanup.validate_review(bad, [report])
    report.write_text("changed after review")
    with pytest.raises(ValueError, match="bind exact final"):
        cleanup.validate_review(review, [report])


@pytest.mark.parametrize("explicit_delete", [False, True])
def test_incomplete_run_never_reaches_deletion_even_with_flag(owned, monkeypatch, explicit_delete):
    test, video, download = owned
    (test / "inputs/download_verification.json").write_text(json.dumps(download))
    review = test / "review.json"
    review.write_text("{}")
    args = ["verify_and_cleanup_test02.py", "--review-receipt", str(review)]
    if explicit_delete:
        args.append("--delete-downloaded-video")
    monkeypatch.setattr(sys, "argv", args)

    def unfinished(*args, **kwargs):
        raise ValueError("fresh improved worker incomplete")

    monkeypatch.setattr(cleanup, "load_bundle", unfinished)
    monkeypatch.setattr(
        cleanup, "delete_exact_download", lambda *a, **k: pytest.fail("Deletion reached incomplete run")
    )
    with pytest.raises(ValueError, match="worker incomplete"):
        cleanup.main()
    assert video.exists()
