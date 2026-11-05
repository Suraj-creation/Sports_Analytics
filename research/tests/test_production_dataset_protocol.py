import copy
import hashlib
import json

import pytest

from research.production_dataset_protocol import freeze, validate_protocol


def protocol():
    return {
        "schema_version": 1,
        "protocol_id": "synthetic-contract",
        "intervals": "half_open",
        "metric_policy": {"rally_minimum_iou": 0.5},
        "recordings": [
            {
                "recording_id": "held",
                "source_sha256": "1" * 64,
                "match_id": "match-one",
                "split": "held_out",
                "match_identity_reviewed": True,
                "media_use_authorized": True,
                "annotation_use_authorized": True,
                "exposure": "none",
            }
        ],
    }


def history():
    return {"schema_version": 1, "records": []}


@pytest.mark.parametrize("alias", ["source_sha256", "match_id"])
def test_match_and_content_aliases_cannot_cross_heldout_partition(alias):
    data = protocol()
    other = {
        "recording_id": "different-clip-name",
        "source_sha256": "2" * 64,
        "match_id": "match-two",
        "split": "development",
    }
    other[alias] = data["recordings"][0][alias]
    data["recordings"].append(other)
    with pytest.raises(ValueError, match="crosses held-out"):
        validate_protocol(data, history())


def test_exposed_historical_holdout_is_not_a_new_blind_holdout():
    old = history()
    old["records"].append({"source_sha256": "1" * 64, "exposure": "historical_predictions_seen"})
    with pytest.raises(ValueError, match="history prevents"):
        validate_protocol(protocol(), old)


@pytest.mark.parametrize(
    "field,value",
    [
        ("match_identity_reviewed", False),
        ("match_id", None),
        ("source_sha256", None),
        ("media_use_authorized", False),
        ("annotation_use_authorized", False),
        ("exposure", "tuning"),
    ],
)
def test_pending_identity_rights_or_exposure_gates_block_blind_status(field, value):
    data = protocol()
    data["recordings"][0][field] = value
    with pytest.raises(ValueError):
        validate_protocol(data, history())


def test_unidentified_candidates_can_be_quarantined_without_accuracy_claim():
    data = protocol()
    data["recordings"][0] = {
        "recording_id": "candidate",
        "source_sha256": None,
        "match_id": None,
        "split": "quarantined",
    }
    result = validate_protocol(data, history())
    assert result["quarantined_ids"] == ["candidate"]
    assert result["prospective_held_out_ids"] == []
    assert result["accuracy_claim_eligible"] is False


def test_freeze_snapshots_exact_inputs_and_never_opens_declared_media(tmp_path):
    data = protocol()
    data["recordings"][0]["media_path"] = str(tmp_path / "deliberately_nonexistent_video.mp4")
    pp, hp, output = tmp_path / "protocol.json", tmp_path / "history.json", tmp_path / "frozen"
    pp.write_text(json.dumps(data))
    hp.write_text(json.dumps(history()))
    before = copy.deepcopy(data)
    result = freeze(pp, hp, output)
    assert data == before
    assert (output / "protocol.json").read_bytes() == pp.read_bytes()
    assert hashlib.sha256((output / "executed_protocol_tool.py").read_bytes()).hexdigest() == result["tool_sha256"]
    assert result["media_or_label_contents_accessed"] is False
    assert result["accuracy_claim_eligible"] is False
    with pytest.raises(FileExistsError):
        freeze(pp, hp, output)
