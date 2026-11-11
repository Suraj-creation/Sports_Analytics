"""Verify final Test2 evidence; optionally unlink only its exact owned download.

Default is verification only. No recursive deletion, pipeline changes, network
requests or automatic Test3. Invoke only after final root diagnostic review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from evaluation.ground_truth_validation.orchestration.build_test02_consolidated_report import (  # noqa: E402
    Inputs,
    load_bundle,
)
from research.pipeline_repair_run_analysis import audit_frames, load_analysis_input, load_chunks  # noqa: E402

TEST = ROOT / "evaluation/ground_truth_validation/test_02"
EXTERNAL = ROOT.parent / "ground-truth-validation-artifacts-20261110/test_02"
VIDEO = TEST / "inputs/Test2_Full_Rev.mp4"
SOURCE_SHA = "4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a"
SOURCE_BYTES = 2453914397
DRIVE_FILE_ID = "17EeE7JmLC4zQNWzeTjr7cZk_DFYdh3Bs"
N = 29296
REPORT = ROOT / "evaluation/ground_truth_validation/reports/test_02_consolidated_v1.md"
DATASET_MANIFEST = ROOT / "evaluation/ground_truth_validation/dataset_inventory/dataset_manifest.json"
REGENERABLE = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def validate_video(path, download):
    """Never normalize an arbitrary input into an authorized deletion target."""
    path = Path(path)
    if (
        ".." in path.parts
        or path.absolute() != VIDEO.absolute()
        or path.name != "Test2_Full_Rev.mp4"
        or path.is_symlink()
        or not path.is_file()
        or path.resolve() != path.absolute()
    ):
        raise ValueError("Only the exact regular downloaded Test2 path is eligible; no links/path escapes")
    for parent in (TEST, TEST / "inputs"):
        if parent.is_symlink() or not parent.is_dir():
            raise ValueError("Downloaded input directory must be regular and inside the expected test workspace")
    if (
        download.get("file_id") != DRIVE_FILE_ID
        or download.get("name") != path.name
        or download.get("sha256") != SOURCE_SHA
        or download.get("verified_bytes") != SOURCE_BYTES
    ):
        raise ValueError("Original Drive download identity/size/hash receipt differs")
    info = path.stat()
    if info.st_size != SOURCE_BYTES or info.st_nlink != 1 or sha(path) != SOURCE_SHA:
        raise ValueError("Downloaded video bytes/hash or exclusive local file identity differs")
    return {
        "device": info.st_dev,
        "inode": info.st_ino,
        "bytes": info.st_size,
        "mtime_ns": info.st_mtime_ns,
        "sha256": SOURCE_SHA,
        "path": str(path.absolute()),
    }


def validate_review(review, required):
    if (
        review.get("schema") != "test2-final-evaluation-review:v1"
        or review.get("test") != 2
        or review.get("source_sha256") != SOURCE_SHA
        or review.get("final_disposition") != "complete_with_documented_limitations"
        or review.get("reviewer_type") != "agent_orchestrator"
        or review.get("approved_cleanup") != "delete_only_downloaded_test2_video"
    ):
        raise ValueError("Source-bound final Test2 review disposition required")
    for key in (
        "diagnostic_review_completed",
        "fresh_metrics_reviewed",
        "test1_semantic_regression_reviewed",
        "all_annotation_families_accounted_for",
        "remaining_limitations_recorded",
    ):
        if review.get(key) is not True:
            raise ValueError("Final review is incomplete: " + key)
    hashes = review.get("reviewed_files_sha256", {})
    if not hashes or any(hashes.get(str(path.resolve())) != sha(path) for path in required):
        raise ValueError("Review must bind exact final Markdown/JSON and fresh before/after comparison hashes")
    for path, digest in hashes.items():
        if not Path(path).is_file() or sha(path) != digest:
            raise ValueError("Reviewed final artifact changed")


def verify_hash_map(root, mapping):
    for relative, digest in mapping.items():
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Artifact catalogue must contain safe relative paths")
        path = root / path
        if not path.is_file() or sha(path) != digest:
            raise ValueError("Final retained artifact hash mismatch: " + str(path))


def verify_annotations():
    before = read(EXTERNAL / "baseline_v1/annotation_hashes_before.json")
    folder = ROOT / "Part2/dataset/Test2_Full"
    actual = {str(p): sha(p) for p in sorted(folder.iterdir()) if p.is_file()}
    if len(actual) != 7 or actual != before:
        raise ValueError("All seven original Test2 annotations must remain byte-identical")
    result = {"test2_files_verified": 7, "test2_sha256": actual, "historical_dataset_manifest": None}
    if DATASET_MANIFEST.exists():
        original = read(DATASET_MANIFEST)
        files = original.get("files", [])
        if len(files) != 62:
            raise ValueError("Expected complete historical 62-file Part2 preservation manifest")
        for row in files:
            path = Path(row["path"])
            if not path.is_file() or path.stat().st_size != row["bytes"] or sha(path) != row["sha256"]:
                raise ValueError("Original Part2 dataset/supporting file changed: " + str(path))
        result["historical_dataset_manifest"] = {
            "path": str(DATASET_MANIFEST),
            "sha256": sha(DATASET_MANIFEST),
            "verified_files": len(files),
        }
    return result


def inventory(root, exclusions):
    root = root.resolve(strict=True)
    excluded = [Path(p).absolute() for p in exclusions]
    entries = {}

    def omitted(path):
        return any(path.absolute() == p or p in path.absolute().parents for p in excluded)

    for folder, directories, files in os.walk(root, followlinks=False):
        base = Path(folder)
        for name in list(directories):
            path = base / name
            if name in REGENERABLE or omitted(path):
                directories.remove(name)
            elif path.is_symlink():
                directories.remove(name)
                files.append(name)
        for name in sorted(files):
            path = base / name
            if omitted(path) or path.suffix == ".pyc":
                continue
            relative = str(path.relative_to(root))
            if path.is_symlink():
                if not path.exists() or path.resolve() == VIDEO.resolve():
                    raise ValueError("Retained symlink is broken or depends on the retired raw download")
                entries[relative] = {
                    "kind": "symlink",
                    "target": str(path.readlink()),
                    "resolved_target": str(path.resolve()),
                }
            elif path.is_file():
                entries[relative] = {"kind": "file", "bytes": path.stat().st_size, "sha256": sha(path)}
            else:
                raise ValueError("Unexpected nonregular retained artifact: " + str(path))
    return {
        "root": str(root),
        "exclusions": [str(p) for p in excluded],
        "regenerable_directory_exclusions": sorted(REGENERABLE),
        "entries": entries,
        "file_count": sum(e["kind"] == "file" for e in entries.values()),
        "symlink_count": sum(e["kind"] == "symlink" for e in entries.values()),
        "file_bytes": sum(e.get("bytes", 0) for e in entries.values()),
    }


def verify_inventory(manifest):
    actual = inventory(Path(manifest["root"]), manifest["exclusions"])
    if actual != manifest:
        raise ValueError("Retained artifact population, file count or hashes changed during verification")


def local_document_links(documents):
    checked, retired = [], []
    for document in sorted(set(Path(p).resolve() for p in documents)):
        text = re.sub(r"```.*?```", "", document.read_text(), flags=re.S)
        for target in re.findall(r"\[[^\]]*\]\((<[^>]+>|[^)]+)\)", text):
            target = target.strip()
            target = target[1:-1] if target.startswith("<") and target.endswith(">") else target
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue  # External URL: intentionally no network check.
            target = unquote(target.split("#", 1)[0].split("?", 1)[0])
            target = re.sub(r":\d+$", "", target)
            path = Path(target)
            path = (path if path.is_absolute() else document.parent / path).resolve()
            if not path.exists():
                raise ValueError("Required local document/evidence link missing: " + str(document) + " -> " + str(path))
            record = {"document": str(document), "target": str(path)}
            (retired if path == VIDEO.resolve() else checked).append(record)
    return {
        "verified_retained_links": checked,
        "raw_input_references_intentionally_retired_after_cleanup": retired,
        "network_urls_checked": False,
    }


def delete_exact_download(path, identity, manifests, receipt):
    """The sole deletion primitive. All inputs must be previously verified."""
    if identity.get("all_final_gates_passed") is not True or not manifests:
        raise ValueError("Deletion requires completed final verification gates and retained manifests")
    if receipt.exists() or receipt.is_symlink():
        raise ValueError("Never overwrite an existing cleanup receipt")
    current = validate_video(path, identity["download_receipt"])
    for key in ("device", "inode", "bytes", "mtime_ns", "sha256", "path"):
        if current[key] != identity[key]:
            raise ValueError("Exact video identity changed after final verification")
    for manifest in manifests:
        verify_inventory(manifest)
    retained = {str(p): sha(p) for p in receipt.parent.glob("*_manifest.json")}
    if not retained:
        raise ValueError("Retained SHA256 manifest files must exist before deletion")
    reports_path = receipt.parent / "required_reports_manifest.json"
    if not reports_path.is_file():
        raise ValueError("Final report hash manifest is required before deletion")
    for name, digest in read(reports_path).items():
        if not Path(name).is_file() or sha(Path(name)) != digest:
            raise ValueError("Final retained report changed before deletion")
    # Reserve the exclusive receipt before unlink, so a prior receipt cannot be
    # overwritten after data removal. No recursive or user-selected target.
    with receipt.open("x") as stream:
        try:
            latest = path.lstat()
            if (
                not stat.S_ISREG(latest.st_mode)
                or latest.st_ino != identity["inode"]
                or latest.st_dev != identity["device"]
                or latest.st_size != SOURCE_BYTES
                or latest.st_mtime_ns != identity["mtime_ns"]
            ):
                raise ValueError("Downloaded path changed immediately before deletion")
            path.unlink()
            value = {
                "schema": "test2-owned-download-cleanup:v1",
                "status": "deleted_only_downloaded_test2_video",
                "path": str(path),
                "bytes_removed": SOURCE_BYTES,
                "source_sha256": SOURCE_SHA,
                "drive_file_id": DRIVE_FILE_ID,
                "original_remote_source_unchanged": True,
                "retained_manifest_sha256": retained,
                "final_verification_sha256": sha(receipt.parent / "verification.json")
                if (receipt.parent / "verification.json").is_file()
                else None,
                "deleted_paths": [str(path)],
                "annotations_predictions_proxies_models_reports_preserved": True,
                "automatic_test3": False,
                "completed_utc": datetime.now(UTC).isoformat(),
            }
        except Exception as error:
            json.dump(
                {"status": "cleanup_failed_or_refused", "error": str(error), "path_still_exists": path.exists()},
                stream,
                indent=2,
            )
            stream.flush()
            os.fsync(stream.fileno())
            raise
        json.dump(value, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    for manifest in manifests:
        verify_inventory(manifest)
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-receipt", type=Path, required=True)
    parser.add_argument("--delete-downloaded-video", action="store_true")
    args = parser.parse_args()
    download = read(TEST / "inputs/download_verification.json")
    identity = validate_video(VIDEO, download)
    inputs = Inputs()
    bundle = load_bundle(EXTERNAL, inputs)
    for name, digest in bundle["after"]["plan"]["source_files_sha256"].items():
        if sha(Path(name)) != digest:
            raise ValueError("Current source differs from the completed fresh post-fix implementation")
    for arm in ("baseline_v1", "improved_v1"):
        path = EXTERNAL / arm
        bound = load_analysis_input(path / "run", None)
        if bound["source_sha256"] != SOURCE_SHA or bound["media"]["n_frames"] != N:
            raise ValueError("Both arms must be genuine full Test2 fresh inference")
        consumed = {}
        _, frames = load_chunks(bound["cache_dir"], bound["cache_sha256"], consumed)
        audit_frames(frames, N)
        del frames
    base_completion = read(EXTERNAL / "baseline_v1/baseline_completion.json")
    if (
        base_completion.get("status") != "completed_fresh_Test2_baseline_and_diagnostics"
        or base_completion.get("annotations_unchanged") is not True
        or base_completion.get("frames") != N
    ):
        raise ValueError("Completed original Test2 baseline receipt required")
    improved = EXTERNAL / "improved_v1"
    verification = read(improved / "artifact_verification.json")
    verify_hash_map(improved, verification["artifacts_sha256"])
    verify_hash_map(bundle["after"]["matrix_path"].parent, verification["report_sha256"])
    if not bundle["before"]["matrix"]["unavailable_metrics"] or set(
        bundle["before"]["matrix"]["unavailable_metrics"]
    ) != set(bundle["after"]["matrix"]["unavailable_metrics"]):
        raise ValueError("All unavailable metric families must remain explicitly accounted for")
    for arm in (bundle["before"], bundle["after"]):
        for name, metric in arm["matrix"]["unavailable_metrics"].items():
            if metric.get("status") != "unavailable" or metric.get("value") is not None:
                raise ValueError("Missing independent labels cannot become numerical accuracy: " + name)
    semantic = read(EXTERNAL / "test1_semantic_regression_v1/semantic_regression_metrics.json")
    feedback = semantic.get("perception_schedule_feedback", {})
    if (
        feedback.get("schedule_driver_equal") is not True
        or feedback.get("differing_driver_frontiers")
        or feedback.get("unknown_driver_frontiers")
        or semantic.get("original_inputs_annotations_cache_unchanged") is not True
    ):
        raise ValueError("Test1 full semantic regression and equal observed cadence drivers required before cleanup")
    semantic_completion = read(EXTERNAL / "test1_semantic_regression_v1/completion.json")
    verify_hash_map(EXTERNAL / "test1_semantic_regression_v1", semantic_completion["artifact_sha256"])
    fix = read(TEST / "fixes/applied_fix_receipt.json")
    if (
        sha(TEST / "fixes/applied_fix_receipt.json") != sha(improved / "applied_fix_receipt.json")
        or sha(Path(fix["test_file"])) != fix["test_sha256"]
    ):
        raise ValueError("Applied source/test fix differs from fresh evaluated repair")
    if any(
        fix.get(k) is not True
        for k in (
            "regressions_passed",
            "broad_unit_regressions_passed",
            "baseline_protected",
            "perception_models_profile_unchanged",
        )
    ):
        raise ValueError("Passed applied-source fix and broad regression receipts required")
    for log in fix["test_logs"]:
        if sha(log["path"]) != log["sha256"]:
            raise ValueError("Source-fix test evidence changed")
    annotations = verify_annotations()
    report_json = REPORT.with_suffix(".json")
    payload = read(report_json)
    if (
        payload.get("schema") != "test2-consolidated-before-after:v1"
        or payload.get("status") != "completed_consolidated_report"
        or payload.get("source_sha256") != SOURCE_SHA
        or payload.get("physical_accuracy_gain_claimed") is not False
        or payload.get("prior_records_overwritten") is not False
    ):
        raise ValueError("Completed truthful Test2 consolidated Markdown/JSON required")
    review = read(args.review_receipt)
    review_hash = sha(args.review_receipt)
    validate_review(review, [REPORT, report_json, improved / "before_after_comparison.json"])
    documents = [REPORT, *TEST.rglob("*.md"), *EXTERNAL.rglob("*.md")]
    links = local_document_links(documents)
    inputs.unchanged()
    folder = TEST / "retention" / datetime.now(UTC).strftime("verification_%Y%m%dT%H%M%S_%fZ")
    folder.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(args.review_receipt, folder / "final_review_receipt.json")
    shutil.copyfile(__file__, folder / "verify_and_cleanup_test02.executed.py")
    manifests = [inventory(EXTERNAL, [VIDEO, folder]), inventory(TEST, [VIDEO, folder])]
    for name, manifest in zip(
        ("external_artifacts_manifest.json", "workspace_test02_manifest.json"), manifests, strict=True
    ):
        dump(folder / name, manifest)
    reports = {str(p): sha(p) for p in (REPORT, report_json, improved / "before_after_comparison.json")}
    dump(folder / "required_reports_manifest.json", reports)
    dump(
        folder / "verification.json",
        {
            "schema": "test2-final-retention-verification:v1",
            "status": "all_final_gates_passed",
            "source_identity": identity,
            "download_receipt": download,
            "review_receipt_sha256": review_hash,
            "original_annotations": annotations,
            "local_document_links": links,
            "retained_reports_sha256": reports,
            "delete_requested": args.delete_downloaded_video,
            "automatic_test3": False,
            "helper_sha256": sha(Path(__file__)),
        },
    )
    for manifest in manifests:
        verify_inventory(manifest)
    validate_review(review, [REPORT, report_json, improved / "before_after_comparison.json"])
    if sha(args.review_receipt) != review_hash:
        raise ValueError("Final review receipt changed during retention verification")
    identity.update(all_final_gates_passed=True, download_receipt=download)
    if args.delete_downloaded_video:
        value = delete_exact_download(VIDEO, identity, manifests, folder / "cleanup_receipt.json")
    else:
        value = {"status": "verified_only_video_preserved", "video_deleted": False}
        dump(folder / "verify_only_receipt.json", value)
    print(json.dumps({**value, "verification_directory": str(folder)}, indent=2))


if __name__ == "__main__":
    main()
