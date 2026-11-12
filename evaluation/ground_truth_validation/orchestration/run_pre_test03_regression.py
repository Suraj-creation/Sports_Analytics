"""One candidate-native fresh Test1/2 regression; no cleanup or Test3 advance.

Numerical evaluators and matching remain unchanged; codec24 uses an explicit
source-native structural audit. Historical JSONs are copied and compared
read-only, never re-evaluated with new code. --check-only validates inputs/imports
without creating an output or starting inference.
"""

from __future__ import annotations

import argparse
import ast
import fcntl
import hashlib
import json
import math
import os
import shutil
import subprocess
import time
import traceback
from pathlib import Path

import yaml

# The orchestration workspace is explicit configuration, separate from the
# actual native producer root. No imported native module ROOT is reassigned.
MAIN = Path(os.environ.get("SPORTS_ANALYTICS_PRIMARY_WORKSPACE", Path(__file__).resolve().parents[3])).resolve()
WORK = MAIN / "evaluation/ground_truth_validation"
OLD = MAIN.parent / "ground-truth-validation-artifacts-20261110"
NEW = MAIN.parent / "ground-truth-validation-artifacts-20261111/pre_test03_v1"
STATUS = WORK / "regression_tests/pre_test03_v1"
PROFILE = "config/profiles/experimental-pipeline-repair-v1.yaml"
PINS = (PROFILE, "models/manifest.yaml", "models/cache/lock.json")
SPEC = {
    1: {
        "sha": "877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6",
        "n": 17268,
        "refs": {
            "Test1_Full.csv",
            "Test1_Full2.csv",
            "Test1_Full_rally.csv",
            "Test1_Full_rev_T.csv",
            "Test1_Full_rev_T4.csv",
            "win_predictions.csv",
        },
        "binding": "test_01/diagnostics/geometry_root_cause/diagnostic_coordinate_binding.json",
    },
    2: {
        "sha": "4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a",
        "n": 29296,
        "refs": {"Test2_Full.csv", "Test2_Full_rally.csv", "win_predictions.csv"},
        "binding": "test_02/diagnostics/annotation_visual_review/diagnostic_coordinate_binding.json",
    },
}
COMMON = (
    "research/production_external_stress.py",
    "research/normal_timestamp_audit.py",
    "research/pipeline_repair_run_analysis.py",
    "research/pipeline_repair_evaluation.py",
    "research/production_external_semantic_replay.py",
    "research/production_external_reference_report.py",
    "research/production_replay_parity_audit.py",
    "research/production_contact_result_audit.py",
    "research/test2_evaluation.py",
    "scripts/benchmarking/evaluate_rallies.py",
    "evaluation/ground_truth_validation/orchestration/evaluate_test01_components.py",
    "evaluation/ground_truth_validation/orchestration/evaluate_test02_components.py",
    "evaluation/ground_truth_validation/orchestration/export_completed_analytics.py",
    "evaluation/ground_truth_validation/orchestration/export_test02_heatmaps.py",
)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def require_new_output(output, pipeline, *, main=MAIN, old=OLD):
    output, pipeline = Path(output).resolve(), Path(pipeline).resolve()
    if output.exists() or output.is_symlink():
        raise ValueError("Existing outputs/failed attempts are immutable; require NEW output")
    for protected in (main, pipeline, old):
        protected = Path(protected).resolve()
        if output == protected or protected in output.parents or output in protected.parents:
            raise ValueError("Output overlaps protected repository/baseline paths")
    if any(p in {"baseline_v1", "improved_v1", "run"} for p in output.parts):
        raise ValueError("Output cannot target a historical run/baseline directory")
    return output


def require_pin(actual, expected, label):
    if not expected or actual != expected:
        raise ValueError("Changed or missing original pin: " + label)


