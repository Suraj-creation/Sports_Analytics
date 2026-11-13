"""Same-native-root structural integration; controlled proofs are not model runs."""

import ast
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from evaluation.ground_truth_validation.orchestration import evaluate_manifest_components as m
from research import scene_epoch_audit_v3 as auditor

HERE = Path(__file__).resolve().parent


def controlled_packets():
    previous = {
        "f": 0,
        "ce": 0,
        "cc": None,
        "cd": None,
        "p": [],
        "do": True,
        "g": np.eye(3).ravel().tolist(),
        "cs": "VALID",
        "v": "main",
        "r": False,
        "s": None,
    }
    current = deepcopy(previous)
    current.update(f=1, ce=1)
    current["cc"] = {"version": "foreground-scene-hypothesis:v4", "hypothesis": False, "status": "measured"}
    current["cd"] = {
        "version": "detector-layout-scene-decision:v3",
        "raw_hypothesis": False,
        "decision": "barrier",
        "reason": "controlled_positive",
        "previous_frame": 0,
        "previous_camera": previous["g"],
        "previous_to_current": current["g"],
        "expected_participants": 2,
        "detector_frame": 1,
    }
    return [
        {
            "v": 23,
            "start": f["f"],
            "end": f["f"],
            "frames": [f],
            "ci": {"layout_format_context": {"match_format": "singles", "confirmed": True}},
        }
        for f in (previous, current)
    ]


def typed_control(packet):
    return SimpleNamespace(
        frames=[
            SimpleNamespace(
                frame_idx=f["f"],
                content_change=SimpleNamespace(hypothesis=f["cc"]["hypothesis"]) if f["cc"] else None,
                content_decision=SimpleNamespace(**f["cd"]) if f["cd"] else None,
            )
            for f in packet["frames"]
        ]
    )


def controlled_interfaces(monkeypatch, **change):
    provenance = {"producer_root": str(m.ROOT), "tool_root": str(m.ROOT), "source_sha256": {}}
    provenance.update(change.get("provenance", {}))
    original = change.get("original", m.analysis)

    def bridge(producer_root, tool_root):
        assert producer_root == tool_root == m.ROOT
        return original, auditor, change.get("decoder", typed_control), provenance

    monkeypatch.setattr(m, "load_native_interfaces", bridge)


def test_same_native_interface_keeps_weak_raw_flag_and_source_proof(monkeypatch):
    controlled_interfaces(monkeypatch)
    packets = controlled_packets()
    frames = [f for p in packets for f in p["frames"]]
    coverage, provenance = m.native_scene_coverage(frames, packets, 2)
    assert coverage["counts"]["scene_raw_hypotheses"] == 0
    assert coverage["counts"]["actual_content_epoch_increments"] == 1
    assert provenance["scene_epoch_proof"]["weak_barrier_frames"] == [1]
    assert provenance["scene_epoch_proof"]["cross_chunk_camera_proof_frames"] == [1]


@pytest.mark.parametrize("damage", ["module_identity", "producer", "tool"])
def test_foreign_native_audit_interface_rejected_before_decoder(monkeypatch, damage):
    changes = {"decoder": lambda _: pytest.fail("Foreign-root decoder must not execute")}
    if damage == "module_identity":
        changes["original"] = SimpleNamespace(ROOT=m.ROOT, __file__=m.analysis.__file__)
    else:
        changes["provenance"] = {damage + "_root": "/foreign"}
    controlled_interfaces(monkeypatch, **changes)
    with pytest.raises(ValueError, match="native root"):
        m.native_scene_coverage([], [], 0)


@pytest.mark.parametrize(
    "damage",
    [
        "missing",
        "unknown",
        "no_barrier",
        "downgrade",
        "missing_epoch",
        "previous_camera",
        "relative_camera",
        "unconfirmed_format",
    ],
)
def test_structural_proof_failure_not_replaced_by_coverage_counts(monkeypatch, damage):
    controlled_interfaces(monkeypatch)
    packets = controlled_packets()
    p = packets[1]
    f = p["frames"][0]
    if damage == "missing":
        f["cd"] = None
    elif damage in {"unknown", "no_barrier"}:
        f["cd"]["decision"] = damage
    elif damage == "downgrade":
        p["v"] = 22
    elif damage == "missing_epoch":
        f["ce"] = 0
    elif damage == "previous_camera":
        f["cd"]["previous_camera"] = [1.0, 0, 3, 0, 1, 0, 0, 0, 1]
    elif damage == "relative_camera":
        f["cd"]["previous_to_current"] = [1.0, 0, 3, 0, 1, 0, 0, 0, 1]
    elif damage == "unconfirmed_format":
        p["ci"]["layout_format_context"]["confirmed"] = False
    with pytest.raises(ValueError):
        m.native_scene_coverage([f for p in packets for f in p["frames"]], packets, 2)


