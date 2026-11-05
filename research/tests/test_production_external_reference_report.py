"""Evaluation contracts only; synthetic controls do not establish sports accuracy."""

import copy
import csv
from fractions import Fraction
from types import SimpleNamespace

import pytest

from research import production_external_reference_report as report


def labels():
    return {
        "schema_version": 1,
        "session_id": "NEW",
        "media_sha256": "a" * 64,
        "timebase": "canonical_media_seconds",
        "window_s": [0, 10],
        "window_frames": [0, 300],
        "fps_num": 30,
        "fps_den": 1,
        "media_n_frames": 300,
        "width": 1280,
        "height": 720,
        "status": "draft",
        "split": "diagnostic",
        "exhaustive": True,
        "review": {"human_verified": False},
        "shots": [],
    }


def truth(frame, family="smash", actor="A"):
    return {
        "annotation_id": f"source-{frame}",
        "frame_idx": frame,
        "time_s": frame / 30,
        "family": family,
        "raw_family": family,
        "player_id": actor,
        "source_hitter": actor,
    }


def event(name, kind, frame, *, status="confirmed", payload=None, actor=None, supersedes=None):
    return SimpleNamespace(
        event_id=name,
        type=kind,
        frame_start=frame,
        supersedes=supersedes,
        status=SimpleNamespace(value=status),
        payload=payload or {},
        actors=SimpleNamespace(player_id=actor),
    )


def test_binding_changes_only_three_keys_and_copies_nested_data():
    original = {
        **labels(),
        "session_id": "OLD",
        "proxy_sha256": "b" * 64,
        "alignment": {"offset": -12001},
        "shots": [truth(10)],
    }
    preserved = copy.deepcopy(original)
    new = report.derive_binding(original, "NEW", "c" * 64, "d" * 64)
    assert {k for k in new if new[k] != original[k]} == {"session_id", "media_sha256", "proxy_sha256"}
    assert new["review"]["human_verified"] is False and new["shots"] == original["shots"]
    new["shots"][0]["family"] = "unknown"
    assert original == preserved


def test_binding_rejects_old_session_id():
    with pytest.raises(ValueError, match="new isolated"):
        report.derive_binding(labels(), "NEW", "c" * 64, "d" * 64)


def test_provisional_contacts_and_missing_or_provisional_strokes_are_retained():
    contacts = [event("c1", "contact", 1, status="provisional", actor="P1"), event("c2", "contact", 299, actor="A")]
    stroke = event("s1", "stroke", 1, status="provisional", payload={"contact_event_id": "c1", "stroke": "smash"})
    events = [*contacts, stroke]
    machine = report.extract_predictions(
        events, {e.event_id: e for e in events}, labels(), report.load_helper()._root_event_id
    )
    assert len(machine["shots"]) == 2
    assert [s["family"] for s in machine["shots"]] == ["unknown", "unknown"]
    assert [s["raw_actor_id"] for s in machine["shots"]] == ["P1", "A"]
    assert all(s["player_id"] is None for s in machine["shots"])


def test_stroke_revision_reference_resolves_contact_root():
    old = event("old", "contact", 30)
    live = event("new", "contact", 30, supersedes="old")
    stroke = event("s", "stroke", 30, payload={"contact_event_id": "old", "stroke": "smash"})
    events = [live, stroke]
    machine = report.extract_predictions(
        events, {"old": old, "new": live, "s": stroke}, labels(), report.load_helper()._root_event_id
    )
    assert machine["shots"][0]["family"] == "smash"
    assert machine["shots"][0]["contact_root_id"] == "old"


@pytest.mark.parametrize("case", ["orphan", "frame", "class", "duplicate", "outside"])
def test_invalid_event_relationships_are_not_hidden(case):
    contact = event("c", "contact", 20 if case != "outside" else 300)
    stroke = event(
        "s",
        "stroke",
        21 if case == "frame" else 20,
        payload={
            "contact_event_id": "missing" if case == "orphan" else "c",
            "stroke": "invented" if case == "class" else "smash",
        },
    )
    events = [contact, stroke]
    if case == "duplicate":
        events.append(event("s2", "stroke", 20, payload={"contact_event_id": "c", "stroke": "drop"}))
    with pytest.raises(ValueError):
        report.extract_predictions(
            events, {e.event_id: e for e in events}, labels(), report.load_helper()._root_event_id
        )