def no_annotations(value):
    """Validate worker profile/session/input paths, never the evaluation plan's code list."""
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in {
                "ground_truth",
                "ground_truth_path",
                "annotation",
                "annotations",
                "reference_csv",
                "gt_path",
            }:
                raise ValueError("Annotations cannot enter worker configuration")
            no_annotations(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            no_annotations(item)
    elif isinstance(value, str):
        path = value.replace("\\", "/").lower()
        if "/part2/" in path or path.startswith("part2/") or path.endswith(".csv"):
            raise ValueError("Ground-truth/CSV input cannot enter worker")


def require_completed(info, parent, *, test):
    spec = SPEC[test]
    if (
        info.get("status") != "completed"
        or info.get("cached_perception_used") is not False
        or info.get("source_sha256") != spec["sha"]
        or info.get("frames_processed") != spec["n"]
        or info.get("frontier_frame") != spec["n"] - 1
        or parent.get("status") != "completed"
        or parent.get("worker_exit_code") != 0
        or parent.get("frozen_source_inputs_unchanged") is not True
        or parent.get("output_proxy_sha256") != info.get("proxy_sha256")
    ):
        raise ValueError("Genuine complete fresh worker+parent for the exact video required")
    a, b = info.get("perception_cache_catalog", {}), parent.get("perception_cache_catalog_verification", {})
    if (
        not a.get("sha256")
        or b.get("status") != "verified"
        or b.get("catalog_sha256") != a["sha256"]
        or b.get("frames") != spec["n"]
        or b.get("files") != a.get("file_count")
    ):
        raise ValueError("Parent-verified complete perception catalogue required")


def require_semantic(manifest, *, test, source_report_sha):
    if (
        manifest.get("schema") != "cached-external-semantic:v2"
        or manifest.get("baseline_parity") is not True
        or manifest.get("source_intervention") is not None
        or manifest.get("geometry_bracket") is not False
        or manifest.get("contact_motion_reliability") is not False
        or manifest.get("frames") != SPEC[test]["n"]
        or manifest.get("trace_step_count") != SPEC[test]["n"]
        or manifest.get("trace_ranges_telemetry_only") != [[0, SPEC[test]["n"]]]
        or manifest.get("source_report_sha256") != source_report_sha
    ):
        raise ValueError("Strict full own-run semantic parity required; this is not new NN inference")


def require_native_plan(plan, root, protocol, *, test, head):
    root, protocol = Path(root).resolve(), Path(protocol).resolve()
    case = plan.get("cases", {}).get(f"test{test}", {})
    sources = plan.get("source_files_sha256", {})
    if (
        Path(plan.get("root", "/missing")).resolve() != protocol
        or plan.get("code_commit") != head
        or case.get("frames") != SPEC[test]["n"]
        or case.get("source_sha256") != SPEC[test]["sha"]
        or Path(plan.get("profile_source", "/missing")) != root / PROFILE
        or str(root / "sports/badminton/src/bai_badminton/engine.py") not in sources
        or any(not Path(path).is_relative_to(root) for path in sources)
    ):
        raise ValueError("Candidate-native source paths, commit, protocol and exact full test plan required")


def require_unsupported_null(components):
    if any(value.get("value") is not None for value in components["unsupported_metrics"].values()):
        raise ValueError("Unsupported accuracy metrics must remain null, never zero performance")


def checked_references(before, after, test):
    if set(before) != SPEC[test]["refs"] or set(after) != SPEC[test]["refs"]:
        raise ValueError("All original reference families required")
    result = {}
    for name in sorted(before):
        old, new = before[name], after[name]
        if old["role"] != new["role"] or old["metrics"]["matching_policy"] != new["metrics"]["matching_policy"]:
            raise ValueError("Original reference interpretation/matching changed")
        result[name] = {"role": old["role"], "baseline": old["metrics"], "candidate": new["metrics"]}
    return result


def git(root, *args):
    executable = shutil.which("git") or "/usr/bin/git"
    return subprocess.check_output([executable, *args], cwd=root).decode()  # noqa: S603 - fixed Git argv, no shell


def require_dacc05e_sources(sources):
    for name, digest in sources.items():
        if name.startswith(("engine/src/", "sports/badminton/src/")) and name.endswith(".py"):
            expected = hashlib.sha256(git(MAIN, "show", "dacc05e:" + name).encode()).hexdigest()
            require_pin(digest, expected, "preserved dacc05e core " + name)


def environment(root):
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        str(root / p) for p in ("sports/badminton/src", "engine/src", "agents/src", "apps/api/src", ".")
    )
    env["PYTHONUNBUFFERED"] = "1"
    return env


def runtime_environment(root, env):
    code = """import importlib.metadata as m,json,platform,sys
names=['torch','onnxruntime-gpu','onnxruntime','rapidocr','rtmlib','av','numpy','opencv-python']
versions={}
for name in names:
 try: versions[name]=m.version(name)
 except m.PackageNotFoundError: versions[name]=None
print(json.dumps({'python':sys.version,'platform':platform.platform(),'packages':versions}))
"""
    result = json.loads(
        subprocess.check_output(  # noqa: S603 - fixed read-only metadata probe, no shell
            [str(root / ".venv/bin/python"), "-c", code], cwd=root, env=env, text=True
        )
    )
    gpu = shutil.which("nvidia-smi")
    result["gpu_inventory"] = (
        subprocess.check_output(  # noqa: S603 - resolved GPU inventory binary, fixed query
            [gpu, "--query-gpu=index,name,uuid,driver_version", "--format=csv"], text=True
        )
        if gpu
        else None
    )
    result["selected_environment"] = {
        key: env.get(key)
        for key in ("PYTHONPATH", "CUDA_VISIBLE_DEVICES", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "LD_LIBRARY_PATH")
    }
    return result


def source_inventory(root):
    # Track all code/config/test/doc edits in Git status; freeze every actual
    # production source byte, including new files, separately from HEAD alone.
    files = {
        p
        for name in (
            "engine/src",
            "sports/badminton/src",
            "agents/src",
            "apps/api/src",
            "config",
            "research",
            "scripts",
            "evaluation/ground_truth_validation/orchestration",
        )
        for p in (root / name).rglob("*")
        if p.is_file()
        and "__pycache__" not in p.parts
        and (
            name in {"engine/src", "sports/badminton/src", "agents/src", "apps/api/src", "config"} or p.suffix == ".py"
        )
    }
    files.update(root / p for p in (*COMMON, "pyproject.toml", "uv.lock", *PINS) if (root / p).is_file())
    return {str(p): sha(p) for p in sorted(files)}


