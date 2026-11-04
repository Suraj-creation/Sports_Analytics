"""SS22 imports preserve published truth without inventing alignment or identity review.

Fixtures are synthetic. Root runs these tests only on the configured GPU server.
The importer module is intentionally absent until that initial RED run is observed.
"""

from __future__ import annotations

import csv
import hashlib
import importlib
import io
import json
from copy import deepcopy

import pytest


FIELDS = (
    "rally", "ball_round", "frame_num", "player", "type", "roundscore_A", "roundscore_B",
    "getpoint_player", "flaw", "hit_x", "hit_y",
)


def source_rows():
    return [
        [7, 1, 101, "A", "發短球", 1, 0, "", "", "", ""],
        [7, 2, 126, "B", "防守回抽", 1, 0, "", "", 510, 220],
        [7, 3, 151, "A", "unreleased, ambiguous shot", 1, 0, "A", 1, 620, 320],
        [8, 1, 201, "B", "殺球", 1, 1, "B", "", 600, 220],
        [9, 1, 251, "B", "發長球", 1, 2, "", "", "", ""],
        [9, 2, 276, "A", "勾球", 1, 2, "B", "", 620, 320],
    ]


def raw_csv(rows=None, fields=FIELDS):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(fields)
    writer.writerows(source_rows() if rows is None else rows)
    return stream.getvalue().encode("utf-8")


def arguments(rows=None):
    raw = raw_csv(rows)
    return raw, {
        "expected_csv_sha256": hashlib.sha256(raw).hexdigest(),
        "session_id": "SYNTHETICSESSION1",
        "source_media_sha256": "a" * 64,
        "proxy_sha256": "b" * 64,
        "timebase": "canonical_media_seconds",
        "fps_num": 25,
        "fps_den": 1,
        "n_frames": 400,
        "width": 1280,
        "height": 720,
        "label_to_proxy_frame_offset": -1,
        "match_format": "singles",
        "selected_windows": [
            {"window_id": "set1-rally7", "rally_id": 7, "window_frames": [95, 160],
             "exhaustive_published_contacts": True},
            {"window_id": "set1-rally9", "rally_id": 9, "window_frames": [245, 285],
             "exhaustive_published_contacts": True},
        ],
        # Deliberately reversed: A is never assumed to mean configured P1.
        "scoring_labels": {"A": "P2", "B": "P1"},
        "provenance": {
            "dataset": "CoachAI-ShuttleSet22",
            "dataset_revision": "c" * 40,
            "match_id": "synthetic_singles_match",
            "set_no": 1,
            "annotations_url": "https://example.invalid/official/set1.csv",
            "source_video_url": "https://example.invalid/official/broadcast",
            "publication": "https://example.invalid/official/paper",
            "annotation_origin": "published_human_annotation",
            "source_competitors": {"A": "Alpha Athlete", "B": "Beta Athlete"},
            "upstream_tuned": True,
            "license_evidence": {
                "id": "MIT",
                "url": "https://example.invalid/official/LICENSE",
                "sha256": "d" * 64,
                "scope": "publisher_repository_original_annotations",
            },
        },
        "split": "development",
    }


def actor_map():
    return {
        "A": {"source_competitor": "Alpha Athlete", "configured_competitor": "Alpha Athlete",
              "scoring_label": "P2", "actor_id": "P2"},
        "B": {"source_competitor": "Beta Athlete", "configured_competitor": "Beta Athlete",
              "scoring_label": "P1", "actor_id": "P1"},
    }


def convert(rows=None, **changes):
    raw, kwargs = arguments(rows)
    kwargs.update(changes)
    module = importlib.import_module("research.evaluation.shuttleset_reference")
    return module.convert_reference(raw, **kwargs)


def test_explicit_offset_windows_and_raw_truth_survive_without_identity_or_review():
    documents = convert()
    assert [d["window_id"] for d in documents] == ["set1-rally7", "set1-rally9"]
    first = documents[0]
    assert first["window_frames"] == [95, 160]
    assert first["window_s"] == [3.8, 6.4]
    assert [s["frame_idx"] for s in first["shots"]] == [100, 125, 150]
    assert [s["time_s"] for s in first["shots"]] == [4.0, 5.0, 6.0]
    assert [s["source_frame"] for s in first["shots"]] == [101, 126, 151]
    assert [s["family"] for s in first["shots"]] == ["short_serve", "drive", "unknown"]
    assert [s["source_hitter"] for s in first["shots"]] == ["A", "B", "A"]
    assert [s["source_competitor"] for s in first["shots"]] == [
        "Alpha Athlete", "Beta Athlete", "Alpha Athlete",
    ]
    assert [s["scoring_label"] for s in first["shots"]] == ["P2", "P1", "P2"]
    assert all(s["player_id"] is None for d in documents for s in d["shots"])
    assert first["shots"][2]["raw_family"] == "unreleased, ambiguous shot"
    assert first["shots"][2]["source_row"]["flaw"] == "1"
    assert first["shots"][2]["source_row"]["getpoint_player"] == "A"
    assert first["shots"][0]["source_row"]["roundscore_A"] == "1"
    assert first["shots"][0]["source_row"]["roundscore_B"] == "0"
    assert sum(len(d["shots"]) for d in documents) == 5  # unselected rally 8 stays excluded
    assert len({s["annotation_id"] for d in documents for s in d["shots"]}) == 5
    assert first["status"] == "draft" and first["split"] == "development"
    assert first["review"]["human_verified"] is False
    assert first["review"]["our_human_reviewed"] is False
    assert first["reference_provenance"]["annotation_origin"] == "published_human_annotation"
    assert first["reference_provenance"]["upstream_tuned"] is True
    assert first["reference_provenance"]["annotations_sha256"] == arguments()[1]["expected_csv_sha256"]
    assert first["media_sha256"] == "a" * 64 and first["proxy_sha256"] == "b" * 64
    assert first["truth_coverage"]["source_hitter"] == 3
    assert first["truth_coverage"]["benchmark_actor"] == 0
    assert first["metric_availability"]["known_shot_labels"] is True
    assert first["metric_availability"]["rally_down_boundaries"] is False
    assert first["metric_availability"]["dense_shuttle"] is False
    assert first["metric_availability"]["score_sequence"] is False
    assert first["metric_availability"]["durable_player_identity"] is False


