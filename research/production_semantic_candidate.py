"""Controlled production-engine replay; never fresh inference or annotation-fed decisions.

Association uses retained candidates only. Optional scene hypotheses are from a
separately hashed prior-only pixel diagnostic; its legacy ROI context is explicit.
The unchanged evaluator is invoked only after predictions have been written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import research.replay_rally_evidence as replay_module  # noqa: E402
from bai_badminton.components import _ContactEvidence  # noqa: E402
from bai_badminton.engine import BadmintonMatchEngine  # noqa: E402
from bai_badminton.perception.association import CausalShuttleAssociation  # noqa: E402
from bai_badminton.perception.content import scene_change_from_dict  # noqa: E402
from bai_badminton.plugin import BadmintonSession  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--association", action="store_true")
    parser.add_argument("--scene-hypotheses", type=Path)
    parser.add_argument("--contact-evidence", action="store_true")
    args = parser.parse_args()
    source = args.source.resolve()
    metadata = json.loads((source / "benchmark_metadata.json").read_text())
    provider = CausalShuttleAssociation(fps=metadata["video_fps"])
    scene = {}
    if args.scene_hypotheses:
        for line in args.scene_hypotheses.open():
            evidence = scene_change_from_dict(json.loads(line)["scene"])
            if evidence.hypothesis:
                scene[evidence.frame] = evidence
    old_decode, old_engine = BadmintonSession.decode_perception, replay_module.BadmintonMatchEngine
    epoch, observed_statuses = 0, {}

    def decode(receiver, data, *, diagnostic=False):
        nonlocal epoch
        chunk = old_decode(receiver, data, diagnostic=diagnostic)
        for fp in chunk.frames:
            if fp.frame_idx in scene:
                epoch += 1
                fp.content_change = scene[fp.frame_idx]
            fp.content_epoch = epoch if args.scene_hypotheses else fp.content_epoch
            if args.association:
                registered = (
                    fp.cam is not None and fp.calibration_state is not None and fp.calibration_state.value == "VALID"
                )
                fp.shuttle_observation = provider.update(
                    fp.frame_idx,
                    epoch=(fp.shot_id << 32) | fp.content_epoch,
                    raw_xy=fp.shuttle_xy,
                    raw_support=fp.shuttle_conf,
                    diagnostic=fp.diagnostic.shuttle if fp.diagnostic else None,
                    image_valid=not fp.replay,
                    image_to_reference=np.linalg.inv(fp.cam) if registered else None,
                )
                status = fp.shuttle_observation.status
                observed_statuses[status] = observed_statuses.get(status, 0) + 1
            fp.__post_init__()
        return chunk

    class Engine(BadmintonMatchEngine):
        def __init__(self, *a, **kw):
            if args.contact_evidence:
                kw["contact_inference"] = _ContactEvidence({"spatial_sigma_px": 2.5 / math.sqrt(12)})
            super().__init__(*a, **kw)

    BadmintonSession.decode_perception = decode
    replay_module.BadmintonMatchEngine = Engine
    try:
        replay_module.replay(
            source,
            args.output.resolve(),
            {
                "use_reconstruction": False,
                "motion_guard": False,
                "use_exit_recovery": True,
                "use_curve_exit": False,
            },
            implementation="rally-evidence-tracklets-v1",
            candidate=bool(args.association or args.scene_hypotheses),
        )
    finally:
        BadmintonSession.decode_perception = old_decode
        replay_module.BadmintonMatchEngine = old_engine
    out = args.output.resolve()
    replay_metadata = json.loads((out / "replay_metadata.json").read_text())
    assert replay_metadata["source_unchanged"]
    archive = out / "executed_source"
    for name, value in replay_metadata["source_sha256"].items():
        path = ROOT / name
        assert sha(path) == value
        target = archive / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    (out / "executed_candidate.py").write_bytes(Path(__file__).read_bytes())
    from scripts.benchmarking.evaluate_rallies import read_csv, save_evaluation

    fps = metadata["video_fps"]
    metrics = save_evaluation(
        out, read_csv(ROOT / metadata["ground_truth_path"], fps), read_csv(out / "predicted_rallies.csv", fps), fps
    )
    manifest = {
        "mode": "cached production semantic counterfactual; NOT fresh inference",
        "source_run": str(source),
        "source_metadata_sha256": sha(source / "benchmark_metadata.json"),
        "association": args.association,
        "contact_evidence": args.contact_evidence,
        "scene_hypotheses_sha256": sha(args.scene_hypotheses) if args.scene_hypotheses else None,
        "scene_barriers": sorted(scene),
        "association_status_counts": observed_statuses,
        "cache_candidate_coverage": "selected diagnostic windows only; unknown elsewhere",
        "replay_metadata_sha256": sha(out / "replay_metadata.json"),
        "ground_truth_use": "unchanged evaluation after durable predictions only",
        "detection": metrics["detection"],
        "selected_interval_parity": replay_metadata["baseline_interval_parity"],
        "limits": ["no independent contact/scene/shuttle labels", "legacy scene ROI/cadence context"],
    }
    (out / "candidate_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
