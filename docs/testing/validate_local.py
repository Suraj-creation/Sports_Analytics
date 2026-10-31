"""Offline source-checkout validation using existing packages only.

Examples (from the repository root):
  python docs/testing/validate_local.py static
  python docs/testing/validate_local.py probe
  python docs/testing/validate_local.py --paths-file cached-paths.json test -q engine/tests

An optional JSON paths file lists existing dependency directories to add for this
process, such as compatible packages already in a local uv cache. Nothing is
installed, synchronized, fetched, or substituted. Tests must still report missing
optional dependencies as skips. No model accuracy is established by this tool.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOTS = (".", "engine/src", "sports/badminton/src", "apps/api/src", "agents/src", "research/src")
PACKAGES = (
    "pytest",
    "numpy",
    "scipy",
    "pydantic",
    "pydantic_settings",
    "cv2",
    "pyarrow",
    "duckdb",
    "msgpack",
    "ulid",
    "structlog",
    "redis",
    "av",
    "fastapi",
    "httpx",
    "hypothesis",
    "torch",
    "onnxruntime",
    "trackers",
    "supervision",
    "rtmlib",
    "rapidocr",
)


def paths(extra: Path | None) -> None:
    sys.path[:0] = [str(ROOT / name) for name in SOURCE_ROOTS]
    directories = json.loads(extra.read_text(encoding="utf-8-sig")) if extra is not None else []
    if not isinstance(directories, list) or not all(isinstance(item, str) for item in directories):
        raise ValueError("paths file must be a JSON list of existing package directories")
    for item in directories:
        directory = Path(item).resolve(strict=True)
        if not directory.is_dir():
            raise ValueError(f"not a package directory: {directory}")
        sys.path.append(str(directory))
    # CLI regression tests start real child interpreters. Carry the same source
    # and existing dependency paths into those children without installing them.
    inherited = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = os.pathsep.join(
        [*[str(ROOT / name) for name in SOURCE_ROOTS], *directories, *([inherited] if inherited else [])]
    )


def static() -> int:
    """Parse tracked project Python without importing dependencies or writing bytecode."""
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git must already be installed for source validation")
    files = (
        subprocess.check_output(  # noqa: S603 - resolved git with fixed read-only arguments
            [
                git,
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "--",
                "engine",
                "sports/badminton",
                "apps/api",
                "agents",
                "research",
                "docs/testing/validate_local.py",
            ],
            cwd=ROOT,
        )
        .decode()
        .splitlines()
    )
    checked, errors = 0, []
    for name in sorted(set(files)):
        path = ROOT / name
        if path.suffix != ".py" or not path.is_file():
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=name)
            checked += 1
        except (SyntaxError, UnicodeError) as exc:
            errors.append(f"{name}: {exc}")
    print(json.dumps({"parsed_python_files": checked, "errors": errors}, indent=2))
    return int(bool(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths-file", type=Path)
    parser.add_argument("command", choices=("probe", "static", "test", "script"))
    parser.add_argument("args", nargs=argparse.REMAINDER)
    options = parser.parse_args()
    paths(options.paths_file)
    if options.command == "static":
        return static()
    if options.command == "probe":
        found = {name: spec.origin if (spec := importlib.util.find_spec(name)) else None for name in PACKAGES}
        print(json.dumps({"python": sys.version, "executable": sys.executable, "packages": found}, indent=2))
        return 0
    # Source-only execution has no installed bai.sports entry-point metadata.
    # Register the real implementation, exactly as an installed entry point does.
    from bai_badminton.plugin import BadmintonPlugin
    from bai_engine.sport import register

    register(BadmintonPlugin())
    if options.command == "test":
        import pytest

        return int(pytest.main(options.args))
    if not options.args:
        parser.error("script requires a repository Python file and optional arguments")
    script = Path(options.args[0]).resolve(strict=True)
    if not script.is_relative_to(ROOT):
        parser.error("script must be inside this repository")
    sys.argv = [str(script), *options.args[1:]]
    runpy.run_path(str(script), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
