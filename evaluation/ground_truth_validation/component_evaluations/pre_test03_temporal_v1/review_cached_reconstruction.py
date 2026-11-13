"""Read-only full-cache window diagnostic, not engine replay or neural inference."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import msgpack
import numpy as np

from bai_badminton.events.rally_motion import trajectory_continuation_supported
from bai_badminton.observations import WindowObs
from bai_badminton.perception.shuttle_post import Track, process


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def ranges(mask):
    edges = np.diff(np.r_[False, mask, False].astype(int))
    return list(zip(np.flatnonzero(edges == 1).tolist(), np.flatnonzero(edges == -1).tolist()))


def review(run):
    info = json.loads((run/"inference.json").read_text())
    parent = json.loads(run.with_name(run.name+".executor.json").read_text())
    if info["status"] != "completed" or parent["status"] != "completed" or parent["worker_exit_code"] != 0:
        raise ValueError("Require completed source/cache run")
    receipt = info["perception_cache_catalog"]
    catalog_path = run/receipt["path"]
    if sha(catalog_path) != receipt["sha256"]:
        raise ValueError("Completed catalogue changed")
    catalog = json.loads(catalog_path.read_text())
    paths = {item["path"]: item["sha256"] for item in catalog["files"]}
    consumed, frames = {}, []
    for relative, digest in sorted(paths.items()):
        path = run/relative
        if sha(path) != digest:
            raise ValueError("Original source cache changed")
        consumed[str(path)] = digest
        frames.extend(msgpack.unpackb(path.read_bytes(), raw=False)["frames"])
    n = info["frames_processed"]
    if [f["f"] for f in frames] != list(range(n)):
        raise ValueError("Full original canonical cache population required")
    # This diagnostic composes the documented same-context stabilized pixels.
    # It does not instantiate identity/calibration/rally state or claim replay.
    points, valid, contexts = [], [], []
    for f in frames:
        raw = (f.get("sa") or {}).get("selected_xy")
        g = np.asarray(f["g"], dtype=float).reshape(3, 3) if f.get("g") else None
        usable = bool(g is not None and not f["l"] and f["v"] == "main" and f["cs"] == "VALID"
                      and np.isfinite(g).all() and np.linalg.cond(g) < 1e12)
        valid.append(usable)
        if raw is not None and usable:
            mapped = np.linalg.inv(g) @ np.r_[raw, 1.]
            points.append(mapped[:2]/mapped[2])
        else:
            points.append((np.nan, np.nan))
        contexts.append((f["sh"], f["ce"], f["r"], usable, f["v"]))
    points = np.asarray(points)
    valid = np.asarray(valid)
    breaks = np.r_[False, [a != b for a, b in zip(contexts, contexts[1:])]]
    visible = np.isfinite(points).all(axis=1) & valid
    raw = Track.from_arrays(points[:,0], points[:,1], visible, np.array([f["c"] for f in frames]))
    ordinary = process(raw, break_before=breaks)
    old = Track(*(getattr(ordinary, k).copy() for k in ("x", "y", "vis", "conf", "interp")))
    for i, f in enumerate(frames):
        if f.get("sa") is not None and f["sa"]["status"] != "observed":
            old.vis[i] = old.interp[i] = False
    blocked = ~valid
    for i, f in enumerate(frames):
        evidence = f.get("sa") or {}
        if evidence.get("status") in {"ambiguous", "invalid"} or evidence.get("association_status") == "rejected":
            blocked[i] = True
    processing_breaks = breaks | blocked
    processing_breaks[1:] |= blocked[:-1]
    changed_raw = Track.from_arrays(points[:,0], points[:,1], visible & ~blocked, raw.conf)
    candidate = process(changed_raw, break_before=processing_breaks)
    candidate.vis[blocked] = candidate.interp[blocked] = False
    window = WindowObs(0, info["media"]["fps_num"]/info["media"]["fps_den"], candidate, {},
                       replay=np.array([f["r"] for f in frames]), break_before=breaks)
    groups = []
    for lo, hi in ranges(candidate.interp):
        groups.append({"start":lo,"stop_exclusive":hi,"length":hi-lo,
                       "raw_status_counts":dict(Counter((f.get("sa") or {}).get("status") for f in frames[lo:hi])),
                       "existing_continuation_policy_supported":trajectory_continuation_supported(window,lo)})
    observed_differences = np.flatnonzero((old.vis & ~old.interp) != (candidate.vis & ~candidate.interp)).tolist()
    g69 = []
    if n == 29296:
        for f in range(27324,27351):
            g69.append({"frame":f,"source_status":(frames[f].get("sa") or {}).get("status"),
                        "old_interp":bool(old.interp[f]),"candidate_interp":bool(candidate.interp[f]),
                        "observed":bool(candidate.vis[f] and not candidate.interp[f]),
                        "continuation_supported":trajectory_continuation_supported(window,f) if candidate.interp[f] else False})
    return {"scope":"All retained source cache pixels in a full-array window diagnostic; NOT full engine replay or NN inference",
            "source_sha256":info["source_sha256"],"frames":n,"cache_catalog_sha256":receipt["sha256"],
            "old_reconstructed_frames":int(old.interp.sum()),"candidate_reconstructed_frames":int(candidate.interp.sum()),
            "candidate_reconstruction_groups":groups,"observed_mask_difference_count":len(observed_differences),
            "observed_mask_difference_frames":observed_differences,"g69_window":g69,
            "existing_continuation_supported_groups":sum(g["existing_continuation_policy_supported"] for g in groups),
            "existing_continuation_supported_frames":sum(g["length"] for g in groups if g["existing_continuation_policy_supported"]),
            "input_sha256":{str(run/"inference.json"):sha(run/"inference.json"),str(catalog_path):sha(catalog_path),**consumed},
            "physical_accuracy_claimed":False,"thresholds_modified":False,"raw_observations_modified":False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = review(args.run.resolve())
    result["helper_sha256"] = sha(__file__)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(result,stream,indent=2,allow_nan=False)
        stream.write("\n")
    print(json.dumps({k:v for k,v in result.items() if k in {"frames","old_reconstructed_frames","candidate_reconstructed_frames","observed_mask_difference_count","existing_continuation_supported_groups","existing_continuation_supported_frames"}}))


if __name__ == "__main__":
    main()