def baseline_documents(test):
    baseline = OLD / f"test_{test:02d}/improved_v1"
    paths = {
        "components": baseline / "bound_reference_diagnostics/component_reference_metrics.json",
        "analysis": baseline / "analysis/technical_analysis.json",
        "plan": baseline / "protocol/plan.json",
        "worker": baseline / "run/inference.json",
        "parent": baseline / "run.executor.json",
        "catalogue": baseline / "run/perception_completion_catalog.json",
        "primary": baseline / "rally_reference_evaluation/evaluation_results.json",
    }
    paths["completion"] = baseline / (
        "regression_completion.json" if test == 1 else "all_reference_diagnostics_completion.json"
    )
    if test == 1:
        control = OLD / "test_02/test1_semantic_regression_v1"
        paths.update(
            semantic_control=control / "semantic_regression_metrics.json",
            semantic_control_completion=control / "completion.json",
        )
    return paths


def require_helper_compatibility(root):
    """Permit only reviewed codec/structural dispatch changes; metric AST is exact."""
    receipt = {}
    component_paths = {
        "evaluation/ground_truth_validation/orchestration/evaluate_test01_components.py",
        "evaluation/ground_truth_validation/orchestration/evaluate_test02_components.py",
    }
    dispatch = ast.parse(
        "audit_completed_component_frames(frames,n,packets=chunks,consumed=consumed,producer_root=ROOT) "
        "if any(chunk['v']>=24 for chunk in chunks) else audit_frames(frames,n)",
        mode="eval",
    ).body

    class Normalize(ast.NodeTransformer):
        def __init__(self, name):
            self.name = name
            self.dispatches = 0
            self.codec_changes = 0

        def visit_ImportFrom(self, node):
            if (
                self.name in component_paths
                and node.module == "research.scene_epoch_audit_v3"
                and len(node.names) == 1
                and node.names[0].name == "audit_completed_component_frames"
                and node.names[0].asname is None
            ):
                return None
            return node

        def visit_IfExp(self, node):
            if self.name in component_paths and ast.dump(node) == ast.dump(dispatch):
                self.dispatches += 1
                return node.orelse
            return self.generic_visit(node)

        def visit_Assign(self, node):
            if (
                self.name == "research/production_external_stress.py"
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "PERCEPTION_CATALOG_LIMITS"
            ):
                for key, value in zip(node.value.keys, node.value.values, strict=True):
                    if isinstance(key, ast.Constant) and key.value == "accepted_codec_versions":
                        values = [element.value for element in value.elts]
                        if values == [20, 21, 22, 23, 24]:
                            value.elts.pop()
                            self.codec_changes += 1
            return self.generic_visit(node)

        def visit_Call(self, node):
            if (
                self.name == "research/pipeline_repair_completion.py"
                and isinstance(node.func, ast.Name)
                and node.func.id == "_validate_cache_context"
            ):
                values = {item.arg: item.value for item in node.keywords}
                versions, label = values.get("accepted_versions"), values.get("context_label")
                if (
                    isinstance(versions, ast.Tuple)
                    and [value.value for value in versions.elts] == [21, 22, 23, 24]
                    and isinstance(label, ast.Constant)
                    and label.value == "completed codec21/22/23/24"
                ):
                    versions.elts.pop()
                    label.value = "completed codec21/22/23"
                    self.codec_changes += 1
            return self.generic_visit(node)

        def visit_Compare(self, node):
            expected = ast.parse("value['v'] in (21,22,23,24)", mode="eval").body
            if self.name == "research/production_external_stress.py" and ast.dump(node) == ast.dump(expected):
                node.comparators[0].elts.pop()
                self.codec_changes += 1
            return self.generic_visit(node)

    for name in (*COMMON, "research/pipeline_repair_completion.py"):
        before, after = MAIN / name, root / name
        previous_sha, current_sha = sha(before), sha(after)
        mode = "byte_identical"
        if previous_sha != current_sha:
            if name not in component_paths | {
                "research/production_external_stress.py",
                "research/pipeline_repair_completion.py",
            }:
                raise ValueError("Unreviewed evaluator/helper change: " + name)
            normalizer = Normalize(name)
            normalized = normalizer.visit(ast.parse(after.read_text()))
            if ast.dump(normalized, include_attributes=False) != ast.dump(
                ast.parse(before.read_text()), include_attributes=False
            ):
                raise ValueError("Matching/arithmetic or unreviewed helper AST change: " + name)
            if name in component_paths and normalizer.dispatches != 1:
                raise ValueError("Exactly one reviewed structural component dispatch required: " + name)
            expected_codec_changes = 1 if name == "research/pipeline_repair_completion.py" else 2
            if name not in component_paths and normalizer.codec_changes != expected_codec_changes:
                raise ValueError("Exactly the reviewed codec24 schema extensions are required")
            mode = "exact_AST_except_explicit_codec24_structural_dispatch"
        receipt[name] = {"primary_workspace_sha256": previous_sha, "native_sha256": current_sha, "compatibility": mode}
    return receipt


