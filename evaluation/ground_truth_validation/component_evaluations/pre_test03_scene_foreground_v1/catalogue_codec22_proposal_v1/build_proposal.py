"""Create an unapplied schema-only patch; canonical and candidate stay read-only."""

import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
CANDIDATE = ROOT.parent / "test03-scene-continuity-20261112"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    names = [
        "research/production_external_stress.py",
        "research/pipeline_repair_completion.py",
        "research/normal_timestamp_audit.py",
    ]
    bases = {name: (ROOT / name).read_text() for name in names}
    assert all((CANDIDATE / name).read_text() == text for name, text in bases.items())
    proposed = dict(bases)
    stress = bases[names[0]].replace(
        '"accepted_codec_versions": [20, 21],', '"accepted_codec_versions": [20, 21, 22],', 1
    )
    stress = stress.replace('if value["v"] == 21:', 'if value["v"] in (21, 22):', 1)
    start = stress.index("    # Older published catalogues recorded the narrower codec20-only policy.")
    end = stress.index("    if recorded != observed", start)
    stress = (
        stress[:start]
        + """    # Preserve a published acceptance policy only when the observed population
    # actually fits it. Every other limit, header, byte hash and receipt is exact.
    for historical_versions in ([20], [20, 21]):
        historical_limits = {**PERCEPTION_CATALOG_LIMITS, "accepted_codec_versions": historical_versions}
        if (
            isinstance(recorded, dict)
            and recorded.get("schema") == PERCEPTION_CATALOG_SCHEMA
            and recorded.get("limits") == historical_limits
            and all(row["codec_version"] in historical_versions for row in observed["files"])
        ):
            observed["limits"]["accepted_codec_versions"] = historical_versions
            break
"""
        + stress[end:]
    )
    proposed[names[0]] = stress
    completion = bases[names[1]]
    start = completion.index("def validate_cache21(payload, profile, media):")
    end = completion.index("\n\ndef cache_catalog(", start)
    body = completion[start:end]
    body = body.replace(
        "def validate_cache21(payload, profile, media):",
        'def _validate_cache_context(payload, profile, media, *, accepted_versions=(21,), context_label="codec21"):',
    )
    body = body.replace('value.get("v") != 21', 'value.get("v") not in accepted_versions', 1)
    body = body.replace(
        'raise ValueError("codec21 source profile/model/media identity mismatch")',
        'raise ValueError(f"{context_label} source profile/model/media identity mismatch")',
        1,
    )
    body += '''

def validate_cache21(payload, profile, media):
    """Historical recovery contract stays strictly codec21, without header rewriting."""
    return _validate_cache_context(payload, profile, media, accepted_versions=(21,))


def validate_completed_cache(payload, profile, media):
    """Normal completed-run schema validation; no recovery or neural execution."""
    return _validate_cache_context(
        payload, profile, media, accepted_versions=(21, 22), context_label="completed codec21/22"
    )
'''
    proposed[names[1]] = completion[:start] + body + completion[end:]
    proposed[names[2]] = (
        bases[names[2]]
        .replace(
            "decode_source_pts, validate_cache21, verify_proxy",
            "decode_source_pts, validate_completed_cache, verify_proxy",
            1,
        )
        .replace(
            "validate_cache21(data, bound.profile, bound.media)",
            "validate_completed_cache(data, bound.profile, bound.media)",
            1,
        )
    )
    patch, hashes = [], {}
    for name in names:
        for directory, text in (("original_sources", bases[name]), ("proposed_sources", proposed[name])):
            p = HERE / directory / name
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("x") as stream:
                stream.write(text)
        hashes[name] = {"original_sha256": sha(bases[name].encode()), "proposed_sha256": sha(proposed[name].encode())}
        patch += difflib.unified_diff(
            bases[name].splitlines(True), proposed[name].splitlines(True), fromfile="a/" + name, tofile="b/" + name
        )
    with (HERE / "schema_only_codec22.patch").open("x") as stream:
        stream.write("".join(patch))
    assert all(
        (ROOT / name).read_text() == text and (CANDIDATE / name).read_text() == text for name, text in bases.items()
    )
    with (HERE / "proposal_source_bindings.json").open("x") as stream:
        json.dump(
            {
                "schema": "unapplied-codec22-schema-proposal:v1",
                "applied": False,
                "files": hashes,
                "candidate_source_commit": "7ed2f731e2d58273e381710226500f30d47e00bb",
                "numeric_metrics_matching_thresholds_changed": False,
                "canonical_and_candidate_unchanged": True,
            },
            stream,
            indent=2,
        )
        stream.write("\n")
    print("Unapplied proposal written; three original/candidate source files remain byte-identical.")


if __name__ == "__main__":
    main()