def test_unchanged_matching_inclusive_tolerances_and_unknown_denominators():
    helper = report.load_helper()
    document = {**labels(), "shots": [truth(30), truth(90, "drop"), truth(150, "drive"), truth(210, "lift")]}
    machine = {k: document[k] for k in ("schema_version", "session_id", "media_sha256", "timebase", "window_s")}
    machine["shots"] = [
        dict(event_id="at3", frame_idx=33, time_s=33 / 30, family="smash", player_id=None),
        dict(event_id="at6", frame_idx=96, time_s=96 / 30, family="unknown", player_id=None),
        dict(event_id="at7", frame_idx=157, time_s=157 / 30, family="drive", player_id=None),
        dict(event_id="wrong", frame_idx=210, time_s=7, family="smash", player_id=None),
        dict(event_id="break", frame_idx=280, time_s=280 / 30, family="unknown", player_id=None),
    ]
    at3, at6 = (helper.timing_metrics(document, machine, n) for n in (3, 6))
    assert at3["contact_detection"]["true_positives"] == 2
    assert at6["contact_detection"] == {
        "truth_count": 4,
        "prediction_count": 5,
        "true_positives": 3,
        "false_positives": 2,
        "false_negatives": 1,
        "precision": 3 / 5,
        "recall": 3 / 4,
        "f1": 2 / 3,
    }
    assert at6["matched_known_class"]["correct"] == 1
    assert at6["matched_known_class"]["predicted_unknown"] == 1
    assert at6["classification"]["unknown_prediction_fraction"] == 2 / 5
    assert at6["hitter"]["benchmark_actor_truth"] == 4
    assert at6["hitter"]["resolved_predictions_on_matched_truth"] == 0


def test_all_four_hitter_labels_remain_in_denominator():
    helper = report.load_helper()
    document = {
        **labels(),
        "shots": [truth(frame, actor=actor) for frame, actor in zip([30, 60, 90, 120], "ABCD", strict=True)],
    }
    machine = {k: document[k] for k in ("schema_version", "session_id", "media_sha256", "timebase", "window_s")}
    machine["shots"] = [
        {
            "event_id": str(s["frame_idx"]),
            "time_s": s["time_s"],
            "frame_idx": s["frame_idx"],
            "family": s["family"],
            "player_id": None,
        }
        for s in document["shots"]
    ]
    metrics = helper.timing_metrics(document, machine, 3)
    assert set(metrics["hitter"]["end_to_end_per_actor"]) == set("ABCD")
    assert metrics["hitter"]["benchmark_actor_truth"] == 4
    assert metrics["hitter"]["coverage_on_all_actor_truth"] == 0


def test_frozen_d9_projection_keeps_unknown_and_native_labels():
    protocol = {
        "before_predictions": True,
        "strict_native12_retained": True,
        "platform_to_reference": {k: k for k in (*report.NATIVE12, "unknown")},
    }
    protocol["platform_to_reference"].update(block="unknown", cross_net="net_shot", rush="push")
    machine = {"shots": [{"family": k} for k in ("block", "unknown", "cross_net", "rush")]}
    projected = report.project_d9(machine, protocol)
    assert [s["family"] for s in projected["shots"]] == ["unknown", "unknown", "net_shot", "push"]
    assert [s["native12_family"] for s in projected["shots"]] == ["block", "unknown", "cross_net", "rush"]
    assert machine["shots"][0]["family"] == "block"