def preflight(args):
    if args.test not in SPEC:
        raise ValueError("Only Test1 or Test2 is authorized; no Test3")
    root, video = args.pipeline_root.resolve(strict=True), args.video.resolve(strict=True)
    output = require_new_output(args.output or NEW / f"test_{args.test:02d}", root)
    if root == MAIN or Path(git(root, "rev-parse", "--show-toplevel").strip()).resolve() != root:
        raise ValueError("Require isolated candidate-native Git root")
    if sha(video) != SPEC[args.test]["sha"]:
        raise ValueError("Wrong original test video SHA256")
    paths = baseline_documents(args.test)
    baseline = {name: read(path) for name, path in paths.items()}
    require_completed(baseline["worker"], baseline["parent"], test=args.test)
    require_pin(sha(paths["worker"]), baseline["parent"]["worker_report_sha256"], "baseline parent-bound worker")
    require_pin(sha(paths["plan"]), baseline["parent"]["plan_sha256"], "baseline parent-bound plan")
    require_pin(
        sha(paths["catalogue"]),
        baseline["worker"]["perception_cache_catalog"]["sha256"],
        "baseline completed catalogue",
    )
    if (
        baseline["catalogue"]["frame_count"] != SPEC[args.test]["n"]
        or baseline["catalogue"]["source_sha256"] != SPEC[args.test]["sha"]
    ):
        raise ValueError("Preserved baseline catalogue source/frontier mismatch")
    old = baseline["components"]
    if (
        old.get("source_sha256") != SPEC[args.test]["sha"]
        or old.get("test") != args.test
        or old.get("status") != "completed_readonly_component_reference_diagnostics"
        or set(old["interval_reference_comparisons"]) != SPEC[args.test]["refs"]
    ):
        raise ValueError("Preserved full all-reference baseline required")
    if args.test == 1:
        control, completion = baseline["semantic_control"], baseline["semantic_control_completion"]
        if (
            control.get("status") != "completed_controlled_semantic_regression"
            or control.get("new_neural_inference") is not False
            or control.get("source_sha256") != SPEC[1]["sha"]
            or control.get("original_inputs_annotations_cache_unchanged") is not True
            or control.get("frames") != SPEC[1]["n"]
            or completion.get("status") != control["status"]
            or completion["artifact_sha256"].get("semantic_regression_metrics.json") != sha(paths["semantic_control"])
        ):
            raise ValueError("Test1 latest dacc05e fixed-perception semantic control required")
        if set(control["all_reference_comparisons"]) != SPEC[1]["refs"] or any(
            value["semantic_replay_metrics"] != old["interval_reference_comparisons"][name]["metrics"]
            for name, value in control["all_reference_comparisons"].items()
        ):
            raise ValueError(
                "Test1 full-NN interval baseline differs from latest semantic control; cannot silently merge"
            )
        require_dacc05e_sources(control["source_intervention"]["executed_source_sha256"])
    else:
        require_dacc05e_sources(
            {
                str(Path(path).relative_to(MAIN)): digest
                for path, digest in baseline["plan"]["source_files_sha256"].items()
            }
        )
    protected = {str(path): sha(path) for path in paths.values()}
    prepared_profile = OLD / f"test_{args.test:02d}/improved_v1/protocol/profiles/experiment.yaml"
    protected[str(prepared_profile)] = sha(prepared_profile)
    for items in baseline["analysis"]["models_verified_during_analysis"].values():
        for record in items.values():
            path = record.get("source_path", record.get("path"))
            if path is not None and record.get("sha256"):
                require_pin(sha(path), record["sha256"], "actual model artifact " + str(path))
                protected[str(path)] = record["sha256"]
    for name in PINS:
        expected = baseline["plan"]["input_files_sha256"].get(str(MAIN / name))
        require_pin(sha(root / name), expected, name)
        protected[str(root / name)] = expected
    require_pin(sha(root / PROFILE), baseline["plan"]["profile_source_sha256"], "source profile")
    no_annotations(yaml.safe_load((root / PROFILE).read_text()))
    manifest = WORK / "dataset_inventory/dataset_manifest.json"
    protected[str(manifest)] = sha(manifest)
    # Every original Part2 supporting file remains unchanged, not just rally CSV.
    for item in read(manifest)["files"]:
        original = Path(item["path"])
        require_pin(sha(original), item["sha256"], str(original))
        protected[str(original)] = item["sha256"]
    main_annotations = MAIN / f"Part2/dataset/Test{args.test}_Full"
    candidate_annotations = root / f"Part2/dataset/Test{args.test}_Full"
    expected_names = {p.name for p in main_annotations.iterdir() if p.is_file()}
    if {p.name for p in candidate_annotations.iterdir() if p.is_file()} != expected_names:
        raise ValueError("Candidate annotation population differs from originals")
    for name in expected_names:
        path = candidate_annotations / name
        require_pin(sha(path), sha(main_annotations / name), "candidate original annotation " + name)
        protected[str(path)] = sha(path)
    binding = WORK / SPEC[args.test]["binding"]
    if read(binding).get("source_sha256") != SPEC[args.test]["sha"]:
        raise ValueError("Original coordinate certificate source mismatch")
    protected[str(binding)] = sha(binding)
    helper_compatibility = require_helper_compatibility(root)
    env = environment(root)
    probe = "import bai_badminton.engine,bai_engine;print(bai_badminton.engine.__file__);print(bai_engine.__file__)"
    imported = subprocess.check_output(  # noqa: S603 - candidate Python, fixed import probe, no shell
        [str(root / ".venv/bin/python"), "-c", probe], cwd=root, env=env, text=True
    ).splitlines()
    expected = [root / "sports/badminton/src/bai_badminton/engine.py", root / "engine/src/bai_engine/__init__.py"]
    if [Path(p).resolve() for p in imported] != expected:
        raise ValueError("Worker would import installed/main code instead of candidate")
    protected[str(Path(__file__).resolve())] = sha(__file__)
    return {
        "root": root,
        "video": video,
        "output": output,
        "paths": paths,
        "baseline": baseline,
        "protected": protected,
        "binding": binding,
        "env": env,
        "sources": source_inventory(root),
        "head": git(root, "rev-parse", "HEAD").strip(),
        "dirty": git(root, "status", "--porcelain=v1"),
        "patch": git(root, "diff", "--binary", "HEAD"),
        "imports": imported,
        "prepared_profile": yaml.safe_load(prepared_profile.read_text()),
        "helper_compatibility": helper_compatibility,
    }


