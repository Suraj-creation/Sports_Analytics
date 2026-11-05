"""Causal association on frozen candidate summaries, never fresh inference or labels.

Frames without retained candidates explicitly retain unknown association. This
partial acquisition experiment cannot stand in for full-video association.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections import Counter
from pathlib import Path

import msgpack
import numpy as np

from bai_badminton.perception.association import CausalShuttleAssociation
from bai_badminton.perception.diagnostics import FrameDiagnostic


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = Path(__file__).resolve().parents[1] / "sports/badminton/src/bai_badminton/perception/association.py"
    before = digest(source)
    (args.output / "association_source.py").write_bytes(source.read_bytes())
    (args.output / "probe_source.py").write_bytes(Path(__file__).read_bytes())
    files = sorted(args.run.glob("runtime/sessions/*/perception/*.msgpack"))
    hashes = {str(p.resolve()): digest(p) for p in files}
    metadata = json.loads((args.run / "benchmark_metadata.json").read_text())
    provider = CausalShuttleAssociation(fps=metadata["video_fps"])
    counts, ambiguous, selected = Counter(), [], 0
    started = time.monotonic()
    with (args.output / "association.jsonl").open("x") as stream:
        for path in files:
            for row in msgpack.unpackb(path.read_bytes(), raw=False)["frames"]:
                diagnostic = FrameDiagnostic.from_dict(row["dg"]).shuttle if row.get("dg") else None
                registered = row.get("g") is not None and row.get("cs") == "VALID"
                transform = np.linalg.inv(np.asarray(row["g"]).reshape(3, 3)) if registered else None
                evidence = provider.update(
                    row["f"],
                    epoch=(row["sh"] << 32) | row.get("ce", 0),
                    raw_xy=row["s"],
                    raw_support=row["c"],
                    diagnostic=diagnostic,
                    image_valid=not row["r"],
                    image_to_reference=transform,
                )
                counts[evidence.status] += 1
                if diagnostic is not None:
                    selected += 1
                    stream.write(json.dumps(evidence.to_dict(), allow_nan=False) + "\n")
                if evidence.status == "ambiguous":
                    if ambiguous and row["f"] == ambiguous[-1][1] + 1:
                        ambiguous[-1][1] = row["f"]
                    else:
                        ambiguous.append([row["f"], row["f"]])
    assert digest(source) == before
    assert all(digest(Path(p)) == h for p, h in hashes.items())
    summary = {
        "mode": "frozen candidate evidence replay; partial candidate acquisition; no fresh inference",
        "hypothesis": "co-observed static distractors cannot establish airborne identity after becoming global maximum",
        "negative_controls": (
            "raw coordinates/confidences/cache bytes unchanged; standalone floor/weak-launch/jump controls in tests"
        ),
        "source_sha256": before,
        "script_sha256": digest(Path(__file__)),
        "source_run": str(args.run.resolve()),
        "cache_hashes": hashes,
        "status_counts": counts,
        "candidate_frames": selected,
        "ambiguous_ranges": ambiguous,
        "elapsed_s": time.monotonic() - started,
        "evidence_sha256": digest(args.output / "association.jsonl"),
        "limits": [
            "not independently labelled shuttle/contact accuracy",
            "unknown candidates outside recorded diagnostic windows",
        ],
    }
    (args.output / "manifest.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "cache_hashes"}, indent=2))


if __name__ == "__main__":
    main()
