"""Compatibility uses native evidence, preserving legacy numeric coverage."""

import importlib.util
import os
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import msgpack
import numpy as np
import pytest

TOOL_ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "explicit_test_scene_epoch_v3", TOOL_ROOT / "research/scene_epoch_audit_v3.py"
)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def frame(index, *, epoch=0, raw=False, decision=None):
    return {
        "f": index,
        "ce": epoch,
        "cc": {"hypothesis": raw, "status": "measured"},
        "cd": decision,
        "p": [],
        "do": True,
        "cs": "VALID",
        "v": "main",
        "r": False,
        "g": np.eye(3).ravel().tolist(),
        "s": None,
    }


def typed_stub(packet):
    return SimpleNamespace(
        frames=[
            SimpleNamespace(
                frame_idx=f["f"],
                content_change=SimpleNamespace(hypothesis=f["cc"]["hypothesis"]) if f.get("cc") else None,
                content_decision=SimpleNamespace(**f["cd"]) if f.get("cd") else None,
            )
            for f in packet["frames"]
        ]
    )


def packet(frames):
    return {
        "v": 23,
        "start": frames[0]["f"],
        "end": frames[-1]["f"],
        "frames": frames,
        "ci": {"layout_format_context": {"match_format": "singles", "confirmed": True}},
    }


def weak_pair():
    previous = frame(0)
    current = frame(1, epoch=1)
    current["cc"]["version"] = "foreground-scene-hypothesis:v4"
    current["cd"] = {
        "version": "detector-layout-scene-decision:v3",
        "decision": "barrier",
        "reason": "complete_layout",
        "raw_hypothesis": False,
        "previous_frame": 0,
        "previous_camera": previous["g"],
        "previous_to_current": current["g"],
        "expected_participants": 2,
        "detector_frame": 1,
    }
    return [packet([previous]), packet([current])]


def test_strong_unknown_fallback_and_raw_flags_exactly_match_original_counts():
    from research.pipeline_repair_run_analysis import audit_frames as original

    rows = [
        frame(0),
        frame(1, raw=True, decision={"decision": "no_barrier", "reason": "layout", "detector_frame": 1}),
        frame(2, epoch=1, raw=True, decision={"decision": "unknown", "reason": "fallback", "detector_frame": None}),
    ]
    expected = original(rows, 3)
    actual, csv_rows, proof = audit.audit_frames(rows, 3, packets=[packet(rows)], decode_packet=typed_stub)
    assert (actual, csv_rows) == expected
    assert proof["weak_barrier_frames"] == []
    assert actual["counts"]["scene_raw_hypotheses"] == 2


def test_positive_weak_reset_preserves_false_raw_flag_in_counts_and_csv():
    packets = weak_pair()
    frames = [f for p in packets for f in p["frames"]]
    report, csv_rows, proof = audit.audit_frames(frames, 2, packets=packets, decode_packet=typed_stub)
    assert proof["weak_barrier_frames"] == [1] and proof["cross_chunk_camera_proof_frames"] == [1]
    assert report["counts"]["scene_raw_hypotheses"] == 0
    assert report["counts"]["actual_content_epoch_increments"] == 1
    assert csv_rows[1][7] is False and csv_rows[1][8] is True


@pytest.mark.parametrize(
    "change",
    [
        "missing",
        "unknown",
        "no_barrier",
        "downgrade",
        "missing_epoch",
        "wrong_previous",
        "forged_previous",
        "invalid_previous",
        "wrong_relative",
        "unknown_format",
        "unconfirmed",
    ],
)
def test_weak_reset_requires_positive_typed_source_bound_authority(change):
    packets = weak_pair()
    f = packets[1]["frames"][0]
    if change == "missing":
        f["cd"] = None
    elif change in {"unknown", "no_barrier"}:
        f["cd"]["decision"] = change
    elif change == "downgrade":
        packets[1]["v"] = 22
    elif change == "missing_epoch":
        f["ce"] = 0
    elif change == "wrong_previous":
        f["cd"]["previous_frame"] = -1
    elif change == "forged_previous":
        f["cd"]["previous_camera"] = [1.0, 0, 3, 0, 1, 0, 0, 0, 1]
    elif change == "invalid_previous":
        packets[0]["frames"][0]["cs"] = "LOST"
    elif change == "wrong_relative":
        f["cd"]["previous_to_current"] = [1.0, 0, 3, 0, 1, 0, 0, 0, 1]
    elif change == "unknown_format":
        packets[1]["ci"]["layout_format_context"]["match_format"] = "unknown"
    elif change == "unconfirmed":
        packets[1]["ci"]["layout_format_context"]["confirmed"] = False
    with pytest.raises(ValueError):
        audit.audit_frames([f for p in packets for f in p["frames"]], 2, packets=packets, decode_packet=typed_stub)


def test_decoder_rejection_cannot_be_replaced_by_wire_flags():
    packets = weak_pair()

    def reject(_):
        raise ValueError("native proof rejected")

    with pytest.raises(ValueError, match="native proof rejected"):
        audit.audit_frames([f for p in packets for f in p["frames"]], 2, packets=packets, decode_packet=reject)