def test_explicit_verified_competitor_map_exposes_truth_without_resolving_machine_actors():
    from research.shot_benchmark import evaluate

    labels = convert(benchmark_actor_map=actor_map())[0]
    assert [s["player_id"] for s in labels["shots"]] == ["P2", "P1", "P2"]
    assert labels["truth_coverage"]["benchmark_actor"] == 3
    predictions = {key: labels[key] for key in ("schema_version", "session_id", "media_sha256", "timebase", "window_s")}
    predictions["shots"] = [
        {"time_s": 4.0, "family": "short_serve", "player_id": None, "event_id": "e1"},
        {"time_s": 5.0, "family": "drive", "player_id": None, "event_id": "e2"},
        {"time_s": 6.0, "family": "unknown", "player_id": None, "event_id": "e3"},
    ]
    result = evaluate(labels, predictions, allow_draft=True)
    assert result["matched"] == 3
    assert result["known_family"]["truth_support"] == 2
    assert result["attribution"] == {
        "labelled": 3, "correct": 0, "unresolved": 3,
        "accuracy_all_labelled": 0.0, "accuracy_resolved": None,
    }
    assert result["end_to_end"]["joint_contact_family_hitter"]["truth_count"] == 2
    assert result["end_to_end"]["joint_contact_family_hitter"]["false_negatives"] == 2
    assert result["accuracy_claim_eligible"] is False
    unbound_labels = convert()[0]
    unbound = evaluate(unbound_labels, predictions, allow_draft=True)
    assert unbound["attribution"]["labelled"] == 0
    assert unbound["end_to_end"]["joint_contact_family_hitter"]["truth_count"] == 0


@pytest.mark.parametrize("problem", ["wrong_source_name", "wrong_configured_name", "wrong_slot", "duplicate_actor", "partial_map"])
def test_ambiguous_or_unverified_benchmark_actor_bindings_are_rejected(problem):
    binding = actor_map()
    if problem == "wrong_source_name":
        binding["A"]["source_competitor"] = "Someone Else"
    elif problem == "wrong_configured_name":
        binding["A"]["configured_competitor"] = "Someone Else"
    elif problem == "wrong_slot":
        binding["A"]["scoring_label"] = "P1"
    elif problem == "duplicate_actor":
        binding["B"]["actor_id"] = "P2"
    else:
        binding.pop("B")
    with pytest.raises(ValueError):
        convert(benchmark_actor_map=binding)


@pytest.mark.parametrize(
    "raw_family,family",
    [("放小球", "net_shot"), ("擋小球", "block"), ("殺球", "smash"), ("點扣", "smash"),
     ("挑球", "lift"), ("防守回挑", "lift"), ("長球", "clear"), ("平球", "drive"),
     ("小平球", "drive"), ("後場抽平球", "drive"), ("切球", "drop"), ("過渡切球", "drop"),
     ("過度切球", "drop"), ("推球", "push"), ("撲球", "rush"), ("防守回抽", "drive"),
     ("勾球", "cross_net"), ("發短球", "short_serve"), ("發長球", "long_serve"),
     ("未知球種", "unknown"), ("unsupported new type", "unknown")],
)
def test_only_documented_native_taxonomy_is_mapped_and_unknown_raw_labels_are_retained(raw_family, family):
    rows = source_rows()
    rows[0][4] = raw_family
    shot = convert(rows)[0]["shots"][0]
    assert shot["family"] == family
    assert shot["raw_family"] == raw_family
    assert shot["mapping_reason"]


