"""Freeze reviewed metadata and split rules without opening media or labels.

This is a companion to the existing shot/tracking/participant/reference
evaluators. Metadata consistency is not verified sporting accuracy, rights or
human review. New blind evaluation cannot reuse previously exposed recordings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SHA256 = re.compile(r"[0-9a-f]{64}")
SPLITS = {"development", "historical_evaluation", "held_out", "quarantined"}


def validate_protocol(protocol: dict, exposure_history: dict) -> dict:
    if protocol.get("schema_version") != 1 or exposure_history.get("schema_version") != 1:
        raise ValueError("unsupported protocol or exposure-history schema")
    if not isinstance(protocol.get("protocol_id"), str) or not protocol["protocol_id"].strip():
        raise ValueError("a protocol identity is required")
    if protocol.get("intervals") != "half_open" or not isinstance(protocol.get("metric_policy"), dict):
        raise ValueError("declare half-open intervals and a frozen metric policy")
    records = protocol.get("recordings")
    if not isinstance(records, list) or not records:
        raise ValueError("recording metadata must be nonempty")
    history = exposure_history.get("records")
    if not isinstance(history, list) or any(not isinstance(row, dict) for row in history):
        raise ValueError("exposure history must be explicit, including an empty list when truly unknown")
    ids, groups, matches_by_hash = set(), {}, {}
    held_out = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("recording entries must be objects")
        identity, split = record.get("recording_id"), record.get("split")
        if not isinstance(identity, str) or not identity.strip() or identity in ids:
            raise ValueError("recording identities must be nonempty and unique")
        ids.add(identity)
        if split not in SPLITS:
            raise ValueError(f"{identity}: unknown split")
        source_hash, match = record.get("source_sha256"), record.get("match_id")
        if source_hash is not None and (not isinstance(source_hash, str) or not SHA256.fullmatch(source_hash)):
            raise ValueError(f"{identity}: invalid source digest")
        if match is not None and (not isinstance(match, str) or not match.strip()):
            raise ValueError(f"{identity}: invalid match identity")
        for key in (("recording", identity), ("hash", source_hash), ("match", match)):
            if key[1] is not None:
                groups.setdefault(key, set()).add(split)
        if source_hash and match:
            matches_by_hash.setdefault(source_hash, set()).add(match)
        if split != "held_out":
            continue
        if not source_hash or not match or record.get("match_identity_reviewed") is not True:
            raise ValueError(f"{identity}: held-out match/source identity review is missing")
        if record.get("media_use_authorized") is not True or record.get("annotation_use_authorized") is not True:
            raise ValueError(f"{identity}: held-out use authorization is missing")
        if record.get("exposure") != "none":
            raise ValueError(f"{identity}: previously exposed material is not a new blind holdout")
        for prior in history:
            same = (
                prior.get("recording_id") == identity
                or (source_hash and prior.get("source_sha256") == source_hash)
                or (match and prior.get("match_id") == match)
            )
            if same and prior.get("exposure") != "none":
                raise ValueError(f"{identity}: exposure history prevents new blind status")
        held_out.append(identity)
    if any("held_out" in splits and len(splits) > 1 for splits in groups.values()):
        raise ValueError("the same recording, content hash or match crosses held-out and exposed splits")
    if any(len(matches) > 1 for matches in matches_by_hash.values()):
        raise ValueError("one source digest has contradictory match identities")
    return {
        "metadata_contract_passed": True,
        "recording_count": len(records),
        "prospective_held_out_ids": held_out,
        "quarantined_ids": [r["recording_id"] for r in records if r["split"] == "quarantined"],
        "accuracy_claim_eligible": False,
        "media_or_label_contents_accessed": False,
        "limits": [
            "Identity, exposure, authorization and review fields are attestations, not independently verified facts.",
            "Actual source/proxy/label hashes, canonical mapping, exhaustive review and component support "
            "remain gates.",
            "No predictions, labels, inference or evaluator results are created by freezing metadata.",
            "Model training overlap remains a separate unknown unless independently established.",
        ],
    }


def freeze(protocol_path: Path, history_path: Path, output: Path) -> dict:
    if output.exists():
        raise FileExistsError(f"refusing existing output {output}")
    protocol_bytes, history_bytes = protocol_path.read_bytes(), history_path.read_bytes()
    tool_bytes = Path(__file__).read_bytes()
    result = validate_protocol(json.loads(protocol_bytes), json.loads(history_bytes))
    result.update(
        status="frozen_metadata_only",
        protocol_sha256=hashlib.sha256(protocol_bytes).hexdigest(),
        exposure_history_sha256=hashlib.sha256(history_bytes).hexdigest(),
        tool_sha256=hashlib.sha256(tool_bytes).hexdigest(),
    )
    output.mkdir(parents=True, exist_ok=False)
    for name, data in (
        ("protocol.json", protocol_bytes),
        ("exposure_history.json", history_bytes),
        ("executed_protocol_tool.py", tool_bytes),
    ):
        with (output / name).open("xb") as stream:
            stream.write(data)
    (output / "freeze.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--exposure-history", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(freeze(args.protocol.resolve(), args.exposure_history.resolve(), args.output.resolve()), indent=2))


if __name__ == "__main__":
    main()