def stable(admitted):
    if (
        source_inventory(admitted["root"]) != admitted["sources"]
        or git(admitted["root"], "rev-parse", "HEAD").strip() != admitted["head"]
        or git(admitted["root"], "status", "--porcelain=v1") != admitted["dirty"]
        or git(admitted["root"], "diff", "--binary", "HEAD") != admitted["patch"]
    ):
        raise ValueError("Frozen candidate commit/dirty source/helper set changed")
    if any(sha(path) != digest for path, digest in admitted["protected"].items()):
        raise ValueError("Original annotation/baseline/profile/model/helper input changed")


def state(status_dir, stage, **details):
    value = {
        "stage": stage,
        "epoch": time.time(),
        "details": details,
        "automatic_cleanup": False,
        "automatic_test3": False,
    }
    with (status_dir / "history.jsonl").open("a") as stream:
        stream.write(json.dumps(value, allow_nan=False) + "\n")
    temporary = status_dir / "status.tmp"
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(status_dir / "status.json")
    print(stage, flush=True)


def flat(value, prefix=""):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            path = prefix + "." + key if prefix else key
            if key in {
                "comparison",
                "raw_rows",
                "reference_source_rows",
                "scene_records",
                "details",
                "certificate",
                "readouts",
                "input_sha256",
            }:
                continue
            result.update(flat(item, path))
        return result
    if isinstance(value, list):
        if len(value) <= 32:
            return {k: v for i, item in enumerate(value) for k, v in flat(item, prefix + f"[{i}]").items()}
        return {prefix + ".retained_entries": len(value)}
    return {prefix: value}


def display(value):
    if value is None:
        return "Unavailable"
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("Nonfinite report metric")
        return f"{value:.10g}"
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def metric_table(lines, before, after):
    a, b = flat(before), flat(after)
    lines += ["", "| Saved metric | Preserved baseline/control | Fresh candidate | Delta |", "|---|---|---|---|"]
    for key in sorted(set(a) | set(b)):
        old, new = a.get(key), b.get(key)
        delta = new - old if type(old) in (int, float) and type(new) in (int, float) else None
        lines.append("| " + " | ".join(display(v) for v in (key, old, new, delta)) + " |")
    lines.append("")


