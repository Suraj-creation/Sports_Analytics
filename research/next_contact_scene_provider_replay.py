"""Controlled cached semantics with the actual opt-in production contact provider.

The caller supplies independent cache/run identities and exact rally flags.
Ground truth is never read; evaluation is a separate operation after export.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

import replay_rally_evidence as semantic

from bai_badminton.components import _MotionReliableContact
from bai_badminton.events.contact import CONTACT_RELIABILITY_MODEL

ROOT = Path(__file__).resolve().parents[1]
CONTACT_IMPLEMENTATION = "contact-motion-reliability-v1"
FLAGS = {
    "use_reconstruction": False,
    "motion_guard": False,
    "use_exit_recovery": True,
    "use_curve_exit": False,
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--contact-implementation", choices=[CONTACT_IMPLEMENTATION], required=True)
    parser.add_argument("--spatial-sigma-px", type=float, required=True)
    parser.add_argument("--rally-implementation", choices=["rally-evidence-tracklets-v1"], required=True)
    parser.add_argument("--rally-params", type=json.loads, required=True)
    args = parser.parse_args()
    if args.rally_params != FLAGS:
        raise ValueError("this controlled interaction requires all four explicit frozen rally flags")
    source_paths = [
        Path(__file__),
        ROOT / "research/replay_rally_evidence.py",
        ROOT / "sports/badminton/src/bai_badminton/events/contact.py",
        ROOT / "sports/badminton/src/bai_badminton/components.py",
        ROOT / "sports/badminton/src/bai_badminton/engine.py",
        ROOT / "sports/badminton/src/bai_badminton/participant_contact.py",
    ]
    captured = {path: path.read_bytes() for path in source_paths}
    source_hashes = {str(path.relative_to(ROOT)): hashlib.sha256(data).hexdigest() for path, data in captured.items()}
    provider = _MotionReliableContact({"spatial_sigma_px": args.spatial_sigma_px})
    original_engine = semantic.BadmintonMatchEngine
    constructed = []

    def engine_with_contact(*values, **kwargs):
        if kwargs.get("contact_inference") is not None:
            raise ValueError("contact provider is already supplied; refusing an ambiguous override")
        kwargs["contact_inference"] = provider
        engine = original_engine(*values, **kwargs)
        constructed.append(engine.contact_inference is provider)
        return engine

    semantic.BadmintonMatchEngine = engine_with_contact
    started = time.monotonic()
    semantic.replay(
        args.baseline.resolve(),
        args.output.resolve(),
        dict(args.rally_params),
        implementation=args.rally_implementation,
        candidate=True,
    )
    elapsed = time.monotonic() - started
    if constructed != [True]:
        raise RuntimeError("production contact provider injection was not verified")
    events = [json.loads(line) for line in (args.output / "events.jsonl").open()]
    superseded = {event["supersedes"] for event in events if event.get("supersedes")}
    contacts = [
        event
        for event in events
        if event["type"] == "contact" and event["event_id"] not in superseded and event["status"] != "retracted"
    ]
    actual_models = sorted({event["payload"]["contact_method"] for event in contacts})
    if contacts and actual_models != [CONTACT_RELIABILITY_MODEL]:
        raise RuntimeError("contact event provenance differs from the selected production provider")
    snapshots = args.output / "executor_source"
    for path, data in captured.items():
        destination = snapshots / path.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    unchanged = all(sha(path) == source_hashes[str(path.relative_to(ROOT))] for path in source_paths)
    metadata = {
        "mode": "controlled semantic replay on source run's own perception caches; NOT new neural inference",
        "executor_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "baseline": str(args.baseline.resolve()),
        "baseline_metadata_sha256": sha(args.baseline / "benchmark_metadata.json"),
        "reference_profile_note": (
            "replay_metadata.profile is inherited source profile; actual override is explicit here"
        ),
        "actual_override": {
            "contact_implementation": CONTACT_IMPLEMENTATION,
            "contact_class": "bai_badminton.components._MotionReliableContact",
            "contact_model": CONTACT_RELIABILITY_MODEL,
            "contact_params": {"spatial_sigma_px": args.spatial_sigma_px},
            "rally_implementation": args.rally_implementation,
            "rally_params": args.rally_params,
        },
        "source_sha256_before": source_hashes,
        "source_unchanged": unchanged,
        "injection_verified": constructed,
        "live_contact_count": len(contacts),
        "actual_contact_models": actual_models,
        "semantic_elapsed_seconds": elapsed,
        "confidence_semantics": "uncalibrated heuristic support; spatial scale is sensitivity assumption",
        "ground_truth_usage": "no annotation values read by this executor",
        "limitations": [
            "Perception and cadence feedback fixed to source run",
            "Contact counts are not physical contact accuracy",
            "The preceding old-mask reliability trial used a different rally provider; not a complete factorial",
        ],
    }
    (args.output / "contact_provider_override.json").write_text(json.dumps(metadata, indent=2) + "\n")
    if not unchanged:
        raise RuntimeError("executor source changed during replay")
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    main()
