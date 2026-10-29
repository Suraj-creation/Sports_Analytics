"""Explicit, read-only BST shadow inference for a completed singles session.

Example:
  python -m research.evaluation.bst_shadow_session --data-dir data --session ID \
      --output data/audit/ID-bst-shadow.json

The JSON is bound to source media, events, cache and model digests. It is never
appended to the session. No reference labels are read, and no accuracy is claimed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import torch

from bai_badminton.events.bst import CHECKPOINT_SHA256, BSTClassifier
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema.events import Event, current_view
from bai_engine.schema.session import Session, SessionStatus
from research.evaluation.benchmark_reference_session import _catalogue, _event_rows
from research.evaluation.bst_shadow import digest, extract_frames, infer_strokes


def run_session(data: Path, session_id: str, output: Path, models: Path) -> dict:
    if not session_id.isalnum():
        raise ValueError("valid session id required")
    if output.exists():
        raise ValueError("shadow output must be a new path")
    if output.resolve().is_relative_to((data / "sessions").resolve()):
        raise ValueError("shadow output must be outside session stores")
    catalogue = _catalogue(data, session_id)
    session = Session.model_validate_json(catalogue)
    if session.status != SessionStatus.ANALYSED or session.media is None or not session.source.sha256:
        raise ValueError("completed source-bound session required")
    if session.roster and session.roster.match_format != "singles":
        raise ValueError("BST-CG-AP supports singles only")
    media = data / "media" / session.source.sha256
    media_hashes = {name: digest(media / name) for name in ("source.mp4", "proxy.mp4")}
    if media_hashes["source.mp4"] != session.source.sha256:
        raise ValueError("source media digest mismatch")
    rows = _event_rows(data, session_id)
    event_hash = hashlib.sha256("\n".join(body for _, body in rows).encode()).hexdigest()
    events = current_view([Event.model_validate_json(body).with_seq(seq) for seq, body in rows])
    cache = data / "sessions" / session_id / "perception"
    frames, provenance = extract_frames(cache, [e for e in events if e.type == "calibration"])
    checkpoint = ModelRegistry(models).path("bst_cg_ap_shuttleset", fetch=False)
    predictions, reasons = infer_strokes(session, events, frames, BSTClassifier(checkpoint, device="cpu"))
    if catalogue != _catalogue(data, session_id) or rows != _event_rows(data, session_id):
        raise ValueError("source session changed during inference")
    if {path.name: digest(path) for path in cache.glob("seg_*.msgpack")} != provenance["cache_sha256"]:
        raise ValueError("source cache changed during inference")
    if media_hashes != {name: digest(media / name) for name in media_hashes}:
        raise ValueError("source media changed during inference")
    from bai_badminton.events import _bst_network, bst

    result = {
        "version": "bst-session-shadow-v1",
        "session_id": session_id,
        "source_media_sha256": session.source.sha256,
        "media_files": media_hashes,
        "media": session.media.model_dump(mode="json"),
        "catalogue_sha256": hashlib.sha256(catalogue.encode()).hexdigest(),
        "event_log_sha256": event_hash,
        "cache_provenance": provenance,
        "checkpoint_sha256": CHECKPOINT_SHA256,
        "source_files_sha256": {
            str(Path(module.__file__).resolve()): digest(Path(module.__file__)) for module in (bst, _bst_network)
        },
        "model": BSTClassifier.name,
        "device": "cpu",
        "torch_threads": torch.get_num_threads(),
        "coverage": dict(reasons),
        "predictions": list(predictions.values()),
        "source_session_modified": False,
        "reference_labels_used": False,
        "accuracy_evaluated": False,
        "limitations": [
            "Class probabilities are uncalibrated and do not prove that contact occurred.",
            "Incomplete or unsupported contexts remain unknown rather than borrowing observations.",
            "Sparse RTMPose inputs differ from dense MMPose training data.",
            "Court side is not a persistent player identity.",
            "The default application classifier remains rules; this JSON is diagnostic only.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--session", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--models", type=Path, default=Path("models"))
    args = parser.parse_args()
    torch.set_num_threads(2)
    result = run_session(args.data_dir.resolve(), args.session, args.output, args.models)
    print(json.dumps({"output": str(args.output.resolve()), "coverage": result["coverage"], "session_modified": False}))


if __name__ == "__main__":
    main()
