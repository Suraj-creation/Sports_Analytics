"""Add the root's third completed bundle without editing used review configuration."""

import json
from pathlib import Path

from native_completion_gate import sha
from partition_pending_visuals import partition, validate_bundle

HERE = Path(__file__).resolve().parent


def main():
    config = json.loads((HERE / "review_config.json").read_text())
    plan = json.loads((HERE / "source_frame_plan.json").read_text())
    paths = [Path(p) for p in config["existing_visual_evidence_roots"]]
    paths.append(HERE.parent / "visual_test02_weak_barriers_v1")
    bundles = [validate_bundle(path, config) for path in paths]
    covered = {frame for bundle in bundles for frame in bundle["frames"]}
    batches, reused = partition(plan["frames"], covered)
    directory = HERE / "pending_source_frame_plans_v2"
    directory.mkdir(exist_ok=False)
    files = []
    for number, frames in enumerate(batches, 1):
        path = directory / f"batch_{number:02d}.json"
        with path.open("x") as handle:
            json.dump(
                {
                    **plan,
                    "frames": frames,
                    "scope": "Remaining exact source cases after three completed bundles; no cases dropped",
                },
                handle,
                indent=2,
            )
            handle.write("\n")
        files.append({"path": str(path), "frames": len(frames), "sha256": sha(path)})
    receipt = {
        "status": "all_requested_frames_preserved_without_duplicate_rendering",
        "complete_source_plan_sha256": sha(HERE / "source_frame_plan.json"),
        "complete_requested_frames": len(plan["frames"]),
        "existing_bundles": bundles,
        "requested_reused_frames": reused,
        "pending_frames": sum(map(len, batches)),
        "pending_batch_count": len(batches),
        "maximum_batch_frames": 128,
        "pending_files": files,
        "prior_partition_preserved": "visual_evidence_partition.json",
        "all_requested_frames_visually_reviewed": False,
        "physical_ground_truth": None,
    }
    with (HERE / "visual_evidence_partition_v2.json").open("x") as handle:
        json.dump(receipt, handle, indent=2)
        handle.write("\n")
    print(
        json.dumps(
            {
                "complete": len(plan["frames"]),
                "reused": len(reused),
                "pending": receipt["pending_frames"],
                "batches": files,
            }
        )
    )


if __name__ == "__main__":
    main()