def write_coarse(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(report.TEST7_FIELDS)
        for lo, hi in rows:
            writer.writerow([lo, hi, "OUTCOME_MUST_NOT_PARSE", "x", "x", "x", "x", "x"])


def test_exact_test7_seconds_and_no_outcome_consumption(tmp_path):
    path = tmp_path / "primary.csv"
    write_coarse(path, [("0.1", "0.2"), ("6", "15")])
    assert report.test7_intervals(path, Fraction(30), 500, expected_count=2) == [(3, 6), (180, 450)]


@pytest.mark.parametrize(
    "rows,rate,count",
    [([(".01", ".1")], Fraction(30), 1), ([("6", "15")], Fraction(30000, 1001), 1), ([("6", "15")], Fraction(30), 31)],
)
def test_test7_rejects_rounding_or_missing_rows(tmp_path, rows, rate, count):
    path = tmp_path / "primary.csv"
    write_coarse(path, rows)
    with pytest.raises(ValueError):
        report.test7_intervals(path, rate, 500, expected_count=count)


def finished_fixture():
    doc = labels()
    doc["proxy_sha256"] = "b" * 64
    media = {
        "source_sha256": doc["media_sha256"],
        "proxy_sha256": doc["proxy_sha256"],
        "canonical": {"n_frames": 300, "fps_num": 30, "fps_den": 1, "width": 1280, "height": 720},
    }
    manifest = {
        "schema": "fresh-real-video-run-v1",
        "finished_utc": "2026-11-05",
        "exit_code": 2,
        "sessions": [{"session_id": "NEW", "status": "partial"}],
    }
    detail = {
        "schema": "fresh-real-video-validation-v1",
        "finished_utc": "2026-11-05",
        "status": "partial",
        "session_id": "NEW",
        "frames_processed": 300,
        "inference_window_frames": [0, 300],
        "prefix_truncated": False,
        "cached_perception_used": False,
        "score_or_identity_reviews_seeded": False,
        "media": media,
    }
    return manifest, detail, doc


def test_finished_full_clip_partial_capabilities_is_explicitly_allowed():
    manifest, detail, document = finished_fixture()
    report.validate_finished(manifest, detail, "NEW", document)


@pytest.mark.parametrize(
    "field,value",
    [
        ("finished_utc", None),
        ("frames_processed", 299),
        ("inference_window_frames", [30, 300]),
        ("status", "running"),
        ("cached_perception_used", True),
        ("prefix_truncated", True),
        ("score_or_identity_reviews_seeded", True),
    ],
)
def test_unfinished_cached_seeded_or_truncated_runs_rejected(field, value):
    manifest, detail, document = finished_fixture()
    detail[field] = value
    with pytest.raises(ValueError):
        report.validate_finished(manifest, detail, "NEW", document)


def partition_fixture():
    documents = []
    first_frame = 0
    for index, count in enumerate(report.COUNTS["india"]):
        document = {
            **labels(),
            "media_n_frames": 4800,
            "proxy_sha256": "b" * 64,
            "match_format": "singles",
            "window_frames": [index * 1200, (index + 1) * 1200],
            "population": {"exhaustive_published_contacts": True},
            "reference_provenance": {"frame_mapping": {"offset": -12001}},
            "shots": [],
        }
        for offset in range(count):
            frame = index * 1200 + offset
            document["shots"].append({**truth(frame), "source_frame": frame + 12001})
        documents.append(document)
        first_frame += count
    assert first_frame == 85
    return documents


def test_all_four_partitions_combined_without_timestamp_or_annotation_changes():
    documents = partition_fixture()
    before = copy.deepcopy(documents)
    composite = report.composite_labels(documents, "india")
    assert len(composite["shots"]) == 85
    assert composite["window_frames"] == [0, 4800]
    assert composite["window_s"] == [0, 160]
    assert composite["shots"] == [shot for d in documents for shot in d["shots"]]
    assert documents == before


@pytest.mark.parametrize("change", ["gap", "count", "offset", "review", "annotation", "time"])
def test_partition_scope_and_frozen_alignment_cannot_be_repaired(change):
    documents = partition_fixture()
    if change == "gap":
        documents[1]["window_frames"][0] += 1
    elif change == "count":
        documents[1]["shots"].pop()
    elif change == "offset":
        documents[2]["reference_provenance"]["frame_mapping"]["offset"] = -12000
    elif change == "review":
        documents[2]["review"]["human_verified"] = True
    elif change == "annotation":
        documents[0]["shots"][1]["annotation_id"] = documents[0]["shots"][0]["annotation_id"]
    elif change == "time":
        documents[0]["shots"][0]["time_s"] += 1 / 30
    with pytest.raises(ValueError):
        report.composite_labels(documents, "india")


def test_unfinished_harness_rejected_before_any_reference_label_read(tmp_path):
    import json

    manifest, detail, document = finished_fixture()
    detail["finished_utc"] = None
    run = tmp_path / "run"
    (run / "results/NEW").mkdir(parents=True)
    (run / "run.json").write_text(json.dumps(manifest))
    (run / "results/NEW/report.json").write_text(json.dumps(detail))
    discovery = tmp_path / "discovery.json"
    discovery.write_text(
        json.dumps(
            {
                "additional_available_materials": [
                    {
                        "recording": "india",
                        "reference_summary": document,
                        "proxy": {"sha256": "a" * 64},
                        "derived_labels": [{"path": "NOT_ALLOWED_TO_OPEN_YET"}],
                    }
                ]
            }
        )
    )
    output = tmp_path / "new-evaluation"
    with pytest.raises(ValueError, match="unfinished"):
        report.run_shots(run, "NEW", "india", discovery, output)
    assert not output.exists()


def complete_test7_fixture(tmp_path):
    import json

    from scripts.benchmarking.evaluate_rallies import write_predictions

    run = tmp_path / "run"
    run.mkdir()
    source = tmp_path / "source.mp4"
    source.write_bytes(b"input media bytes; no decode")
    source_sha = report.digest(source)
    proxy = run / "data/media" / source_sha / "proxy.mp4"
    proxy.parent.mkdir(parents=True)
    proxy.write_bytes(b"prepared proxy bytes; no decode")
    coarse = tmp_path / "primary.csv"
    write_coarse(coarse, [(index * 2, index * 2 + 1) for index in range(31)])
    document = {
        "status": "completed",
        "frames_processed": 3000,
        "frontier_frame": 2999,
        "cached_perception_used": False,
        "source_sha256": source_sha,
        "proxy_sha256": report.digest(proxy),
        "media": {"n_frames": 3000, "fps_num": 30, "fps_den": 1},
    }
    (run / "inference.json").write_text(json.dumps(document))
    executor = {
        "status": "completed",
        "worker_exit_code": 0,
        "frozen_source_inputs_unchanged": True,
        "output_proxy_sha256": report.digest(proxy),
    }
    run.with_suffix(".executor.json").write_text(json.dumps(executor))
    (run / "session.json").write_text(
        json.dumps(
            {
                "session_id": "NEW",
                "frontier_frame": 2999,
                "source": {"sha256": source_sha},
                "status": "analysed",
                "media": document["media"],
            }
        )
    )
    (run / "events.jsonl").write_text("")
    write_predictions(run / "predicted_rallies.csv", [], 30)
    discovery = tmp_path / "discovery.json"
    discovery.write_text(
        json.dumps(
            {
                "test7": {
                    "source": {
                        "path": str(source),
                        "sha256": source_sha,
                        "probe": {"streams": [{"codec_type": "video", "avg_frame_rate": "30/1", "nb_frames": "3000"}]},
                    },
                    "primary_reference": {"path": str(coarse), "sha256": report.digest(coarse)},
                }
            }
        )
    )
    return run, discovery


def test_complete_test7_adapter_retains_all31_coarse_misses_and_never_rewrites_inputs(tmp_path):
    run, discovery = complete_test7_fixture(tmp_path)
    before = {str(p): report.digest(p) for p in tmp_path.rglob("*") if p.is_file()}
    output = tmp_path / "new-agreement"
    result = report.run_test7(run, discovery, output)
    assert result["reference_rows"] == 31
    assert result["metrics"]["detection"]["false_negatives"] == 31
    assert result["metrics"]["detection"]["predicted_count"] == 0
    assert len(result["comparisons"]) == 31
    assert result["accuracy_claim_eligible"] is False
    assert before == {path: report.digest(path) for path in before}
    with pytest.raises(ValueError, match="must be new"):
        report.run_test7(run, discovery, output)


def test_finished_test7_proxy_bytes_must_match_export(tmp_path):
    run, discovery = complete_test7_fixture(tmp_path)
    next((run / "data/media").glob("*/proxy.mp4")).write_bytes(b"changed")
    output = tmp_path / "never-created"
    with pytest.raises(ValueError, match="actual canonical proxy"):
        report.run_test7(run, discovery, output)
    assert not output.exists()


@pytest.mark.parametrize("frames", [[0, 2], [0, 1, 1], [1, 0, 2], [0, True, 2]])
def test_full_clip_coverage_cannot_be_inferred_from_only_report_count(tmp_path, frames):
    import json

    path = tmp_path / "coverage.jsonl"
    path.write_text("\n".join(json.dumps({"frame": frame}) for frame in frames))
    with pytest.raises(ValueError, match="full ordered clip"):
        report.validate_coverage(path, 3)


def test_complete_shot_adapter_derives_bindings_after_predictions_without_changing_labels(tmp_path):
    import json
    import subprocess
    import sys

    documents = partition_fixture()
    source = tmp_path / "uploaded_prepared_proxy.mp4"
    source.write_bytes(b"existing proxy fixture; not decoded or inferred")
    source_sha = report.digest(source)
    entries = []
    for index, document in enumerate(documents):
        document["session_id"] = "OLD"
        path = tmp_path / f"partition{index}.json"
        path.write_text(json.dumps(document))
        entries.append({"path": str(path), "sha256": report.digest(path)})
    metadata = tmp_path / "old-binding.json"
    metadata.write_text("{}")
    fixed = {"path": str(metadata), "sha256": report.digest(metadata)}
    run = tmp_path / "run"
    directory = run / "results/NEW"
    directory.mkdir(parents=True)
    (directory / "events.jsonl").write_text("")
    (directory / "current-events.jsonl").write_text("")
    (directory / "session.json").write_text(
        json.dumps(
            {
                "session_id": "NEW",
                "source": {"sha256": source_sha},
                "frontier_frame": 4799,
                "analysed_frames": 4800,
                "roster": {"match_format": "singles"},
            }
        )
    )
    (directory / "frame-coverage.jsonl").write_text("\n".join(json.dumps({"frame": f}) for f in range(4800)))
    manifest, detail, _ = finished_fixture()
    detail.update(frames_processed=4800, inference_window_frames=[0, 4800])
    detail["media"].update(
        source_sha256=source_sha, proxy_sha256=source_sha, source_path=str(source), proxy_path=str(source)
    )
    detail["media"]["canonical"]["n_frames"] = 4800
    detail["artifact_hashes"] = {p.name: report.digest(p) for p in directory.iterdir()}
    (run / "run.json").write_text(json.dumps(manifest))
    (directory / "report.json").write_text(json.dumps(detail))
    entry = {
        "recording": "india",
        "proxy": {"sha256": source_sha},
        "derived_labels": entries,
        "reference_summary": {"fps_num": 30, "fps_den": 1, "media_n_frames": 4800, "match_format": "singles"},
        "preparation": fixed,
        "label_binding": fixed,
        "raw_published_annotations": fixed,
        "original_source": {"recorded_sha256": "a" * 64},
        "original_crop_binding": {"decode_start": 12000},
        "annotation_to_proxy_frame_offset": -12001,
    }
    discovery = tmp_path / "discovery.json"
    discovery.write_text(json.dumps({"additional_available_materials": [entry]}))
    before = {str(p): report.digest(p) for p in tmp_path.rglob("*") if p.is_file()}
    output = tmp_path / "new-agreement"
    # Exercise the documented CLI and its package path, without model imports.
    process = subprocess.run(
        [
            sys.executable,
            str(report.ROOT / "research/production_external_reference_report.py"),
            "--recording",
            "india",
            "--run-root",
            str(run),
            "--session",
            "NEW",
            "--discovery",
            str(discovery),
            "--output",
            str(output),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert process.returncode == 0, process.stderr
    result = report.read(output / "report.json")
    assert all(m["contact_detection"]["truth_count"] == 85 for m in result["metrics_native12_strict"])
    assert all(m["contact_detection"]["false_negatives"] == 85 for m in result["metrics_native12_strict"])
    assert before == {path: report.digest(path) for path in before}
    for index, original in enumerate(documents):
        rebound = report.read(output / f"partition{index}.json")
        assert rebound["shots"] == original["shots"]
        assert rebound["review"]["human_verified"] is False
        assert {k for k in rebound if rebound[k] != original[k]} == {"session_id", "media_sha256", "proxy_sha256"}


def test_test7_worker_and_manifest_cannot_shorten_the_verified_source_together(tmp_path):
    run, discovery = complete_test7_fixture(tmp_path)
    document = report.read(discovery)
    document["test7"]["source"]["probe"]["streams"][0]["nb_frames"] = "3001"
    report.write_new(tmp_path / "different_source_header.json", document)
    with pytest.raises(ValueError, match="full source frame count"):
        report.run_test7(run, tmp_path / "different_source_header.json", tmp_path / "never-created")