def publish(admitted, test):
    output, baseline = admitted["output"], admitted["baseline"]
    after = read(output / "bound_reference_diagnostics/component_reference_metrics.json")
    if (
        after.get("annotations_modified") is not False
        or after.get("all_annotation_files_accounted_for") is not True
        or after.get("source_sha256") != SPEC[test]["sha"]
    ):
        raise ValueError("Complete unchanged all-annotation candidate evaluation required")
    require_unsupported_null(after)
    refs = checked_references(
        baseline["components"]["interval_reference_comparisons"], after["interval_reference_comparisons"], test
    )
    analysis = read(output / "analysis/technical_analysis.json")

    def models(value):
        return {
            group: {name: {k: v for k, v in row.items() if k in {"sha256", "status"}} for name, row in rows.items()}
            for group, rows in value["models_verified_during_analysis"].items()
        }

    if models(analysis) != models(baseline["analysis"]):
        raise ValueError("Actual model checkpoint identities changed despite fixed pins")
    semantic_control = baseline.get("semantic_control", {}).get("semantic_replay_event_summary")
    before_events = semantic_control if test == 1 else baseline["analysis"]["events"]
    before_outcomes = baseline["components"]["outcome_and_stroke_coverage"]
    if test == 1:
        # Pure mapping of saved counts, not a re-evaluation of old events/labels.
        total = semantic_control["live_counts"]["rally_end"]
        known = semantic_control["semantic_counts"]["known_rally_winners"]
        before_outcomes = {
            "predicted_rallies": total,
            "known_winner_outputs": known,
            "unknown_winner_outputs": total - known,
            "stroke_label_counts": semantic_control["categories"]["stroke_stroke"],
        }
    comparison = {
        "schema": "pre-test03-fresh-regression:v1",
        "test": test,
        "scope": "Genuine full candidate-native fresh NN pipeline run versus preserved before JSON; "
        "baseline never re-evaluated",
        "interval_references": refs,
        "baseline_full_NN_components": baseline["components"],
        "fresh_components": after,
        "fresh_worker": read(output / "run/inference.json"),
        "fresh_parent": read(output / "run.executor.json"),
        "event_control_scope": "Latest dacc05e fixed-perception semantic control, NOT fresh NN"
        if test == 1
        else "Latest completed full fresh Test2 improved_v1",
        "before_event_summary": before_events,
        "before_outcome_and_stroke_control": before_outcomes,
        "fresh_event_summary": analysis["events"],
        "baseline_test1_semantic_control": baseline.get("semantic_control"),
        "baseline_json_sha256": {str(p): sha(p) for p in admitted["paths"].values()},
        "actual_model_identity_equal": True,
        "profile_unchanged": True,
        "annotations_unchanged": True,
        "physical_accuracy_gain_claimed": False,
        "visual_review_scope": "Generic root-owned source overlays pending; "
        "hardcoded Test2 HTML renderer deliberately not invoked",
        "test1_heatmap_scope": "Existing heatmap exporter is Test2-only; "
        "no zero grid or unsupported heatmap accuracy manufactured"
        if test == 1
        else "Actual canonical Test2 heatmap export retained",
    }
    dump(output / "comparison.json", comparison)
    lines = [
        f"# Pre-Test3 Test{test}: fresh candidate regression",
        "",
        comparison["scope"],
        "",
        "Test1 timing/component baseline uses its latest full NN run. Its contact/class control separately uses "
        "the latest dacc05e cached semantic regression; that control is not fresh neural inference. "
        "Generated-reference agreement and coverage are not independent contact/player/stroke/winner accuracy. "
        "Shared CPU/RAM/I/O and overlapping stage timers prevent a controlled speedup claim.",
        "",
        "Original matching, partial-reference policies, tolerances and original annotations are unchanged. "
        "Null means unavailable, never zero performance.",
    ]
    for name, row in refs.items():
        lines += ["## " + name, "", "Reference role: " + row["role"]]
        metric_table(lines, row["baseline"], row["candidate"])
        lines += ["| Arm | Missed reference IDs |", "|---|---|"]
        for arm in ("baseline", "candidate"):
            missed = row[arm]["missed_gt_rallies"]
            lines.append("| " + arm + " | " + (", ".join(map(str, missed)) or "None") + " |")
        lines += ["", "| Arm | Extra/unscored prediction | Frame interval | Scope |", "|---|---|---|---|"]
        for arm, reference in (
            ("baseline", baseline["components"]["interval_reference_comparisons"][name]),
            ("candidate", after["interval_reference_comparisons"][name]),
        ):
            for key, meaning in (
                ("unmatched_predictions", "FP under complete reference"),
                ("unscored_current_predictions", "Unscored under partial reference, not FP"),
            ):
                values = reference["metrics"].get(key, reference.get(key, []))
                for value in values:
                    lines.append(
                        f"| {arm} | {value['pred_rally']} | [{value['start_frame']},{value['end_frame']}) | {meaning} |"
                    )
    for section in (
        "annotation_applicability",
        "point_diagnostics",
        "court_diagnostic",
        "actual_cache_component_coverage",
        "track_coverage",
        "ocr_coverage",
        "runtime_resources",
        "unsupported_metrics",
    ):
        lines += ["## " + section]
        metric_table(lines, baseline["components"].get(section), after.get(section))
    lines += ["## Outcome/class counts against latest semantic control", "", comparison["event_control_scope"]]
    metric_table(lines, before_outcomes, after["outcome_and_stroke_coverage"])
    lines += ["## Contact/class event control", "", comparison["event_control_scope"]]
    metric_table(lines, before_events, analysis["events"])
    lines += ["## Actual models, resources and downstream products"]

    def runtime(worker, parent):
        return {
            "worker_elapsed_s": worker.get("elapsed_s"),
            "parent_elapsed_s": parent.get("elapsed_s"),
            "worker_runtime_scope": worker.get("runtime_scope"),
            "physical_gpu_index": parent.get("physical_gpu_index"),
            "allocated_gpu_uuid": parent.get("allocated_gpu_uuid"),
        }

    metric_table(
        lines,
        runtime(baseline["worker"], baseline["parent"]),
        runtime(comparison["fresh_worker"], comparison["fresh_parent"]),
    )
    lines += ["### Exact executed configuration"]
    metric_table(lines, baseline["worker"].get("profile"), comparison["fresh_worker"].get("profile"))
    for section in ("models_verified_during_analysis", "resources", "component_coverage", "selected_components"):
        metric_table(lines, baseline["analysis"].get(section), analysis.get(section))
    for name in (
        "analytics",
        "individual_analytics",
        "estimated_individual_analytics",
        "highlights",
        "rally_outcome_records",
        "scoring_outcome_evidence",
    ):
        path = output / f"downstream_exports/{name}.json"
        if path.is_file():
            lines += ["### " + name]
            metric_table(lines, None, read(path))
    if test == 2:
        lines += ["### Canonical heatmaps"]
        metric_table(lines, None, read(output / "heatmap_exports/heatmaps.json"))
    lines += [
        "## Reproduction and review limits",
        "",
        comparison["visual_review_scope"],
        "",
        comparison["test1_heatmap_scope"],
        "",
        f"Full comparison and original row matrices: [comparison.json]({output / 'comparison.json'}), "
        f"[bound component metrics]({output / 'bound_reference_diagnostics/component_reference_metrics.json'}).",
        f"[Frozen source/protocol]({output / 'preflight.json'}), "
        f"[genuine inference]({output / 'run/inference.json'}), "
        f"[actual runtime environment]({output / 'environment.json'}), "
        f"[strict own-run semantic replay]({output / 'diagnostic_replay/replay_manifest.json'}).",
        "No video, proxy, annotation, old result or failed attempt was deleted. No Test3 was started. "
        "Root must review actual changes and visual failure evidence before accepting the integrated fixes.",
        "",
    ]
    rendered = "\n".join(lines)
    if max(map(len, rendered.splitlines()), default=0) > 12000:
        raise ValueError("Oversized report cell; preserve raw arrays in JSON instead")
    (output / "comparison.md").write_text(rendered)
    return comparison


