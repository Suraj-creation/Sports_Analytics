"""Describe registered contracts and completed evidence without constructing providers."""

# Long literal sentences are human-readable report/table content.
# ruff: noqa: E501

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import shutil
import subprocess
from pathlib import Path

import yaml

from bai_badminton.components import BASELINE_IMPLEMENTATIONS as DOMAIN_DEFAULTS
from bai_badminton.components import register_domain_components
from bai_badminton.format_understanding import register_format_components
from bai_badminton.perception.components import BASELINE_IMPLEMENTATIONS as PERCEPTION_DEFAULTS
from bai_badminton.perception.components import register_perception_components
from bai_engine.components import ComponentRegistry

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/benchmarking/experiments"
HISTORICAL = BASE / "next_20261105_fresh_air_tracklet_v1"
FRESH = [BASE / "prod_20261105_fresh_association_v1", BASE / "prod_20261105_fresh_association_scene_v1"]

# Human evidence classifications; registry declarations are saved separately.
STAGES = [
    (
        "Input and source",
        "engine/sources.py; API routes/sessions.py",
        "Upload and rights-gated YouTube VOD are wired.",
        "RTSP/SRT/WebRTC/camera enum values are not an implemented true-live ingest path.",
    ),
    (
        "Probe and clock",
        "engine/media/probe.py; timeline.py",
        "Selected-video packet-PTS cadence and exact CFR clock are implemented.",
        "Generic original VFR frame↔CFR proxy correspondence is not persisted as a source-frame map.",
    ),
    (
        "Proxy/HLS/decode",
        "engine/media/proxy.py; decode.py",
        "FFmpeg fMP4 HLS/MP4 and SegmentDecoder execute; current media-origin correction has separate browser controls.",
        "Tiny CFR/VFR/browser tests do not certify all codecs, long streams or live interruption latency.",
    ),
    (
        "Task orchestration",
        "engine/bus.py; runtime/runner.py",
        "LocalBus/RedisBus transport; EngineService and SessionRunner own sequential stages, stop/retry and event storage.",
        "Actual local model-free lifecycle tested; Redis/distributed quota/cancellation and deployment load remain separate.",
    ),
    (
        "Q&A and providers",
        "agents/{agent,providers,tools,kb}.py; API routes/agents.py",
        "Eight read-only tools, six-round loop, grounding repair, sequence fence and deterministic fallback are implemented.",
        "No persistent multi-agent CV research scheduler; remote/local-neural provider accuracy untested; configured session token budget not enforced.",
    ),
    (
        "Plugin and composition",
        "engine/sport.py; engine/components.py; badminton/plugin.py",
        "Explicit sport/provider registries, independent ports, fingerprints and lifecycle contracts.",
        "A declaration or successful construction is not physical component accuracy; provider availability may fail explicitly.",
    ),
    (
        "View and histogram cut",
        "perception/scene.py; events/scene.py",
        "Histogram cut/view/replay heuristics execute in historical and current inference.",
        "Same-camera foreground edits can preserve global histograms.",
    ),
    (
        "Court and camera",
        "perception/{court_lines,camera,calibration_state}.py; court.py",
        "Court lines, homography/camera tracking, recovery and manual calibration paths execute.",
        "Floor projection is not airborne 3D geometry; uncertain calibration and image visibility are distinct.",
    ),
    (
        "Content continuity",
        "perception/{scene_change,content}.py",
        "Optional causal previous-ROI pixel hypothesis; diagnostic or explicit experimental barrier; current scene fresh arm selects it.",
        "Underlying evidence never claims authoritative cut truth; 13 source proposals reviewed by assistant, no independent recall denominator.",
    ),
    (
        "Shuttle perception",
        "perception/{tracknet,diagnostics,isolation}.py",
        "Existing TrackNetV3 eight-frame model, background, masks and opt-in bounded heatmap components execute.",
        "Model support is uncalibrated; masks are image priors; no physical trajectory accuracy from rally F1.",
    ),
    (
        "Shuttle association",
        "perception/association.py",
        "Optional causal co-observed static ambiguity, bounded witnesses/expiry and typed raw-source provenance execute in both new arms.",
        "Raw points remain; no predicted coordinate is substituted; independent association labels missing.",
    ),
    (
        "Player detector",
        "perception/players.py; PlayerDetectorPort",
        "RF-DETR-small executes; detector candidates/ROI rejects and unique fresh matches are distinguishable.",
        "Other locally cached detectors are alternatives, not all executed in this full run; carried boxes are not fresh detections.",
    ),
    (
        "Tracking and identity",
        "perception/{players,player_association}.py; participation.py; identity.py; teams.py",
        "ByteTrack, track episodes, HSV/context continuity and anonymous two/four-player retention execute.",
        "Track, participant, named athlete, team and scoring slot remain separate; no fabricated identity labels.",
    ),
    (
        "Optional neural ReID",
        "perception/offline_reid.py; PlayerReIDPort",
        "OSNet adapter/contract exists and requires pinned FP32 weights.",
        "Weights absent locally and full-run capability explicitly unavailable; no embeddings or ReID accuracy claimed.",
    ),
    (
        "Pose",
        "perception/players.py; PosePort",
        "RTMPose-M executes at declared cadence. New canonical pose_frame_idx records actual valid execution per person.",
        "Legacy absent source stays unknown; a scheduled/non-null pose alone cannot prove freshness; no reviewed keypoint accuracy.",
    ),
    (
        "Racket",
        "perception/racket.py; RacketPort",
        "Weightless OpenCV ellipse/shaft near a wrist executes with actual-frame provenance.",
        "This is geometric evidence, not the optional pretrained RacketVision racket model or a calibrated physical overlap detector.",
    ),
    (
        "OCR",
        "perception/scoreboard.py; score_ocr.py",
        "RapidOCR package-selected detection/classification/recognition execute with actual stage hashes/providers.",
        "rapidocr_v4 is a legacy alias; actual selected run uses PP-OCRv6 det/rec and older cls. OCR is a source-board reading, not a scored point.",
    ),
    (
        "Contact",
        "events/{contact,contact_evidence}.py; participant_contact.py",
        "Default legacy candidate support remains; optional evidence policy separates trajectory, physical impact and actor support.",
        "Lifecycle confirmed is finalization, not physical impact. Automatic probable/ambiguous/insufficient are uncalibrated policy states; external review required for physical confirmed.",
    ),
    (
        "Stroke",
        "events/stroke.py; StrokeClassification",
        "stroke-rules-v0 executes and preserves unknown classes plus parent-impact provenance.",
        "Known heuristic class does not validate contact, named hitter or speed/landing physics; reviewed shot labels absent.",
    ),
    (
        "Optional BST",
        "events/bst.py; _bst_network.py",
        "Implemented verified-weight singles shadow adapter, not selected live classifier or registered default stroke replacement.",
        "Local checkpoint absent; exactly two-player pretrained contract excludes doubles; checkpoint grant not independently verified.",
    ),
    (
        "Activity and rally",
        "events/{activity,rally_fsm,rally_evidence,rally_motion}.py",
        "Independent activity and legacy/evidence/qualified-tracklet rally ports execute; half-open intervals and exactly-once lifecycle retained.",
        "Selected tracklet profile is opt-in development evidence. Curves optional/off; available-window VOD lookahead is not immediate true-live evidence.",
    ),
    (
        "Outcome and score",
        "events/rally_outcome.py; rules/{bwf,doubles}.py",
        "Observed-terminal outcome abstains unknown; BWF scoring applies accepted winners/known format.",
        "No reliable landing or winner is inferred merely from missing shuttle; score rules correctness is not winner-estimation accuracy.",
    ),
    (
        "Format and doubles",
        "format_understanding.py; teams.py; analytics/doubles_service.py",
        "Configured or sustained fresh target-court format contract plus independent four-player/team/service estimates.",
        "Configured names/format do not bind athletes. No reviewed four-player accuracy or prospective held-out validation.",
    ),
    (
        "Analytics and storage",
        "analytics/*; TransactionalAnalytics; engine/store/*",
        "Append-only event fold, journal checkpoint/rollback, match/individual/reviewed/estimated views and heatmaps exist.",
        "Counts and aggregates inherit parent uncertainty; old estimates remain labelled, not silently converted into reviewed statistics.",
    ),
    (
        "API, wire and browser",
        "API routes/ws; web/lib/{socket,tracks}; player/overlay",
        "Wire v2 pf source fields and v1 legacy reads, revision fences, anonymous doubles boxes and estimate labels are implemented.",
        "poseObservedFrame is stored truthfully; historical displayPose age/badge still uses display sample frame, not canonical pf. No UI physical-freshness claim.",
    ),
    (
        "Exports and evaluation",
        "API routes/exports.py; engine/evaluation.py; research/evaluation",
        "JSONL, application CSV/legacy CSV/PDF/summary/clips and separate unchanged rally evaluator exist.",
        "Seven-column benchmark CSV is a separate contract. Application official-rally filters and eight-column legacy CSV must not be confused with benchmark matching.",
    ),
    (
        "Unwired optional stages",
        "Profile fields; plugin.capabilities",
        "shuttle_live, shuttle_second_opinion and inpaint settings are declared and reported unsupported when requested.",
        "RacketVision-balltrack has no runtime adapter; wasb_badminton is not in the model manifest; cached InpaintNet is not integrated. Escalation/racket-window settings do not establish event-triggered specialists.",
    ),
]


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    out, report = args.output.resolve(), args.report.resolve()
    out.mkdir(parents=True, exist_ok=False)
    if report.exists():
        raise FileExistsError(report)

    class DescribeOnlyRegistry(ComponentRegistry):
        def create(self, *args, **kwargs):
            raise AssertionError("inventory must never construct a provider")

    registry = DescribeOnlyRegistry()
    for register in (register_domain_components, register_perception_components, register_format_components):
        register(registry)
    contracts = registry.describe()
    assert len(contracts) == 22
    model_manifest = yaml.safe_load((ROOT / "models/manifest.yaml").read_text())["models"]
    lock = json.loads((ROOT / "models/cache/lock.json").read_text())
    models = []
    for name, spec in model_manifest.items():
        source = spec.get("source", {})
        filename = Path(source.get("file") or source.get("url", name).rsplit("/", 1)[-1]).name
        artifact = ROOT / "models/cache" / name / filename
        pin = spec.get("sha256")
        expected = lock.get(name) if pin in (None, "pin-on-first-fetch") else pin
        actual = sha(artifact) if artifact.is_file() else None
        if actual is not None and expected is not None:
            assert actual == expected, name
        models.append(
            {
                "name": name,
                "task": spec["task"],
                "format": spec["format"],
                "registry_status": spec.get("status", "active"),
                "recorded_license": spec.get("license", "unknown"),
                "source": source,
                "pinned_sha256": expected,
                "local_file": str(artifact.relative_to(ROOT)),
                "local_file_present": artifact.is_file(),
                "local_file_sha256": actual,
                "package_installed_version": version(source["package"]) if "package" in source else None,
                "availability_scope": "builtin"
                if spec["format"] == "builtin"
                else "package availability is not model-weight pinning"
                if spec["format"] == "package"
                else "exact local file existence and digest only, not loading or accuracy",
            }
        )
    runs = []
    for directory in [HISTORICAL, *FRESH]:
        inference = json.loads((directory / "inference.json").read_text())
        metadata = json.loads((directory / "benchmark_metadata.json").read_text())
        assert inference["status"] == "analysed"
        runs.append(
            {
                "directory": str(directory.relative_to(ROOT)),
                "source_commit": metadata["git_commit_sha"],
                "source_video_sha256": metadata["source_video_sha256"],
                "prediction_sha256": sha(directory / "predicted_rallies.csv"),
                "inference_sha256": sha(directory / "inference.json"),
                "metadata_sha256": sha(directory / "benchmark_metadata.json"),
                "components": inference["pipeline"]["components"],
                "profile": inference["effective_profile"],
                "execution_backends": inference["execution_backends"],
                "degraded": inference["degraded"],
                "runtime_seconds": inference["elapsed_seconds"],
                "offline_frames_per_second": inference["frames_per_second"],
                "per_stage_seconds": inference["per_stage_seconds"],
                "resources": inference["resources"],
                "event_counts": inference["event_counts"],
                "own_semantic_trace_validation": "historical verified"
                if directory == HISTORICAL
                else "pending orchestrator own-cache audit at inventory creation",
            }
        )
    packages = {
        name: version(name)
        for name in [
            "torch",
            "onnxruntime-gpu",
            "onnxruntime",
            "opencv-python",
            "numpy",
            "pyarrow",
            "pydantic",
            "av",
            "msgpack",
            "rtmlib",
            "trackers",
            "supervision",
            "rapidocr",
            "fastapi",
            "redis",
            "openai",
            "anthropic",
        ]
    }
    inventory = {
        "schema": "production-component-inventory:v1",
        "mode": "read-only describe-only registry plus completed artifacts and file hashes",
        "commit_at_inventory": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "provider_factories_called": 0,
        "models_constructed": 0,
        "inference_launched": False,
        "media_or_labels_opened": False,
        "contracts": contracts,
        "domain_defaults": DOMAIN_DEFAULTS,
        "perception_implementation_defaults": PERCEPTION_DEFAULTS,
        "defaults_scope": "Implementation fallback when a stage is selected; optional ReID/content/association are not enabled merely by appearing here.",
        "stages": [
            dict(zip(("stage", "source", "implemented_or_executed", "limits"), row, strict=True)) for row in STAGES
        ],
        "model_artifacts": models,
        "package_versions": packages,
        "completed_runs": runs,
        "license_scope": "Exact preserved registry strings only; no new legal clearance, publisher authentication, training-data or video rights claim.",
        "realtime_scope": "Offline pipeline throughput below source 30fps; lead-buffered VOD, not real-time production or true-live validation.",
    }
    (out / "component_inventory.json").write_text(json.dumps(inventory, indent=2) + "\n")
    sources = [
        Path(__file__),
        ROOT / "engine/src/bai_engine/components.py",
        ROOT / "sports/badminton/src/bai_badminton/components.py",
        ROOT / "sports/badminton/src/bai_badminton/perception/components.py",
        ROOT / "sports/badminton/src/bai_badminton/format_understanding.py",
        ROOT / "models/manifest.yaml",
        ROOT / "models/cache/lock.json",
        ROOT / "engine/src/bai_engine/sources.py",
        ROOT / "engine/src/bai_engine/media/probe.py",
        ROOT / "engine/src/bai_engine/media/proxy.py",
        ROOT / "engine/src/bai_engine/runtime/runner.py",
        ROOT / "sports/badminton/src/bai_badminton/plugin.py",
        ROOT / "sports/badminton/src/bai_badminton/perception/pipeline.py",
        ROOT / "sports/badminton/src/bai_badminton/perception/players.py",
        ROOT / "agents/src/bai_agents/agent.py",
        ROOT / "agents/src/bai_agents/tools.py",
        ROOT / "agents/src/bai_agents/providers.py",
        ROOT / "apps/api/src/bai_api/routes/agents.py",
        ROOT / "apps/api/src/bai_api/routes/exports.py",
        ROOT / "apps/web/src/lib/tracks.ts",
        ROOT / "apps/web/src/features/player/overlay.ts",
        ROOT / "research/GPU_PERFORMANCE_REPORT.md",
        BASE / "prod_20261105_runtime_gpu1_v2/runtime_probe.json",
    ]
    hashes = {}
    for path in sources:
        relative = path.relative_to(ROOT)
        hashes[str(relative)] = sha(path)
        target = out / "source" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    (out / "source_sha256.json").write_text(json.dumps(hashes, indent=2) + "\n")
    lines = [
        "# Actual component inventory",
        "",
        "## Evidence boundary",
        "",
        "This inventory invokes all three explicit registration functions and `ComponentRegistry.describe()` only. A guard prohibits `create()`: zero factories, providers or models are constructed. It reads source, package metadata, existing local model files and completed run JSON; it opens no media, annotations or sealed labels and launches no inference, GPU job or encode. The exact 22 contracts, model hashes, selected configurations, actual runtime/degradation records and source snapshots are saved separately.",
        "",
        "Registration declares compatibility, required evidence, devices, schema, lifecycle and failure policy. It does not prove a provider can load, that a declared backend executed, or that a physical event is accurate. `supported_formats=[singles,doubles,unknown]` means acquisition/abstention compatibility, not reviewed doubles accuracy. The implementation defaults below are distinct from optional-stage enablement and the research-selected rally profile.",
        "",
        "## Implemented, executed and unwired responsibilities",
        "",
        "| Component | Owner/source | Actual status | Limitation/fallback |",
        "|---|---|---|---|",
    ]
    lines += [f"| {stage} | `{source}` | {status} | {limit} |" for stage, source, status, limit in STAGES]
    lines += [
        "",
        "## Exact registry snapshot",
        "",
        "| Kind | Implementation | Version / output schema | State / failure |",
        "|---|---|---|---|",
    ]
    for contract in contracts:
        lines.append(
            f"| {contract['kind']} | {contract['implementation']} | {contract['version']} / {contract['output_schema']} | {'stateful' if contract['stateful'] else 'stateless port'} / {contract['failure_policy']} |"
        )
    lines += [
        "",
        "The domain implementation defaults are participant-identity-v1, contact-fusion-v1, stroke-rules-v0, temporal-activity-v3, rally-fsm-v1, observed-terminal-v1, bwf-rally-point-v1 and match-analytics-v1. The selected development runs explicitly choose rally-evidence-tracklets-v1; they do not promote it to the application default. Current contact contracts carry v3 output evidence while the historical run used older metadata: identical implementation IDs do not imply identical source/schema executions.",
        "",
        "## Models and dependency availability",
        "",
        "License strings below are preserved local registry declarations, not independent legal clearance. First-fetch pins establish subsequent integrity, not publisher authenticity, safe deserialization or rights to training/video data. Builtins have no weights; a package alias is not a pinned checkpoint. Full digests, actual local-file hashes, URLs, package versions and recorded runtime OCR stage hashes are in the JSON artifact.",
        "",
        "| Model | Local state | Pin/file SHA-256 | Recorded license scope |",
        "|---|---|---|---|",
    ]
    for model in models:
        state = (
            "builtin"
            if model["format"] == "builtin"
            else f"package {model['package_installed_version'] or 'absent'}"
            if model["format"] == "package"
            else "file verified"
            if model["local_file_present"]
            else "file absent"
        )
        lines.append(
            f"| {model['name']} | {state} | `{model['local_file_sha256'] or model['pinned_sha256'] or 'none'}` | {model['recorded_license']} |"
        )
    lines += [
        "",
        "The RTMPose-X name contains `halpe26`, but its manifest explicitly identifies a body7 384×288 export with heel/toe work still deferred. It must not be advertised as demonstrated 26-keypoint inference. Optional RacketVision/BST/ReID absence is distinct from missing adapters; cached InpaintNet has weights but is still unwired. `wasb_badminton` is referenced by profiles but absent from the manifest. TensorRT appearing in a contract or ORT advertised-provider list is not a verified TensorRT engine.",
        "",
        "## Actual execution evidence and throughput",
        "",
        "| Completed run | Source | Offline seconds / FPS | Degradation |",
        "|---|---|---|---|",
    ]
    for run in runs:
        degradation = "; ".join(f"{item['stage']}: {item['reason']}" for item in run["degraded"]) or "none recorded"
        lines.append(
            f"| {Path(run['directory']).name} | `{run['source_commit'][:12]}` | {run['runtime_seconds']:.3f} / {run['offline_frames_per_second']:.5f} | {degradation} |"
        )
    lines += [
        "",
        "The two new full-pipeline runs completed while this inventory was prepared; their exact own-cache semantic audits and boundary investigations are still pending here. Their throughput is measured during concurrent runs on separate leased GTX1080Ti cards and shared CPU resources. The ~10 FPS quality-mode rates are below the 30 FPS source, so neither this measurement nor buffered VOD playback is a real-time claim. Stage times overlap/nest and must not be summed as independent critical-path fractions.",
        "",
        "Historical actual runtime records show TrackNet Torch CUDA FP16 and OpenCV CPU racket geometry, with ONNX CUDA+CPU provider registration for detector, pose and OCR. The separate executed-node probe confirms 758 RF-DETR CUDA nodes and RTMPose 185 CUDA plus two CPU shape nodes for its fixed inputs. It does not profile OCR or every full-video invocation. ONNX image tensors there are FP32 despite YAML precision=fp16. No TensorRT execution, TF32 arithmetic, RTX4000Ada throughput or optional-model inference is inferred from configuration strings.",
        "",
        "RapidOCR's legacy alias `rapidocr_v4` resolved in the historical run to package3.10.0 with PP-OCRv6 det/rec and a mobile v2 classification graph. Actual weight hashes and all stage providers are retained in the runtime JSON. Missing OSNet is explicit degradation; neither constant embeddings nor names are substituted. Locally present alternate detector/pose files establish integrity/availability only; this inventory does not load them.",
        "",
        "## Explicitly unresolved system contracts",
        "",
        "True-live ingestion remains unwired even though SourceKind and profile fields exist. VFR is detected from packet PTS and converted to canonical CFR, but the generic original-source frame↔proxy correspondence map is absent. A corrected/browser-tested presentation origin is not a full VFR provenance map or proof of RTSP/SRT/WebRTC causality. The current source-clock and browser reports own their exact tested scope.",
        "",
        "Frontend wire v2 preserves canonical `poseObservedFrame`; absent legacy pf remains null. Existing displayPose/overlay rendering still derives display hold age from stored sample frames and does not consume pf as a physical freshness badge. This inventory therefore claims provenance transport, not UI physical freshness. Existing machine/reviewed labels distinguish estimates from human events; they do not verify contacts, strokes or identities.",
        "",
        "The Q&A agent can fall back deterministically when its provider is unavailable. It never schedules perception or writes reviewed sporting truth. Its configured token budget has no durable consumption/reservation enforcement. Local scripted-provider and service lifecycle tests establish software behavior, not remote model accuracy, distributed durability or deployment reliability.",
        "",
        "Independent source-bound labels for physical impacts, first/last sporting observations, player identities, shot classes, landmarks and match-disjoint four-player doubles remain missing. The dataset manifest has zero eligible prospective held-out recordings. No component-performance claim is manufactured from complete software tests or Test1 rally F1. Experimental profiles remain unsuitable for production promotion.",
        "",
        f"Artifact: `{out.relative_to(ROOT)}/component_inventory.json`; exact registration/source provenance: `source_sha256.json` and `source/`.",
        "",
    ]
    report.write_text("\n".join(lines))
    (out / "report_sha256.json").write_text(json.dumps({str(report.relative_to(ROOT)): sha(report)}, indent=2) + "\n")
    print(
        json.dumps(
            {
                "contracts": len(contracts),
                "stages": len(STAGES),
                "model_entries": len(models),
                "factories_called": 0,
                "report": str(report),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
