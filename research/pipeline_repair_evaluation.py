"""Unchanged rally evaluation after verified normal or explicit recovered completion.

Recovery never changes the original worker status and never supplies inference
intervals: predictions must already be the production exporter output.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.production_external_semantic_replay import load_finished_input, sha  # noqa: E402
from research.test2_evaluation import supplement, write_artifacts  # noqa: E402
from scripts.benchmarking.evaluate_rallies import read_csv  # noqa: E402


def evaluate(run: Path, sid: str, reference: Path, output: Path, *, completion_recovery: Path | None = None):
    if output.exists() or run.resolve() in output.resolve().parents:
        raise ValueError("evaluation requires a new directory outside the original run")
    recorded = load_finished_input(run, sid, completion_recovery=completion_recovery)
    predictions = run / "predicted_rallies.csv"
    # Producer/source/cache verification above must succeed before any labels.
    bindings = {
        *recorded.input_paths,
        predictions,
        reference,
        Path(__file__),
        ROOT / "research/test2_evaluation.py",
        ROOT / "scripts/benchmarking/evaluate_rallies.py",
    }
    before = {str(path.resolve()): sha(path) for path in bindings}
    fps = recorded.media["fps_num"] / recorded.media["fps_den"]
    gt, pred = read_csv(reference, fps), read_csv(predictions, fps)
    result, rows = supplement(gt, pred, fps, recorded.media["n_frames"])
    result["provenance"] = before
    result["completion_check_scope"] = {
        "producer": recorded.layout,
        "receipt": str(recorded.report_path),
        "explicit_posthoc_finalization_recovery": completion_recovery is not None,
        "original_worker_receipt_unchanged": True,
        "cache_digest_scope": recorded.cache_digest_scope,
        "reference_role": "legacy annotation agreement; no independent physical accuracy certification",
        "matching": "unchanged IoU 0.5; maximum cardinality then total IoU; zero-origin half-open frames",
    }
    if any(sha(Path(path)) != digest for path, digest in before.items()):
        raise ValueError("evaluation input changed during evaluation")
    write_artifacts(output, result, rows)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("run", "reference", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--completion-recovery", type=Path)
    args = parser.parse_args()
    evaluate(
        args.run.resolve(),
        args.session,
        args.reference.resolve(),
        args.output.resolve(),
        completion_recovery=args.completion_recovery.resolve() if args.completion_recovery else None,
    )


if __name__ == "__main__":
    main()
