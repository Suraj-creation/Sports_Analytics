"""Repeat the previous main scopes without asserting a whole-candidate freeze.

The evolving working tree is recorded before/after. This is preliminary,
not a substitute for the orchestrator's later committed-source acceptance run.
"""
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path("/home/administrator/Desktop/sport-analytics/test03-scene-overlap-20261112")
MAIN = ROOT.parent / "Sports_Analytics"
OUT = MAIN / "evaluation/ground_truth_validation/regression_tests/pre_test03_scene_origin_v1/unit_main_preliminary_v1"
PRIOR = MAIN / "evaluation/ground_truth_validation/regression_tests/pre_test03_contract_v1/unit_main_v1"
SCOPES = ["engine/tests", "sports/badminton/tests", "agents/tests", "apps/api/tests", "tests/benchmarking"]
CORE = ["sports/badminton/src/bai_badminton/perception/scene_change.py",
        "sports/badminton/src/bai_badminton/perception/content.py",
        "sports/badminton/src/bai_badminton/perception/components.py", "sports/badminton/src/bai_badminton/plugin.py"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory():
    paths = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, text=True)
    return {name: sha(ROOT / name) for name in sorted(set(paths.splitlines()))
            if name.endswith((".py", ".toml", ".yaml", ".yml")) and (ROOT / name).is_file()}


def main():
    assert not OUT.exists()
    prior = json.loads((PRIOR / "manifest.json").read_text())
    assert prior["argv"][3:8] == SCOPES
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(str(ROOT / name) for name in
                                       ["sports/badminton/src", "engine/src", "agents/src", "apps/api/src", "."])
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    probe = "import bai_badminton.engine,bai_engine;print(bai_badminton.engine.__file__);print(bai_engine.__file__)"
    imports = subprocess.check_output([str(ROOT / ".venv/bin/python"), "-c", probe], cwd=ROOT, env=env, text=True).splitlines()
    assert len(imports) == 2 and all(Path(name).resolve().is_relative_to(ROOT) for name in imports)
    OUT.mkdir(parents=True)
    shutil.copyfile(__file__, OUT / "executed_preliminary_runner.py")
    command = [str(ROOT / ".venv/bin/python"), "-m", "pytest", *SCOPES, "-q", "--junitxml=" + str(OUT / "junit.xml")]
    before = inventory()
    started = time.time()
    meta = {"schema": "preliminary-main-suite-invocation:v1", "argv": command, "cwd": str(ROOT),
            "scope": SCOPES, "prior_scope_receipt": str(PRIOR / "manifest.json"),
            "prior_receipt_sha256": sha(PRIOR / "manifest.json"), "imports": imports,
            "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "git_status": subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True),
            "PYTHONPATH": env["PYTHONPATH"], "CUDA_VISIBLE_DEVICES": env.get("CUDA_VISIBLE_DEVICES"),
            "python": sys.version, "platform": platform.platform(), "pytest": importlib.metadata.version("pytest"),
            "started_epoch": started, "files_sha256": before, "whole_source_freeze_claimed": False,
            "core_source_sha256": {name: before[name] for name in CORE}}
    (OUT / "manifest.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps({"started": "preliminary_main", "output": str(OUT), "source_files": len(before)}), flush=True)
    with (OUT / "pytest.log").open("xb") as log:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=False)
    after = inventory()
    changed = [name for name in sorted(set(before) | set(after)) if before.get(name) != after.get(name)]
    counts = {}
    if (OUT / "junit.xml").exists():
        tree = ET.parse(OUT / "junit.xml")
        counts = {key: sum(int(node.get(key, "0")) for node in tree.iter("testsuite"))
                  for key in ["tests", "failures", "errors", "skipped"]}
    receipt = {"schema": "preliminary-main-suite-completion:v1", "exit_code": result.returncode,
               "elapsed_seconds": time.time() - started, "junit_counts": counts,
               "whole_source_freeze_claimed": False, "changed_files": changed,
               "core_sources_unchanged": all(before[name] == after.get(name) for name in CORE),
               "after_files_sha256": after, "manifest_sha256": sha(OUT / "manifest.json"),
               "log_sha256": sha(OUT / "pytest.log")}
    if (OUT / "junit.xml").exists():
        receipt["junit_sha256"] = sha(OUT / "junit.xml")
    (OUT / "completion.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({key: value for key, value in receipt.items() if key != "after_files_sha256"}), flush=True)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
