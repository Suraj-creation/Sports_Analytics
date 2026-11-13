"""Explicit-path export of frozen native canonical Test2 heatmaps.

Derived from export_test02_heatmaps.export: only input/import boundary changed.
The detached ledger checks, canonical build, grid normalization and policies are
unchanged. Does not add navigation files to the original failed orchestration.
"""

from __future__ import annotations

import argparse
import ast
import collections
import hashlib
import inspect
import json
import shutil
from pathlib import Path


def export(run, downstream, output, producer_root):
    """Use the frozen producer's canonical rebuild on explicit detached exports."""
    import importlib

    run, downstream = Path(run).resolve(strict=True), Path(downstream).resolve(strict=True)
    output, producer_root = Path(output).resolve(), Path(producer_root).resolve(strict=True)
    native = importlib.import_module("evaluation.ground_truth_validation.orchestration.evaluate_test02_components")
    semantic = importlib.import_module("research.production_external_semantic_replay")
    stress = importlib.import_module("research.production_external_stress")
    rebuild = importlib.import_module("bai_badminton.analytics.rebuild")
    schema = importlib.import_module("bai_engine.schema")
    storage = importlib.import_module("bai_engine.store")
    for module in (native, semantic, stress, rebuild, schema, storage):
        if not Path(module.__file__).resolve().is_relative_to(producer_root):
            raise ValueError("Actual frozen native producer imports required: " + module.__name__)
    if native.ROOT.resolve() != producer_root or semantic.ROOT.resolve() != producer_root:
        raise ValueError("Producer ROOT must be actual original checkout")
    media_spec, source_sha = native.MEDIA, native.TEST2_SHA
    read, sha, load_finished_input = native.read, native.sha, semantic.load_finished_input
    verify_inputs, build = stress.verify_inputs, rebuild.build
    event_class, event_store, track_store = schema.Event, storage.EventStore, storage.TrackStore
    if output.exists() or any(
        output == protected or protected in output.parents or output in protected.parents
        for protected in (run, downstream, producer_root)
    ):
        raise ValueError("Heatmaps require a new output separate from original run")
    session = read(run / "session.json")
    sid = session["session_id"]
    if session["source"].get("sha256") != source_sha:
        raise ValueError("Requires original Test2 source")
    finished = load_finished_input(run, sid)
    inference = read(finished.report_path)
    parent = read(run.with_suffix(".executor.json"))
    if (
        inference.get("status") != "completed"
        or inference.get("cached_perception_used") is not False
        or inference.get("frames_processed") != media_spec[-1]
        or parent.get("status") != "completed"
        or parent.get("worker_exit_code") != 0
        or parent.get("frozen_source_inputs_unchanged") is not True
    ):
        raise ValueError("Heatmap export requires fresh completed unchanged source execution")
    if (
        finished.layout != "production-full-upload"
        or tuple(finished.media[k] for k in ("width", "height", "fps_num", "fps_den", "n_frames")) != media_spec
    ):
        raise ValueError("Requires completed full canonical Test2 upload")
    plan = read(finished.manifest_path)
    verify_inputs(plan)
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
    native_export = importlib.import_module("evaluation.ground_truth_validation.orchestration.export_test02_heatmaps")
    if (
        Path(native_export.__file__).resolve().parent
        != producer_root / "evaluation/ground_truth_validation/orchestration"
    ):
        raise ValueError("Original native heatmap source required")
    consumed[str(Path(native_export.__file__).resolve())] = sha(Path(native_export.__file__))
    origin_ast_sha = hashlib.sha256(
        ast.dump(ast.parse(inspect.getsource(native_export.export)), include_attributes=False).encode()
    ).hexdigest()

    class CanonicalNames(ast.NodeTransformer):
        def visit_Name(self, node):
            aliases = {
                "event_class": "Event",
                "event_store": "EventStore",
                "track_store": "TrackStore",
                "media_spec": "MEDIA",
                "source_sha": "TEST2_SHA",
            }
            return ast.copy_location(ast.Name(id=aliases.get(node.id, node.id), ctx=node.ctx), node)

    def canonical_fold_core(function):
        tree = ast.parse(inspect.getsource(function))
        core = next(node for node in ast.walk(tree) if isinstance(node, ast.Try))
        return ast.dump(CanonicalNames().visit(core), include_attributes=False)

    if canonical_fold_core(export) != canonical_fold_core(native_export.export):
        raise ValueError("Canonical heatmap rebuild/extraction differs from original native function")
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
        event_class.model_validate_json(line) for line in finished.events_path.read_text().splitlines() if line
    ]
    original_events.sort(key=lambda e: e.seq if e.seq is not None else -1)
    output.mkdir(parents=True)
    work = output / "working"
    work.mkdir()
    for suffix in ("", "-wal", "-shm"):
        source = detached / ("events.sqlite" + suffix)
        if source.is_file():
            shutil.copyfile(source, work / source.name)
    store = event_store(work / "events.sqlite", sid)
    try:
        restored = store.since(0, limit=len(original_events) + 1)
        if len(restored) != len(original_events):
            raise ValueError("Detached event population differs from original append-only ledger")
        for original, copied in zip(original_events, restored, strict=True):
            if original.model_dump(exclude={"seq"}) != copied.model_dump(exclude={"seq"}):
                raise ValueError("Detached event content/order/correction lineage differs")
        folded = build(store, track_store(detached_tracks), media_spec[2] / media_spec[3])
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
            "source_sha256": source_sha,
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
                "producer_root": str(producer_root),
                "explicit_detached_downstream": str(downstream),
                "producer_ROOT_reassigned": False,
                "numeric_heatmap_policy_changed": False,
                "native_canonical_fold_core_AST_equal": True,
                "native_export_function_AST_sha256": origin_ast_sha,
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
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--downstream", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--producer-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.run, args.downstream, args.output, args.producer_root)))