def execute(admitted, test, status_dir):
    root, output = admitted["root"], admitted["output"]
    output.mkdir(parents=True, exist_ok=False)
    admitted["owned_output"] = True
    dump(output / "environment.json", runtime_environment(root, admitted["env"]))
    for name, path in admitted["paths"].items():
        shutil.copyfile(path, output / f"before_{name}.json")
    (output / "candidate_dirty.patch").write_text(admitted["patch"])
    for raw, digest in admitted["sources"].items():
        path = Path(raw)
        destination = output / "executed_source" / path.relative_to(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        require_pin(sha(destination), digest, "frozen source snapshot")
    shutil.copyfile(__file__, output / "executed_runner.py")
    dump(
        output / "preflight.json",
        {
            "test": test,
            "pipeline_root": str(root),
            "commit": admitted["head"],
            "git_status": admitted["dirty"],
            "source_sha256": SPEC[test]["sha"],
            "candidate_sources_sha256": admitted["sources"],
            "protected_input_sha256": admitted["protected"],
            "imports": admitted["imports"],
            "video": str(admitted["video"]),
            "annotation_worker_ingestion": False,
            "primary_workspace": str(MAIN),
            "orchestration_tool_root": str(Path(__file__).resolve().parents[3]),
            "native_ROOT_reassigned": False,
            "helper_compatibility": admitted["helper_compatibility"],
            "new_output": str(output),
        },
    )

    def call(relative, args, label):
        stable(admitted)
        state(status_dir, label, output=str(output), test=test)
        command = [str(root / ".venv/bin/python"), str(root / relative), *map(str, args)]
        dump(
            output / f"{label}.command.json",
            {"argv": command, "cwd": str(root), "pipeline_root": str(root), "started_epoch": time.time()},
        )
        started = time.monotonic()
        with (output / f"{label}.log").open("x") as stream:
            result = subprocess.run(  # noqa: S603 - fixed repository helper and structured argv, no shell
                command, cwd=root, env=admitted["env"], stdout=stream, stderr=subprocess.STDOUT, check=False
            )
        dump(output / f"{label}.result.json", {"exit_code": result.returncode, "elapsed_s": time.monotonic() - started})
        if result.returncode:
            raise RuntimeError(label + " failed; logs and all partial artifacts retained")
        stable(admitted)

    case = f"test{test}"
    sid = f"UPLOADTEST{test}"
    n = SPEC[test]["n"]
    call(
        COMMON[0],
        [
            "prepare-upload",
            "--case",
            case,
            "--video",
            admitted["video"],
            "--profile-source",
            root / PROFILE,
            "--output",
            output / "protocol",
        ],
        "prepare",
    )
    plan = read(output / "protocol/plan.json")
    require_pin(
        plan["profile_source_sha256"], admitted["baseline"]["plan"]["profile_source_sha256"], "prepared profile"
    )
    require_native_plan(plan, root, output / "protocol", test=test, head=admitted["head"])
    if yaml.safe_load((output / "protocol/profiles/experiment.yaml").read_text()) != admitted["prepared_profile"]:
        raise ValueError("Prepared numeric/passive-diagnostic profile differs from the preserved per-video baseline")
    no_annotations(read(Path(plan["cases"][case]["session"])))
    no_annotations(list(plan["input_files_sha256"]))
    call(
        COMMON[0],
        [
            "run",
            "--case",
            case,
            "--plan",
            output / "protocol/plan.json",
            "--output",
            output / "run",
            "--gpu-index",
            "1",
        ],
        "inference",
    )
    info, parent = read(output / "run/inference.json"), read(output / "run.executor.json")
    require_completed(info, parent, test=test)
    require_pin(sha(output / "run/inference.json"), parent["worker_report_sha256"], "parent-bound worker receipt")
    require_pin(
        sha(output / "run" / info["perception_cache_catalog"]["path"]),
        info["perception_cache_catalog"]["sha256"],
        "completion catalogue",
    )
    call(COMMON[1], ["--run", output / "run", "--output", output / "timestamps"], "timestamps")
    call(
        "evaluation/ground_truth_validation/orchestration/analyse_native_completed_run.py",
        ["--run", output / "run", "--output", output / "analysis", "--producer-root", root, "--tool-root", root],
        "analysis",
    )
    evaluator = f"evaluation/ground_truth_validation/orchestration/evaluate_test0{test}_components.py"
    call(
        evaluator,
        [
            "--run",
            output / "run",
            "--output",
            output / "bound_reference_diagnostics",
            "--coordinate-binding",
            admitted["binding"],
        ],
        "components",
    )
    call(
        COMMON[3],
        [
            "--run",
            output / "run",
            "--session",
            sid,
            "--reference",
            MAIN / f"Part2/dataset/Test{test}_Full/Test{test}_Full_rally.csv",
            "--output",
            output / "rally_reference_evaluation",
        ],
        "primary_evaluation",
    )
    call(COMMON[-2], ["--run", output / "run", "--output", output / "downstream_exports"], "downstream")
    call(
        COMMON[4],
        [
            "--run",
            output / "run",
            "--session",
            sid,
            "--output",
            output / "diagnostic_replay",
            "--trace-ranges",
            json.dumps([[0, n]]),
            "--focus",
            "",
        ],
        "semantic_replay",
    )
    manifest = read(output / "diagnostic_replay/replay_manifest.json")
    require_semantic(manifest, test=test, source_report_sha=sha(output / "run/inference.json"))
    for name, digest in manifest["output_artifact_sha256"].items():
        require_pin(sha(output / "diagnostic_replay" / name), digest, "semantic replay output " + name)
    if test == 2:
        call(COMMON[-1], ["--artifact-root", output, "--output", output / "heatmap_exports"], "heatmaps")
    require_pin(sha(admitted["video"]), SPEC[test]["sha"], "final original source video")
    comparison = publish(admitted, test)
    stable(admitted)
    artifacts = {
        str(p.relative_to(output)): sha(p)
        for p in output.rglob("*")
        if p.is_file() and p.suffix not in {".sqlite", ".mp4"} and not p.name.endswith((".sqlite-wal", ".sqlite-shm"))
    }
    dump(
        output / "completion.json",
        {
            "status": "completed_fresh_candidate_regression_root_visual_review_pending",
            "test": test,
            "frames": n,
            "source_sha256": SPEC[test]["sha"],
            "candidate_commit": admitted["head"],
            "new_neural_inference": True,
            "own_run_semantic_parity": True,
            "annotations_and_baselines_unchanged": True,
            "source_helpers_models_profile_frozen": True,
            "actual_model_identity_equal": comparison["actual_model_identity_equal"],
            "artifact_sha256": artifacts,
            "no_cleanup": True,
            "no_test3": True,
            "independent_physical_accuracy_claimed": False,
        },
    )
    state(
        status_dir,
        "completed fresh regression; root visual/metric acceptance review pending",
        output=str(output),
        test=test,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test", type=int, choices=(1, 2), required=True)
    parser.add_argument("--pipeline-root", type=Path, required=True)
    parser.add_argument(
        "--video", type=Path, required=True, help="Exact original test video; Test2 must be restored separately"
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    admitted = preflight(args)
    if args.check_only:
        print(
            json.dumps(
                {
                    "status": "readonly_preflight_passed",
                    "test": args.test,
                    "pipeline_root": str(admitted["root"]),
                    "output": str(admitted["output"]),
                    "NN_started": False,
                }
            )
        )
        return
    STATUS.mkdir(parents=True, exist_ok=True)
    with (STATUS / "execution.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError("Another pre-Test3 fresh video regression is active") from error
        status_dir = STATUS / admitted["output"].name
        status_dir.mkdir(exist_ok=False)
        try:
            execute(admitted, args.test, status_dir)
        except BaseException as error:
            output = admitted["output"]
            if admitted.get("owned_output") is True and output.is_dir():
                (output / "failure.log").write_text(traceback.format_exc())
                if not (output / "failure.json").exists():
                    dump(
                        output / "failure.json",
                        {
                            "status": "failed",
                            "error": str(error),
                            "epoch": time.time(),
                            "partial_artifacts_preserved": True,
                            "no_test3": True,
                        },
                    )
            state(status_dir, "failed; partial evidence preserved", error=str(error), output=str(output))
            raise


if __name__ == "__main__":
    main()