def test_audited_rows_cannot_differ_from_native_packet_population():
    packets = weak_pair()
    frames = deepcopy([f for p in packets for f in p["frames"]])
    frames[1]["p"] = [{"b": [0, 0, 1, 1]}]
    with pytest.raises(ValueError, match="population"):
        audit.audit_frames(frames, 2, packets=packets, decode_packet=typed_stub)


@pytest.fixture(scope="module")
def actual_native_prefix():
    run = os.environ.get("SCENE_AUDIT_ACTUAL_RUN")
    producer = os.environ.get("SCENE_AUDIT_PRODUCER_ROOT")
    if not run or not producer:
        pytest.skip("Explicit source-bound completed-NN integration fixture required")
    import research.pipeline_repair_run_analysis as original
    from bai_badminton.plugin import BadmintonSession

    producer = Path(producer).resolve()
    run = Path(run)
    assert original.ROOT.resolve() == producer
    bound = original.load_analysis_input(run, None)
    assert bound["completion_mode"] == "normal_completed_worker"
    plan = original.read(Path(bound["plan_path"]))
    assert all(original.sha(Path(p)) == h for p, h in plan["source_files_sha256"].items())
    paths = sorted(Path(bound["cache_dir"]).glob("*.msgpack"))[:6]
    packets = []
    for p in paths:
        assert original.sha(p) == bound["cache_sha256"][p.name]
        packets.append(msgpack.unpackb(p.read_bytes(), raw=False))

    def decode(p):
        receiver = SimpleNamespace(perception=SimpleNamespace(ref_id=p["cr"]), _isolation_id=lambda: p["ci"])
        return BadmintonSession.decode_perception(receiver, msgpack.packb(p, use_bin_type=True), diagnostic=True)

    return original, packets, decode


def test_actual_native_Test2_first_weak_355_is_genuine_RED_then_GREEN(actual_native_prefix):
    original, packets, decode = actual_native_prefix
    frames = [f for p in packets for f in p["frames"]]
    assert len(frames) == 360
    with pytest.raises(ValueError, match="lacks raw source hypothesis"):
        original.audit_frames(frames, 360)
    report, csv_rows, proof = audit.audit_frames(frames, 360, packets=packets, decode_packet=decode)
    assert proof["weak_barrier_frames"] == [355]
    assert csv_rows[355][7] is False and csv_rows[355][8] is True
    assert report["scene_records"][-1]["raw_hypothesis"] is False


@pytest.mark.parametrize(
    "change", ["missing", "downgrade", "unknown", "no_barrier", "cohort", "polygon", "camera", "format", "epoch"]
)
def test_actual_native_Test2_weakproof_mutations_rejected(actual_native_prefix, change):
    _, original, decode = actual_native_prefix
    packets = deepcopy(original)
    p = packets[-1]
    f = p["frames"][55]
    assert f["f"] == 355
    if change == "missing":
        f["cd"] = None
    elif change == "downgrade":
        p["v"] = 22
    elif change in {"unknown", "no_barrier"}:
        f["cd"]["decision"] = change
    elif change == "cohort":
        f["cc"]["acquisition_region_keys"] = []
    elif change == "polygon":
        f["cd"]["court_polygon"][0][0] += 1
    elif change == "camera":
        f["cd"]["previous_to_current"][2] += 1
    elif change == "format":
        p["ci"]["layout_format_context"]["confirmed"] = False
    elif change == "epoch":
        for row in p["frames"][55:]:
            row["ce"] -= 1
    with pytest.raises(ValueError):
        audit.audit_frames([f for p in packets for f in p["frames"]], 360, packets=packets, decode_packet=decode)


def adapter_module():
    spec = importlib.util.spec_from_file_location(
        "explicit_test_native_adapter",
        TOOL_ROOT / "evaluation/ground_truth_validation/orchestration/analyse_native_completed_run.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module



def _normalize_original_component_audit_body(nodes):
    """Normalize only the exact declared structural dispatch, never its math."""
    import ast

    expected_import = ast.parse(
        "from research.scene_epoch_audit_v3 import audit_completed_component_frames"
    ).body[0]
    expected_dispatch = ast.parse(
        "coverage, _ = audit_completed_component_frames("
        "frames, n, packets=chunks, consumed=consumed, producer_root=ROOT) "
        "if any(chunk['v'] >= 24 for chunk in chunks) else audit_frames(frames, n)"
    ).body[0]
    expected_source_copy = ast.parse(
        "shutil.copyfile(Path(__file__), output / 'executed_analysis_source.py')"
    ).body[0]
    expected_snapshot = ast.parse("snapshot_execution_sources(output, provenance)").body[0]
    output = []
    for node in nodes:
        if ast.dump(node) in {ast.dump(expected_source_copy), ast.dump(expected_snapshot)}:
            continue
        if isinstance(node, ast.ImportFrom) and node.module == "research.scene_epoch_audit_v3":
            assert ast.dump(node) == ast.dump(expected_import), "Unexpected structural import"
            continue
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Tuple)
            and [item.id for item in node.targets[0].elts] == ["coverage", "_"]
            and isinstance(node.value, ast.IfExp)
        ):
            assert ast.dump(node) == ast.dump(expected_dispatch), "Unexpected structural dispatch"
            node = ast.parse("coverage, _ = audit_frames(frames, n)").body[0]
        output.append(node)
    return output


