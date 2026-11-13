"""Independent static/parity review; no producer imports, models or inference."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
MAIN = OUT.parents[4]
NATIVE = Path("/home/administrator/Desktop/sport-analytics/test03-scene-evidence-contract-20261112")
ART = Path("/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v4")


def sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def dump(name, data):
    with (OUT / name).open("x") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")


def function(path, name):
    return next(n for n in ast.parse(Path(path).read_text()).body if isinstance(n, ast.FunctionDef) and n.name == name)


def canonical(node):
    return ast.dump(node, include_attributes=False)


class ExplicitNativeNames(ast.NodeTransformer):
    def visit_Attribute(self, node):
        node = self.generic_visit(node)
        if isinstance(node.value, ast.Name) and node.value.id in {"original", "components"}:
            return ast.copy_location(ast.Name(id=node.attr, ctx=node.ctx), node)
        return node

    def visit_Dict(self, node):
        retained = [
            (k, v)
            for k, v in zip(node.keys, node.values, strict=True)
            if not isinstance(k, ast.Constant) or k.value != "structural_compatibility"
        ]
        node.keys, node.values = [k for k, _ in retained], [v for _, v in retained]
        return self.generic_visit(node)


def normalize_assembly(new, old, *, component):
    new, old = copy.deepcopy(new), copy.deepcopy(old)

    def marker(node):
        if component:
            return (
                isinstance(node, ast.Assign)
                and isinstance(node.targets[0], ast.Tuple)
                and [x.id for x in node.targets[0].elts] == ["run", "output"]
            )
        return isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "bound"

    start = next(i for i, n in enumerate(new.body) if marker(n))
    kept, excluded = [], []
    for node in new.body[start:]:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Tuple):
            targets = [n.id for n in node.targets[0].elts]
            if targets in (["frame_report", "csv_rows", "structural_proof"], ["coverage", "_", "structural_proof"]):
                replacement = (
                    "coverage, _ = audit_frames(frames, n)"
                    if component
                    else "frame_report, csv_rows = audit_frames(frames, n)"
                )
                kept.append(ast.parse(replacement).body[0])
                excluded.append("new native structural audit callback/proof return")
                continue
        text = ast.unparse(node)
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "plan":
            excluded.append("additional frozen-plan read")
            continue
        if isinstance(node, ast.For) and (
            "provenance" in ast.unparse(node.iter) or ast.unparse(node.iter).startswith("plan['source_files_sha256']")
        ):
            excluded.append("additional source/provenance hash binding loop")
            continue
        if isinstance(node, ast.Expr) and (
            text.startswith("require_recorded_producer(")
            or text.startswith("consumed.update(provenance['source_sha256'])")
            or "structural_compatibility_receipt.json" in text
        ):
            excluded.append("additional source check/provenance/compatibility receipt")
            continue
        kept.append(node)
    new.body = kept
    new = ExplicitNativeNames().visit(new)
    new.name, new.args = old.name, old.args
    assert canonical(new) == canonical(old)
    return {
        "equal": True,
        "normalized_AST_sha256": hashlib.sha256(canonical(old).encode()).hexdigest(),
        "declared_excluded_additions": excluded,
    }


def main():
    parity_path = OUT.parent / "implementation_parity_receipt.json"
    receipt = read(parity_path)
    sources = {}
    for path, digest in receipt["source_sha256"].items():
        assert sha(path) == digest, path
        sources[path] = digest
    tool_paths = [
        MAIN / "research/scene_epoch_audit_v3.py",
        MAIN / "evaluation/ground_truth_validation/orchestration/analyse_native_completed_run.py",
        MAIN / "evaluation/ground_truth_validation/orchestration/continue_native_test02_postprocessing.py",
        MAIN / "evaluation/ground_truth_validation/orchestration/export_native_completed_heatmaps.py",
        MAIN / "evaluation/ground_truth_validation/orchestration/run_pre_test03_regression.py",
    ]
    source_paths = [
        NATIVE / "research/pipeline_repair_run_analysis.py",
        NATIVE / "evaluation/ground_truth_validation/orchestration/evaluate_test02_components.py",
        NATIVE / "evaluation/ground_truth_validation/orchestration/export_test02_heatmaps.py",
        NATIVE / "sports/badminton/src/bai_badminton/plugin.py",
        NATIVE / "sports/badminton/src/bai_badminton/perception/content.py",
    ]
    for path in [*tool_paths, *source_paths]:
        sources[str(path)] = sha(path)
        destination = (
            OUT
            / "source_snapshots"
            / ("native" if path.is_relative_to(NATIVE) else "tool")
            / path.relative_to(NATIVE if path.is_relative_to(NATIVE) else MAIN)
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as stream:
            stream.write(path.read_bytes())
    native_analysis, adapter = source_paths[0], tool_paths[1]
    old = function(native_analysis, "audit_frames")
    new = function(tool_paths[0], "audit_frames")
    new.body = new.body[2:]
    for node in ast.walk(new):
        if (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.BoolOp)
            and len(node.test.values) == 3
            and (canonical(node.test.values[-1]) == canonical(ast.parse("f not in weak_barriers", mode="eval").body))
        ):
            node.test.values = node.test.values[:2]
    new.body[-1].value.elts = new.body[-1].value.elts[:2]
    assert [canonical(n) for n in new.body] == [canonical(n) for n in old.body]
    numeric = {
        "frame_counter_and_csv_body": {"exact_AST_after_declared_structural_changes": True},
        "technical_analysis_assembly": normalize_assembly(
            function(adapter, "analyse_native_completed_run"), function(native_analysis, "analyse"), component=False
        ),
        "Test2_component_assembly": normalize_assembly(
            function(adapter, "evaluate_native_components"),
            function(source_paths[1], "evaluate_components"),
            component=True,
        ),
    }
    old_heatmap = function(source_paths[2], "export")
    new_heatmap = function(tool_paths[3], "export")

    class HeatmapDependencies(ast.NodeTransformer):
        def visit_Name(self, node):
            names = {
                "media_spec": "MEDIA",
                "source_sha": "TEST2_SHA",
                "event_class": "Event",
                "event_store": "EventStore",
                "track_store": "TrackStore",
            }
            return ast.copy_location(ast.Name(id=names.get(node.id, node.id), ctx=node.ctx), node)

    new_heatmap = HeatmapDependencies().visit(new_heatmap)
    old_try = next(n for n in old_heatmap.body if isinstance(n, ast.Try))
    new_try = next(n for n in new_heatmap.body if isinstance(n, ast.Try))
    assert canonical(old_try) == canonical(new_try)
    numeric["canonical_heatmap_rebuild_result_and_private_close"] = {"AST_equal_after_dependency_alias_renaming": True}
    old_report = read(receipt["original_Test1_report"])
    new_report = read(receipt["new_Test1_report"])
    assert set(new_report) - set(old_report) == {"structural_compatibility"}
    assert all(new_report[k] == v for k, v in old_report.items() if k != "consumed_files_sha256")
    assert all(new_report["consumed_files_sha256"][p] == h for p, h in old_report["consumed_files_sha256"].items())
    old_csv = Path(receipt["original_Test1_report"]).parent / "frame_component_coverage.csv"
    new_csv = Path(receipt["new_Test1_report"]).parent / "frame_component_coverage.csv"
    assert old_csv.read_bytes() == new_csv.read_bytes()
    native_components_path = ART / "audit_compat_validation_v3/test02_components/component_reference_metrics.json"
    component_metrics = read(native_components_path)
    assert component_metrics["all_annotation_files_accounted_for"] is True
    assert component_metrics["annotations_modified"] is False
    assert len(component_metrics["interval_reference_comparisons"]) == 3
    assert all(v["value"] is None for v in component_metrics["unsupported_metrics"].values())
    structural = component_metrics["structural_compatibility"]["scene_epoch_proof"]
    assert structural["native_decoded_frames"] == 29296 and structural["native_decoded_packets"] == 489
    assert structural["weak_barrier_frames"] == [355, 699, 1095, 3394, 4581, 5958, 11691, 11985, 25521]
    checks = {
        "Test1_numeric_original_fields_exact": True,
        "Test1_frame_CSV_byte_identical": True,
        "Test1_original_consumed_hashes_preserved": len(old_report["consumed_files_sha256"]),
        "Test1_new_consumed_hashes": len(new_report["consumed_files_sha256"]),
        "Test2_annotation_roles": len(component_metrics["annotation_applicability"]),
        "Test2_reference_metrics": 3,
        "Test2_unsupported_values_null": len(component_metrics["unsupported_metrics"]),
        "Test2_native_structural_proof": structural,
        "physical_scene_accuracy_validated": False,
        "bound_artifact_sha256": {
            str(p): sha(p)
            for p in [
                parity_path,
                Path(receipt["original_Test1_report"]),
                Path(receipt["new_Test1_report"]),
                old_csv,
                new_csv,
                native_components_path,
            ]
        },
    }
    original_root = ART / "test02_candidate_v4"
    original_hashes = {str(p): sha(p) for p in original_root.rglob("*") if p.is_file()}
    assert read(original_root / "run/inference.json")["status"] == "completed"
    assert read(original_root / "run.executor.json")["status"] == "completed"
    assert read(original_root / "failure.json")["status"] == "failed"
    assert not (original_root / "completion.json").exists()
    continuation = ast.parse(tool_paths[2].read_text())
    assert not any(
        isinstance(n, ast.Subscript)
        and isinstance(n.value, ast.Name)
        and n.value.id == "worker"
        and isinstance(n.slice, ast.Constant)
        and n.slice.value == "session_id"
        for n in ast.walk(continuation)
    )
    for path, digest in sources.items():
        assert sha(path) == digest, path
    assert all(sha(path) == digest for path, digest in original_hashes.items())
    dump("numeric_parity.json", numeric)
    dump("receipt_checks.json", checks)
    dump(
        "source_binding.json",
        {
            "source_sha256": sources,
            "original_Test2_root": str(original_root),
            "original_Test2_artifact_sha256": original_hashes,
            "original_Test2_outer_failure_preserved": True,
            "new_NN": False,
            "producer_globals_or_ROOT_changed": False,
        },
    )
    print(
        json.dumps(
            {
                "status": "passed_independent_numeric_and_receipt_review",
                "sources": len(sources),
                "original_Test2_files": len(original_hashes),
                "numeric_AST_groups": len(numeric),
            }
        )
    )


if __name__ == "__main__":
    main()