@pytest.mark.parametrize(
    "changes",
    [{"expected_csv_sha256": "e" * 64}, {"source_media_sha256": "bad"}, {"proxy_sha256": "BAD"},
     {"timebase": "source_seconds"}, {"fps_num": 0}, {"fps_den": True},
     {"label_to_proxy_frame_offset": True}, {"label_to_proxy_frame_offset": -0.5},
     {"n_frames": 275}, {"width": 0}, {"match_format": "doubles"}],
)
def test_invalid_source_proxy_timebase_and_format_bindings_fail_closed(changes):
    with pytest.raises(ValueError):
        convert(**changes)


@pytest.mark.parametrize("problem", ["moving_revision", "missing_license", "missing_license_hash", "missing_origin", "missing_tuning_declaration"])
def test_published_source_and_license_evidence_are_required_without_inventing_them(problem):
    provenance = arguments()[1]["provenance"]
    if problem == "moving_revision":
        provenance["dataset_revision"] = "main"
    elif problem == "missing_license":
        provenance.pop("license_evidence")
    elif problem == "missing_license_hash":
        provenance["license_evidence"].pop("sha256")
    elif problem == "missing_origin":
        provenance.pop("annotation_origin")
    else:
        provenance.pop("upstream_tuned")
    with pytest.raises(ValueError):
        convert(provenance=provenance)


@pytest.mark.parametrize("problem", ["duplicate_frame", "duplicate_round", "fractional_frame", "end_exclusive_anchor", "missing_rally", "overlap", "duplicate_window", "unasserted_scope"])
def test_invalid_selected_contact_population_cannot_silently_change_denominators(problem):
    rows = source_rows()
    windows = deepcopy(arguments()[1]["selected_windows"])
    if problem == "duplicate_frame":
        rows[1][2] = 101
    elif problem == "duplicate_round":
        rows[1][1] = 1
    elif problem == "fractional_frame":
        rows[0][2] = "101.5"
    elif problem == "end_exclusive_anchor":
        rows[2][2] = 161
    elif problem == "missing_rally":
        windows[0]["rally_id"] = 88
    elif problem == "overlap":
        windows[1]["window_frames"] = [150, 285]
    elif problem == "duplicate_window":
        windows[1]["window_id"] = "set1-rally7"
    else:
        windows[0]["exhaustive_published_contacts"] = False
    with pytest.raises(ValueError):
        convert(rows, selected_windows=windows)


def test_unknown_source_hitter_remains_unknown_even_when_other_actors_are_bound():
    rows = source_rows()
    rows[1][3] = ""
    labels = convert(rows, benchmark_actor_map=actor_map())[0]
    shot = labels["shots"][1]
    assert shot["source_hitter"] is None
    assert shot["source_competitor"] is None
    assert shot["scoring_label"] is None and shot["player_id"] is None
    assert labels["truth_coverage"]["source_hitter"] == 2
    assert labels["truth_coverage"]["benchmark_actor"] == 2


def test_project_holdout_reservation_does_not_rewrite_upstream_exposure_or_claim_human_review():
    with pytest.raises(ValueError, match="reserv"):
        convert(split="held_out")
    labels = convert(split="held_out", held_out_reserved_before_tuning=True)[0]
    assert labels["split"] == "held_out" and labels["status"] == "draft"
    assert labels["review"]["human_verified"] is False
    assert labels["reference_provenance"]["upstream_tuned"] is True
    assert labels["population"]["held_out_reserved_before_tuning"] is True
    assert labels["population"]["project_split"] == "held_out"


def test_cli_checks_actual_csv_source_and_proxy_bytes_and_refuses_overwrite(tmp_path):
    module = importlib.import_module("research.evaluation.shuttleset_reference")
    raw, metadata = arguments()
    source, proxy = tmp_path / "source.mp4", tmp_path / "proxy.mp4"
    source.write_bytes(b"synthetic source bytes, not a decoded video")
    proxy.write_bytes(b"synthetic proxy bytes, not a decoded video")
    metadata["source_media_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    metadata["proxy_sha256"] = hashlib.sha256(proxy.read_bytes()).hexdigest()
    csv_path, metadata_path = tmp_path / "set1.csv", tmp_path / "binding.json"
    csv_path.write_bytes(raw)
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    output = tmp_path / "converted"
    argv = ["--csv", str(csv_path), "--metadata", str(metadata_path), "--source-media", str(source),
            "--proxy", str(proxy), "--output-dir", str(output)]
    module.main(argv)
    files = sorted(output.glob("*.json"))
    assert [p.name for p in files] == ["set1-rally7.json", "set1-rally9.json"]
    saved = json.loads(files[0].read_text(encoding="utf-8"))
    assert saved["media_sha256"] == metadata["source_media_sha256"]
    assert saved["proxy_sha256"] == metadata["proxy_sha256"]
    before = {p.name: p.read_bytes() for p in files}
    with pytest.raises(SystemExit) as error:
        module.main(argv)
    assert error.value.code != 0
    assert {p.name: p.read_bytes() for p in files} == before
    proxy.write_bytes(b"tampered proxy bytes")
    argv[-1] = str(tmp_path / "tampered-output")
    with pytest.raises(SystemExit) as error:
        module.main(argv)
    assert error.value.code != 0
    assert not (tmp_path / "tampered-output").exists()