def test_native_decoder_failure_is_propagated_without_annotations(monkeypatch):
    def reject(_):
        raise ValueError("native source proof rejected")

    controlled_interfaces(monkeypatch, decoder=reject)
    packets = controlled_packets()
    with pytest.raises(ValueError, match="native source proof"):
        m.native_scene_coverage([f for p in packets for f in p["frames"]], packets, 2)


def test_legacy_strong_unknown_fallback_coverage_exactly_matches_original(monkeypatch):
    controlled_interfaces(monkeypatch)
    packets = controlled_packets()
    f = packets[1]["frames"][0]
    f["cc"] = {"hypothesis": True, "status": "hypothesis"}
    f["cd"] = {"decision": "unknown", "reason": "legacy_raw_fallback", "detector_frame": None, "raw_hypothesis": True}
    frames = [f for p in packets for f in p["frames"]]
    expected, _ = m.analysis.audit_frames(frames, 2)
    actual, provenance = m.native_scene_coverage(frames, packets, 2)
    assert actual == expected and provenance["scene_epoch_proof"]["weak_barrier_frames"] == []


def test_every_original_non_orchestrator_function_ast_is_unchanged():
    before = ast.parse((HERE / "before_evaluator.py").read_text())
    current = ast.parse(Path(m.__file__).read_text())
    functions = {n.name: n for n in current.body if isinstance(n, ast.FunctionDef)}
    for n in before.body:
        if isinstance(n, ast.FunctionDef) and n.name != "evaluate":
            assert ast.dump(functions[n.name], include_attributes=False) == ast.dump(n, include_attributes=False), (
                n.name
            )


def test_evaluate_ast_changes_only_structural_call_and_declared_provenance():
    before = next(
        n
        for n in ast.parse((HERE / "before_evaluator.py").read_text()).body
        if isinstance(n, ast.FunctionDef) and n.name == "evaluate"
    )
    current = next(
        n
        for n in ast.parse(Path(m.__file__).read_text()).body
        if isinstance(n, ast.FunctionDef) and n.name == "evaluate"
    )
    body = []
    for n in current.body:
        if (
            isinstance(n, ast.Assign)
            and isinstance(n.targets[0], ast.Tuple)
            and [x.id for x in n.targets[0].elts] == ["coverage", "structural_compatibility"]
        ):
            body.append(ast.parse('coverage, _ = analysis.audit_frames(frames, bound["media"]["n_frames"])').body[0])
            continue
        if isinstance(n, ast.Expr) and ast.unparse(n).startswith(
            "consumed.update(structural_compatibility['source_sha256'])"
        ):
            continue
        body.append(n)
    current.body = body

    class RemoveDeclaredProvenance(ast.NodeTransformer):
        def visit_Dict(self, node):
            selected = [
                (k, v)
                for k, v in zip(node.keys, node.values, strict=True)
                if not isinstance(k, ast.Constant) or k.value != "structural_compatibility"
            ]
            node.keys = [k for k, _ in selected]
            node.values = [v for _, v in selected]
            return self.generic_visit(node)

    current = RemoveDeclaredProvenance().visit(current)
    assert ast.dump(current, include_attributes=False) == ast.dump(before, include_attributes=False)


def test_actual_same_root_interface_records_auditor_source_without_root_patch():
    original, loaded, decoder, provenance = m.load_native_interfaces(m.ROOT, m.ROOT)
    assert original is m.analysis and original.ROOT == m.ROOT
    assert callable(decoder) and loaded.AUDIT_VERSION == "source-native-scene-epoch-audit:v3"
    assert provenance["native_ROOT_reassigned"] is False and provenance["native_globals_patched"] is False
    assert str(m.ROOT / "research/scene_epoch_audit_v3.py") in provenance["source_sha256"]
