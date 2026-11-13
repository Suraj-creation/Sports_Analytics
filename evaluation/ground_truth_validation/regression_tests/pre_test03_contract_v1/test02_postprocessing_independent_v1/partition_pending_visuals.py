"""Partition complete review plan without re-rendering source-bound completed bundles."""

import json
from pathlib import Path

from native_completion_gate import sha

HERE = Path(__file__).resolve().parent


def partition(frames, covered, limit=128):
    ids = [x["frame"] for x in frames]
    if any(type(f) is not int or f < 0 for f in ids) or len(set(ids)) != len(ids):
        raise ValueError("Unique canonical source frames required")
    if type(limit) is not int or not 1 <= limit <= 128:
        raise ValueError("Render batch limit must be 1..128")
    pending = [item for item in frames if item["frame"] not in covered]
    batches = [pending[start : start + limit] for start in range(0, len(pending), limit)]
    reused = set(ids) & set(covered)
    emitted = [item["frame"] for batch in batches for item in batch]
    if len(set(emitted)) != len(emitted) or reused & set(emitted) or reused | set(emitted) != set(ids):
        raise ValueError("Source review cases dropped, duplicated or rerendered")
    return batches, sorted(reused)


def validate_bundle(path, config):
    completion_path = path / "completion.json"
    if not completion_path.is_file():
        raise ValueError("Existing visual bundle is not complete; cannot exclude its frames")
    receipt = json.loads(completion_path.read_text())
    invocation = json.loads((path / "invocation.json").read_text())
    if (
        receipt["status"] != "completed"
        or receipt["source_sha256"] != config["source_sha256"]
        or receipt["physical_gt_created"] is not False
        or receipt["metrics_recomputed"] is not False
        or Path(invocation["arguments"]["run"]).resolve() != Path(config["original_run"]).resolve()
        or Path(invocation["arguments"]["pipeline_root"]).resolve() != Path(config["native_root"]).resolve()
    ):
        raise ValueError("Existing visual bundle has different source/producer or altered metric scope")
    for name, digest in receipt["artifact_sha256"].items():
        if sha(path / name) != digest:
            raise ValueError("Existing visual artifact changed: " + name)
    for item in receipt["input_bindings"]:
        if sha(item["path"]) != item["sha256"]:
            raise ValueError("Existing visual input changed: " + item["path"])
    return {
        "path": str(path),
        "completion_sha256": sha(completion_path),
        "frames": receipt["frames"],
        "outputs_verified": len(receipt["artifact_sha256"]),
        "inputs_verified": len(receipt["input_bindings"]),
    }


def main():
    config = json.loads((HERE / "review_config.json").read_text())
    summary = json.loads((HERE / "summary.json").read_text())
    if summary["status"] != "completed_independent_Test2_postprocessing_review_pending_source_classification":
        raise ValueError("Independent guarded review has not completed")
    plan = json.loads((HERE / "source_frame_plan.json").read_text())
    if plan["source_sha256"] != config["source_sha256"] or plan["proxy_sha256"] != config["expected_proxy_sha256"]:
        raise ValueError("Independent complete frame plan changed source pairing")
    bundles = [validate_bundle(Path(p), config) for p in config["existing_visual_evidence_roots"]]
    covered = {frame for bundle in bundles for frame in bundle["frames"]}
    batches, reused = partition(plan["frames"], covered)
    directory = HERE / "pending_source_frame_plans"
    directory.mkdir(exist_ok=False)
    for number, frames in enumerate(batches, 1):
        with (directory / f"batch_{number:02d}.json").open("x") as handle:
            json.dump(
                {
                    **plan,
                    "frames": frames,
                    "scope": "Pending source review only; existing completed bundles reused, no cases dropped",
                },
                handle,
                indent=2,
            )
            handle.write("\n")
    with (HERE / "visual_evidence_partition.json").open("x") as handle:
        json.dump(
            {
                "status": "all_requested_frames_preserved_without_duplicate_rendering",
                "complete_source_plan_sha256": sha(HERE / "source_frame_plan.json"),
                "complete_requested_frames": len(plan["frames"]),
                "existing_bundles": bundles,
                "requested_reused_frames": reused,
                "pending_frames": sum(map(len, batches)),
                "pending_batch_count": len(batches),
                "maximum_batch_frames": 128,
                "physical_ground_truth": None,
            },
            handle,
            indent=2,
        )
        handle.write("\n")
    print(
        json.dumps(
            {
                "complete_frames": len(plan["frames"]),
                "reused_frames": len(reused),
                "pending_frames": sum(map(len, batches)),
                "pending_batches": len(batches),
            }
        )
    )


if __name__ == "__main__":
    main()
