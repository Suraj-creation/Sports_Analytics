"""Export actual canonical Test2 heatmap grids without inventing empty players.

Rebuilds production analytics using a private copy of the already detached event
ledger and verified read-only detached tracks. Never opens original run SQLite.
"""

from __future__ import annotations

import argparse
import collections
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from bai_badminton.analytics.rebuild import build  # noqa: E402
from bai_engine.schema import Event  # noqa: E402
from bai_engine.store import EventStore, TrackStore  # noqa: E402
from evaluation.ground_truth_validation.orchestration.evaluate_test02_components import (  # noqa: E402
    MEDIA,
    TEST2_SHA,
    read,
    sha,
)
from research.production_external_semantic_replay import load_finished_input  # noqa: E402
from research.production_external_stress import verify_inputs  # noqa: E402


def export(artifact_root, output):
    root, output = artifact_root.resolve(strict=True), output.resolve()
    run = root / "run"
    if output.exists() or output == run or run in output.parents or output in run.parents:
        raise ValueError("Heatmaps require a new output separate from original run")
    session = read(run / "session.json")
    sid = session["session_id"]
    if session["source"].get("sha256") != TEST2_SHA:
        raise ValueError("Requires original Test2 source")
    finished = load_finished_input(run, sid)
    inference = read(finished.report_path)
    parent = read(run.with_suffix(".executor.json"))
    if (
        inference.get("status") != "completed"
        or inference.get("cached_perception_used") is not False
        or inference.get("frames_processed") != MEDIA[-1]
        or parent.get("status") != "completed"
        or parent.get("worker_exit_code") != 0
        or parent.get("frozen_source_inputs_unchanged") is not True
    ):
        raise ValueError("Heatmap export requires fresh completed unchanged source execution")
    if (
        finished.layout != "production-full-upload"
        or tuple(finished.media[k] for k in ("width", "height", "fps_num", "fps_den", "n_frames")) != MEDIA
    ):
        raise ValueError("Requires completed full canonical Test2 upload")
    plan = read(finished.manifest_path)
    verify_inputs(plan)
    downstream = root / "downstream_exports"
    receipt_path = downstream / "export_receipt.json"
    receipt = read(receipt_path)
    if (
        receipt.get("status") != "completed"
        or receipt.get("original_artifacts_unchanged") is not True
        or receipt.get("source_completion_sha256") != sha(finished.report_path)
        or Path(receipt["source_run"]).resolve() != run
    ):
        raise ValueError("Detached export is not bound to exact completed Test2 inference")
    for name, digest in receipt["output_sha256"].items():
        if sha(downstream / name) != digest:
            raise ValueError("Canonical export changed: " + name)
    detached = downstream / "detached"
    if not detached.is_dir() or detached.is_symlink():
        raise ValueError("Requires owned existing detached ledger and tracks")
    source_tracks = run / "data/sessions" / sid / "tracks"
    detached_tracks = detached / "tracks"
    source_files = {str(p.relative_to(source_tracks)): p for p in source_tracks.rglob("*") if p.is_file()}
    copied_files = {str(p.relative_to(detached_tracks)): p for p in detached_tracks.rglob("*") if p.is_file()}
    if source_files.keys() != copied_files.keys():
        raise ValueError("Detached track population differs from original completed tracks")
    consumed = {
        str(p): sha(p) for p in (*finished.input_paths, finished.report_path, finished.events_path, receipt_path)
    }
    consumed[str(Path(__file__).resolve())] = sha(Path(__file__))
    for name, source in source_files.items():
        digest = sha(source)
        if sha(copied_files[name]) != digest:
            raise ValueError("Detached observation track differs: " + name)
        consumed[str(source)] = digest
        consumed[str(copied_files[name])] = digest
    # Include every existing detached byte/receipt in the unchanged-input audit.
    for p in detached.rglob("*"):
        if p.is_file():
            consumed[str(p)] = sha(p)
    consumed[str(downstream / "analytics.json")] = sha(downstream / "analytics.json")
    original_events = [
        Event.model_validate_json(line) for line in finished.events_path.read_text().splitlines() if line
    ]
    original_events.sort(key=lambda e: e.seq if e.seq is not None else -1)
    output.mkdir(parents=True)
    work = output / "working"
    work.mkdir()
    for suffix in ("", "-wal", "-shm"):
        source = detached / ("events.sqlite" + suffix)
        if source.is_file():
            shutil.copyfile(source, work / source.name)
    store = EventStore(work / "events.sqlite", sid)
    try:
        restored = store.since(0, limit=len(original_events) + 1)
        if len(restored) != len(original_events):
            raise ValueError("Detached event population differs from original append-only ledger")
        for original, copied in zip(original_events, restored, strict=True):
            if original.model_dump(exclude={"seq"}) != copied.model_dump(exclude={"seq"}):
                raise ValueError("Detached event content/order/correction lineage differs")
        folded = build(store, TrackStore(detached_tracks), MEDIA[2] / MEDIA[3])
        public = folded.to_public()
        expected = read(downstream / "analytics.json")
        for key in ("metric_version", "shot_accounting", "rallies", "unofficial_rallies", "active_play_s", "players"):
            if public.get(key) != expected.get(key):
                raise ValueError("Canonical rebuild differs from accepted downstream export: " + key)
        # Enumerate only grids actually created by production admission gates.
        grids = [folded.heatmaps.to_public(player, kind) for player, kind in sorted(folded.heatmaps.grids)]
        live = store.query()
        stroke_events = [e for e in live if e.type == "stroke"]
        result = {
            "schema": "canonical-test2-heatmap-export:v1",
            "status": "completed",
            "test": 2,
            "session_id": sid,
            "source_sha256": TEST2_SHA,
            "grid_count": len(grids),
            "available": bool(grids),
            "heatmaps": grids,
            "canonical_named_player_count": len(folded.players),
            "official_rally_count": len(folded.rallies),
            "unofficial_rally_count": len(folded.unofficial),
            "live_stroke_events": len(stroke_events),
            "unattributed_live_stroke_events": sum(e.actors.player_id is None for e in stroke_events),
            "stroke_actor_counts": dict(collections.Counter(e.actors.player_id or "unknown" for e in stroke_events)),
            "no_grid_reasons": []
            if grids
            else ["No canonical heatmap samples passed existing phase, named-identity and geometry admission gates"],
            "policy": {
                "phase": "Production build admits stroke statistics and presence paths only from official rallies",
                "identity": (
                    "Named canonical actors/player_id required; anonymous detection slots are not renamed players"
                ),
                "geometry": (
                    "Production camera validity, court-quality, visibility, confidence, continuity "
                    "and finite-coordinate gates unchanged"
                ),
                "kinds": (
                    "presence, movement, origin, targeting and supported trajectory/human landing; "
                    "only actually present grids exported"
                ),
                "normalization": (
                    "Exact production HeatmapSet.to_public default normalization; total retains raw grid mass"
                ),
                "missing": "No default zero grids manufactured for missing players or kinds",
            },
            "physical_accuracy": None,
            "independent_spatial_ground_truth_available": False,
            "inference_performed": False,
            "pipeline_changes": False,
        }
    finally:
        store.close()
    verify_inputs(plan)
    if any(sha(Path(path)) != digest for path, digest in consumed.items()):
        raise ValueError("Original source/detached evidence changed during heatmap export")
    (output / "heatmaps.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    (output / "export_receipt.json").write_text(
        json.dumps(
            {
                "status": "completed",
                "source_run": str(run),
                "canonical_downstream_export_receipt_sha256": sha(receipt_path),
                "source_completion_sha256": sha(finished.report_path),
                "core_plan_sha256": sha(finished.manifest_path),
                "core_plan_current_inputs_verified": True,
                "original_sqlite_opened": False,
                "detached_original_sqlite_opened": False,
                "private_sqlite_copy_used": True,
                "original_and_detached_artifacts_unchanged": True,
                "input_sha256": consumed,
                "exporter_sha256": sha(Path(__file__)),
                "heatmaps_sha256": sha(output / "heatmaps.json"),
            },
            indent=2,
            allow_nan=False,
        )
        + "\n"
    )
    return {"status": "completed", "grid_count": len(grids), "output": str(output)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.artifact_root, args.output)))
