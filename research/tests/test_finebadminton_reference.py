"""Published reference conversion must preserve provenance and reject bad bindings."""

from __future__ import annotations

import hashlib
import importlib
import json
import subprocess
import sys
from copy import deepcopy

import pytest


def source_rows():
    return [
        {
            "video": "0044.mp4",
            "resolution": {"width": 1280, "height": 720},
            "fps": 25.0,
            "duration_frames": 75,
            "start_frame": 100,
            "end_frame": 175,
            "hitting": [
                {
                    "start_frame": 100,
                    "end_frame": 125,
                    "player": "Named server",
                    "get_point": [],
                    "Foundational Actions Level": {
                        "hit type": "serve",
                        "subtype": ["short serve"],
                        "hitter": "bottom",
                        "ball area": "mid front court",
                    },
                    "Tactical Semantics Level": {"player actions": ["backhand"], "shot characteristics": []},
                    "Decision Evaluation Level": {"comment": "Published comment", "quality": 4},
                },
                {
                    "start_frame": 125,
                    "end_frame": 150,
                    "player": "Named receiver",
                    "get_point": [],
                    "Foundational Actions Level": {
                        "hit type": "kill",
                        "subtype": ["jump smash"],
                        "hitter": "top",
                        "ball area": "right back court",
                    },
                },
                {
                    "start_frame": 150,
                    "end_frame": 175,
                    "player": "Named server",
                    "get_point": ["Named server"],
                    "Foundational Actions Level": {
                        "hit type": "cross-court net shot",
                        "subtype": [],
                        "hitter": "bottom",
                        "ball area": "mid front court",
                    },
                },
            ],
            "playerList": [{"name": "Named server", "role": "server"}, {"name": "Named receiver", "role": "receiver"}],
            "evaluations_new": {"score_reason": "Published narrative"},
        }
    ]


def arguments(rows=None):
    raw = json.dumps(source_rows() if rows is None else rows).encode()
    return raw, {
        "session_id": "S1",
        "video_name": "0044.mp4",
        "media_sha256": "a" * 64,
        "expected_media_sha256": "a" * 64,
        "expected_source_sha256": hashlib.sha256(raw).hexdigest(),
        "fps_num": 25,
        "fps_den": 1,
        "n_frames": 250,
        "width": 1280,
        "height": 720,
    }


def convert(rows=None, **changes):
    raw, kwargs = arguments(rows)
    kwargs.update(changes)
    module = importlib.import_module("research.finebadminton_reference")
    return module.convert_reference(raw, **kwargs)


def test_source_anchors_names_and_raw_properties_survive_without_claiming_our_review():
    result = convert()[0]
    assert result["window_s"] == [4.0, 7.0]
    assert [s["time_s"] for s in result["shots"]] == [4.0, 5.0, 6.0]
    assert [s["player_id"] for s in result["shots"]] == ["Named server", "Named receiver", "Named server"]
    assert [s["family"] for s in result["shots"]] == ["short_serve", "smash", "net_shot"]
    assert result["shots"][1]["raw_family"] == "kill"
    assert result["shots"][1]["raw_subtypes"] == ["jump smash"]
    assert result["shots"][1]["source_hitter"] == "top"
    assert result["shots"][2]["placement"] == "cross_court"
    assert len({s["annotation_id"] for s in result["shots"]}) == 3
    assert result["status"] == "draft" and result["split"] == "diagnostic"
    assert result["review"]["human_verified"] is False
    assert result["review"]["provider_human_verified"] is True
    assert result["review"]["origin"] == "published_human_refined_reference"
    assert result["reference_provenance"]["annotations_sha256"] == arguments()[1]["expected_source_sha256"]
    assert result["reference_provenance"]["dataset_revision"] == "72cae601e08c83ee8ec7e19f8fd7850e9158af7d"
    assert "2508.07554" in result["reference_provenance"]["publication"]


@pytest.mark.parametrize(
    "raw_family,subtypes,family",
    [
        ("serve", [], "unknown"),
        ("serve", ["unfamiliar serve"], "unknown"),
        ("serve", ["short serve", "flick serve"], "unknown"),
        ("serve", ["high serve", "flick serve"], "long_serve"),
        ("kill", [], "unknown"),
        ("kill", ["net kill"], "rush"),
        ("kill", ["full smash", "jump smash"], "smash"),
        ("kill", ["net kill", "jump smash"], "unknown"),
        ("unpublished shot", [], "unknown"),
        ("push shot", ["flat lift"], "push"),
        ("net lift", ["high lift"], "lift"),
        ("drop shot", [], "drop"),
    ],
)
def test_only_supported_taxonomy_is_mapped(raw_family, subtypes, family):
    rows = source_rows()
    rows[0]["hitting"][0]["Foundational Actions Level"].update({"hit type": raw_family, "subtype": subtypes})
    shot = convert(rows)[0]["shots"][0]
    assert shot["family"] == family
    assert shot["raw_family"] == raw_family and shot["raw_subtypes"] == subtypes
    assert shot["mapping_reason"]


def test_side_change_between_rallies_is_preserved_instead_of_renaming_players():
    rows = source_rows()
    second = deepcopy(rows[0])
    second.update(start_frame=175, end_frame=250)
    for shot in second["hitting"]:
        shot["start_frame"] += 75
        shot["end_frame"] += 75
        foundation = shot["Foundational Actions Level"]
        foundation["hitter"] = "top" if foundation["hitter"] == "bottom" else "bottom"
    rows.append(second)
    converted = convert(rows)
    assert converted[0]["shots"][0]["player_id"] == converted[1]["shots"][0]["player_id"] == "Named server"
    assert converted[0]["shots"][0]["source_hitter"] == "bottom"
    assert converted[1]["shots"][0]["source_hitter"] == "top"
    assert len({s["annotation_id"] for rally in converted for s in rally["shots"]}) == 6


