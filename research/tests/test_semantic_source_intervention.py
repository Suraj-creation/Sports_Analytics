"""Changed semantics require a complete, baseline-bound experiment declaration."""

from copy import deepcopy

import pytest

from research.production_external_semantic_replay import REPLAY_SCHEMA, require_source_intervention


def case():
    old = {"sports/badminton/src/rally.py": "old", "engine/src/host.py": "same"}
    new = {**old, "sports/badminton/src/rally.py": "new", "sports/badminton/src/policy.py": "added"}
    changes = {
        "sports/badminton/src/rally.py": {"recorded": "old", "current": "new"},
        "sports/badminton/src/policy.py": {"recorded": None, "current": "added"},
    }
    manifest = {
        "schema": "controlled-semantic-source-intervention:v1",
        "source_report_sha256": "report",
        "baseline_proof_sha256": "proof",
        "executed_source_sha256": new,
        "changes": changes,
        "hypothesis": "Typed insufficient contacts must not renew terminal activity.",
    }
    proof = {
        "schema": REPLAY_SCHEMA,
        "baseline_parity": True,
        "geometry_bracket": False,
        "contact_motion_reliability": False,
        "source_report_sha256": "report",
        "executed_source_sha256": old,
        "harness_source_sha256": {"verified-helper.py": "digest"},
    }
    args = {"report_sha": "report", "proof_sha": "proof", "current_sources": new, "recorded_sources": old}
    return manifest, proof, args


def test_declared_source_change_is_a_separate_experiment_not_baseline_parity():
    manifest, proof, args = case()
    assert require_source_intervention(manifest, proof, **args) == manifest["changes"]
    assert proof["baseline_parity"] is True  # original receipt remains unchanged


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema", "baseline"),
        ("source_report_sha256", "another-video"),
        ("baseline_proof_sha256", "other-proof"),
        ("executed_source_sha256", {}),
        ("changes", {}),
        ("hypothesis", ""),
    ],
)
def test_incomplete_or_cross_run_intervention_fails(field, value):
    manifest, proof, args = case()
    manifest[field] = value
    with pytest.raises(ValueError, match="complete declared"):
        require_source_intervention(manifest, proof, **args)


@pytest.mark.parametrize(
    "field,value",
    [
        ("baseline_parity", False),
        ("geometry_bracket", True),
        ("contact_motion_reliability", True),
        ("source_intervention", {"another": "experiment"}),
        ("source_report_sha256", "other-report"),
        ("executed_source_sha256", {"sports/badminton/src/rally.py": "changed"}),
        ("harness_source_sha256", {}),
    ],
)
def test_experimental_or_unbound_proof_cannot_authorize_another_experiment(field, value):
    manifest, proof, args = case()
    proof[field] = value
    with pytest.raises(ValueError, match="strict baseline"):
        require_source_intervention(manifest, proof, **args)


def test_unlisted_extra_source_change_is_rejected():
    manifest, proof, args = case()
    args = deepcopy(args)
    args["current_sources"]["engine/src/host.py"] = "unexpected"
    with pytest.raises(ValueError, match="complete declared"):
        require_source_intervention(manifest, proof, **args)


@pytest.mark.parametrize(
    "options",
    [{"min_duration_s": 0.1}, {"use_short_exchange_evidence": 1}, {"use_terminal_contact_evidence": "yes"}],
)
def test_undeclared_numerical_tuning_or_nonboolean_policy_is_rejected(options):
    manifest, proof, args = case()
    manifest["rally_evidence_options"] = options
    with pytest.raises(ValueError, match="boolean evidence"):
        require_source_intervention(manifest, proof, **args)
