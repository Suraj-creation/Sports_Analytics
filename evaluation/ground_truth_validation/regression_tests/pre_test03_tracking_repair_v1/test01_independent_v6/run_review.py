"""CPU-only review entrypoint; refuses unfinished runs before reading metrics."""

import json
import os
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent


def main():
    config = json.loads((OUT / "review_config.json").read_text())
    completion = Path(config["artifact_root"]) / "completion.json"
    if not completion.is_file():
        raise ValueError("Fresh workflow is incomplete; no metric consumption is allowed")
    from native_completion_gate import completion_contract

    completion_contract(json.loads(completion.read_text()), config)
    native = Path(config["native_root"])
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = os.pathsep.join(map(str, [native / "sports/badminton/src", native / "engine/src", native]))
    for name in ["review_completed_run.py", "review_full_deltas.py", "audit_raw_associated_acquisition.py"]:
        command = [sys.executable, str(OUT / name)]
        with (OUT / (Path(name).stem + ".command.json")).open("x") as stream:
            json.dump(
                {"argv": command, "cwd": str(native), "PYTHONPATH": env["PYTHONPATH"], "new_neural_inference": False},
                stream,
                indent=2,
            )
            stream.write("\n")
        with (OUT / (Path(name).stem + ".execution.log")).open("x") as stream:
            result = subprocess.run(  # noqa: S603 - fixed local review scripts and explicit argv; no shell
                command, cwd=native, env=env, stdout=stream, stderr=subprocess.STDOUT, check=False
            )
        if result.returncode:
            raise RuntimeError(f"Independent review failed closed at {name}; original log preserved")


if __name__ == "__main__":
    main()