@pytest.mark.parametrize(
    "change,error",
    [
        ({"media_sha256": "b" * 64}, "media hash"),
        ({"expected_source_sha256": "b" * 64}, "annotation hash"),
        ({"fps_num": 30}, "fps"),
        ({"fps_den": True}, "fps"),
        ({"n_frames": 174}, "frame"),
        ({"width": 640}, "resolution"),
        ({"video_name": "0045.mp4"}, "video"),
        ({"source_revision": "main"}, "revision"),
        ({"media_sha256": "bad", "expected_media_sha256": "bad"}, "hash"),
    ],
)
def test_source_and_media_bindings_fail_closed(change, error):
    with pytest.raises(ValueError, match=error):
        convert(**change)


@pytest.mark.parametrize(
    "problem",
    [
        "duplicate_anchor",
        "anchor_at_end",
        "fractional_anchor",
        "bool_anchor",
        "wrong_duration",
        "missing_first_hit",
        "noncontiguous_hits",
        "duplicate_name",
        "unknown_name",
        "side_changes_within_rally",
        "two_names_same_side",
        "unknown_side",
        "bad_subtype",
    ],
)
def test_invalid_source_intervals_and_identity_are_rejected(problem):
    rows = source_rows()
    rally, hits = rows[0], rows[0]["hitting"]
    if problem == "duplicate_anchor":
        hits[1]["start_frame"] = 100
    elif problem == "anchor_at_end":
        hits[-1]["start_frame"] = 175
    elif problem == "fractional_anchor":
        hits[0]["start_frame"] = 100.5
    elif problem == "bool_anchor":
        hits[0]["start_frame"] = True
    elif problem == "wrong_duration":
        rally["duration_frames"] = 74
    elif problem == "missing_first_hit":
        hits.pop(0)
    elif problem == "noncontiguous_hits":
        hits[0]["end_frame"] = 124
    elif problem == "duplicate_name":
        rally["playerList"][1]["name"] = "Named server"
    elif problem == "unknown_name":
        hits[0]["player"] = "Another person"
    elif problem == "side_changes_within_rally":
        hits[-1]["Foundational Actions Level"]["hitter"] = "top"
    elif problem == "two_names_same_side":
        hits[1]["Foundational Actions Level"]["hitter"] = "bottom"
    elif problem == "unknown_side":
        hits[0]["Foundational Actions Level"]["hitter"] = "left"
    else:
        hits[0]["Foundational Actions Level"]["subtype"] = "short serve"
    with pytest.raises(ValueError):
        convert(rows)


def test_held_out_requires_explicit_reservation_and_never_promotes_import_review():
    with pytest.raises(ValueError, match="reserved"):
        convert(split="held_out")
    labels = convert(split="held_out", held_out_reserved_before_tuning=True)[0]
    assert labels["split"] == "held_out" and labels["status"] == "draft"
    assert labels["review"]["human_verified"] is False


def test_accepting_provider_review_records_its_scope_without_claiming_our_review():
    labels = convert(accept_published_review=True, split="held_out", held_out_reserved_before_tuning=True)[0]
    assert labels["status"] == "reviewed" and labels["split"] == "held_out"
    assert labels["review"]["human_verified"] is True
    assert labels["review"]["provider_human_verified"] is True
    assert labels["review"]["our_human_reviewed"] is False
    assert labels["review"]["origin"] == "published_human_refined_reference"
    assert labels["reference_provenance"]["dataset_revision"] == "72cae601e08c83ee8ec7e19f8fd7850e9158af7d"
    assert "2508.07554" in labels["review"]["publication"]


def test_cli_hashes_actual_media_writes_rally_files_and_refuses_overwrite(tmp_path):
    raw, kwargs = arguments()
    source, media, output = tmp_path / "source.json", tmp_path / "0044.mp4", tmp_path / "normalized"
    source.write_bytes(raw)
    media.write_bytes(b"synthetic media bytes")
    command = [
        sys.executable,
        "-m",
        "research.finebadminton_reference",
        "--source-json",
        str(source),
        "--media",
        str(media),
        "--video-name",
        "0044.mp4",
        "--session",
        "S1",
        "--expected-media-sha256",
        hashlib.sha256(media.read_bytes()).hexdigest(),
        "--expected-source-sha256",
        kwargs["expected_source_sha256"],
        "--fps-num",
        "25",
        "--fps-den",
        "1",
        "--n-frames",
        "250",
        "--width",
        "1280",
        "--height",
        "720",
        "--output-dir",
        str(output),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    assert completed.returncode == 0, completed.stderr
    manifest = json.loads(completed.stdout)
    assert len(manifest["files"]) == 1
    labels = json.loads((output / "0044-rally-0000.json").read_text())
    assert labels["shots"][1]["player_id"] == "Named receiver"
    assert labels["status"] == "draft" and labels["review"]["human_verified"] is False
    second = subprocess.run(command, capture_output=True, text=True, check=False)
    assert second.returncode != 0 and "exists" in second.stderr
    accepted_output = tmp_path / "accepted"
    command[-1] = str(accepted_output)
    accepted = subprocess.run(command + ["--accept-published-review"], capture_output=True, text=True, check=False)
    assert accepted.returncode == 0, accepted.stderr
    accepted_labels = json.loads((accepted_output / "0044-rally-0000.json").read_text())
    assert accepted_labels["status"] == "reviewed" and accepted_labels["review"]["human_verified"] is True
    assert accepted_labels["review"]["our_human_reviewed"] is False