def test_structural_AST_normalization_rejects_numeric_dispatch_mutation():
    import ast

    forged = ast.parse(
        "coverage, _ = audit_completed_component_frames("
        "frames, n + 1, packets=chunks, consumed=consumed, producer_root=ROOT) "
        "if any(chunk['v'] >= 24 for chunk in chunks) else audit_frames(frames, n)"
    ).body
    with pytest.raises(AssertionError, match="Unexpected structural dispatch"):
        _normalize_original_component_audit_body(forged)



def test_structural_AST_normalization_keeps_nonprovenance_file_operations():
    import ast

    numeric_output = ast.parse("shutil.copyfile(Path(__file__), output / 'technical_analysis.json')").body
    normalized = _normalize_original_component_audit_body(numeric_output)
    assert ast.dump(normalized[0]) == ast.dump(numeric_output[0])


def normalized_assembly(function, original):
    """Only declare structural proof/provenance additions; all numeric AST exact."""
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(function)).body[0]
    old = ast.parse(inspect.getsource(original)).body[0]
    old.body = _normalize_original_component_audit_body(old.body)
    if original.__name__ == "analyse":
        start = next(
            i
            for i, n in enumerate(tree.body)
            if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "bound"
        )
    else:
        start = next(
            i
            for i, n in enumerate(tree.body)
            if isinstance(n, ast.Assign)
            and isinstance(n.targets[0], ast.Tuple)
            and [x.id for x in n.targets[0].elts] == ["run", "output"]
        )
    body = []
    for n in tree.body[start:]:
        text = ast.unparse(n)
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Tuple):
            names = [x.id for x in n.targets[0].elts]
            if names == ["frame_report", "csv_rows", "structural_proof"]:
                body.append(ast.parse("frame_report, csv_rows = audit_frames(frames, n)").body[0])
                continue
            if names == ["coverage", "_", "structural_proof"]:
                body.append(ast.parse("coverage, _ = audit_frames(frames, n)").body[0])
                continue
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "plan":
            continue
        if isinstance(n, ast.For) and (
            "provenance" in ast.unparse(n.iter) or ast.unparse(n.iter).startswith("plan['source_files_sha256']")
        ):
            continue
        if isinstance(n, ast.Expr) and (
            text.startswith("require_recorded_producer(")
            or text.startswith("consumed.update(provenance['source_sha256'])")
            or "structural_compatibility_receipt.json" in text
        ):
            continue
        body.append(n)
    tree.body = _normalize_original_component_audit_body(body)

    class ExplicitNativeNames(ast.NodeTransformer):
        def visit_Attribute(self, node):
            if isinstance(node.value, ast.Name) and node.value.id in {"original", "components"}:
                return ast.copy_location(ast.Name(id=node.attr, ctx=node.ctx), node)
            return self.generic_visit(node)

        def visit_Dict(self, node):
            selected = [
                (k, v)
                for k, v in zip(node.keys, node.values, strict=True)
                if not isinstance(k, ast.Constant) or k.value != "structural_compatibility"
            ]
            node.keys = [k for k, _ in selected]
            node.values = [v for _, v in selected]
            return self.generic_visit(node)

    tree = ExplicitNativeNames().visit(tree)
    tree.name = old.name
    tree.args = old.args
    return ast.dump(tree, include_attributes=False), ast.dump(old, include_attributes=False)


def test_transparent_analysis_assembly_has_exact_original_numeric_AST():
    import research.pipeline_repair_run_analysis as original

    new, old = normalized_assembly(adapter_module().analyse_native_completed_run, original.analyse)
    assert new == old


def test_transparent_component_assembly_has_exact_original_numeric_AST():
    from evaluation.ground_truth_validation.orchestration.evaluate_test02_components import evaluate_components

    new, old = normalized_assembly(adapter_module().evaluate_native_components, evaluate_components)
    assert new == old


def test_plan_producer_mismatch_rejects_before_using_unrelated_source(tmp_path):
    import json

    p = tmp_path / "plan.json"
    p.write_text(json.dumps({"root": str(tmp_path / "protocol"), "source_files_sha256": {}}))
    run = tmp_path / "run"
    run.mkdir()
    (tmp_path / "run.executor.json").write_text(json.dumps({"command": ["python", str(tmp_path / "other/worker.py")]}))
    original = SimpleNamespace(read=lambda p: json.loads(p.read_text()))
    with pytest.raises(ValueError, match="producer differs"):
        adapter_module().require_recorded_producer(
            {"plan_path": str(p), "receipt_path": str(run / "inference.json")}, tmp_path / "producer", original
        )
