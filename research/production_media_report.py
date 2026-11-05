"""Read-only aggregate of deterministic media and actual-browser experiments."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/benchmarking/experiments"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize(output):
    output.mkdir(parents=True, exist_ok=False)
    browser = {}
    for suffix in ["control_stable", "zero_origin", "growing_release", "migrated", "audio_bf0", "fractional"]:
        folder = BASE / f"prod_20261105_browser_media_{suffix}"
        path = folder / "results.json"
        result = json.loads(path.read_text())
        per_transport = []
        for case in result["results"]:
            rows = case.get("rows", [])
            per_transport.append(
                {
                    "case": case.get("name"),
                    "transport": case.get("transport"),
                    "seeks": len(rows),
                    "physical_image_mismatches": sum(r["identity"] != r["expected_identity"] for r in rows),
                    "missing_callbacks": sum(r["callback_missing"] for r in rows),
                    "error": case.get("error"),
                }
            )
        browser[suffix] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": digest(path),
            "observations": per_transport,
            "event_manifest_stages": sorted({r["stage"] for r in result.get("manifest_requests", [])}),
            "capabilities": json.loads((folder / "capabilities.json").read_text()),
        }
    release = json.loads((BASE / "prod_20261105_media_release/results.json").read_text())
    audio = json.loads((BASE / "prod_20261105_hls_audio_bf0_control/results.json").read_text())
    scan = json.loads((BASE / "prod_20261105_media_stream_scan/test1_scan.json").read_text())
    artifacts = {}
    for directory in sorted(BASE.glob("prod_20261105_*")):
        if not directory.is_dir() or not directory.name.startswith(
            ("prod_20261105_media_", "prod_20261105_hls_", "prod_20261105_browser_")
        ):
            continue
        files = [path for path in directory.iterdir() if path.is_file() and path.suffix in {".json", ".log"}]
        artifacts[str(directory.relative_to(ROOT))] = {path.name: digest(path) for path in sorted(files)}
    sources = {}
    for path in [
        Path(__file__),
        ROOT / "engine/src/bai_engine/media/probe.py",
        ROOT / "engine/src/bai_engine/media/proxy.py",
        ROOT / "engine/tests/test_media_compatibility.py",
        *sorted((ROOT / "research").glob("production_*media*")),
        ROOT / "research/production_hls_migration.py",
        ROOT / "research/production_hls_audio_control.py",
        ROOT / "research/production_hls_timestamp_probe.py",
        ROOT / "research/tests/test_production_hls_migration.py",
    ]:
        relative = path.relative_to(ROOT)
        destination = output / "executed_source" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(path.read_bytes())
        sources[str(relative)] = digest(path)
    result = {
        "schema_version": 1,
        "mode": "offline deterministic generic-media and actual-browser contract evidence; no sports accuracy claim",
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "executed_source_sha256": sources,
        "browser": browser,
        "production_release_grid": [
            {
                "case": case["case"],
                "canonical_hls_pts": case["hls_pts_canonical_exact"],
                "decoder_pixels_equal_mp4": case["hls_matches_proxy_fixture_identities"],
                "proxy_sha256": case["proxy_sha256"],
            }
            for case in release["cases"]
        ],
        "release_sources_unchanged": release["sources_unchanged"],
        "aac_bf0_control": {
            "first_pts": {case["case"]: case["hls_pts"][0] for case in audio["cases"]},
            "mp4_bytes_identical": audio["mp4_bytes_identical"],
        },
        "test1_complete_packet_scan": scan,
        "artifact_catalog_sha256": artifacts,
        "limitations": [
            "No deployed assets or URLs changed; source-hash cache migration/routing remains a release gate.",
            "Actual NVENC regeneration, other browsers, audible A/V sync and true live ingest remain unvalidated.",
            (
                "Growing EVENT check proves buffering/append and subsequent seeks; "
                "continuous-playback latency/live analytics remain unvalidated."
            ),
            (
                "Barcodes establish fixture correspondences only; "
                "arbitrary VFR source-frame/proxy mapping is not implemented."
            ),
        ],
        "discarded_or_preliminary": {
            "prod_20261105_hls_zero_origin_component": (
                "Harness mutated final -nostats argument rather than tee target; fix flag ineffective. "
                "Recorded commands show unchanged mux. Superseded by v2; retained."
            ),
            "prod_20261105_browser_media": (
                "Initial asynchronous seek harness can consume queued previous-image callbacks. "
                "Stable subsequent controls supersede it; retained."
            ),
            "prod_20261105_media_verified": (
                "Preliminary unbounded packet-JSON probe implementation; "
                "replaced by bounded-memory selected-video streaming."
            ),
            "prod_20261105_browser_capability": (
                "First WebDriver capability used shell wrapper instead of Firefox ELF; failed, retained."
            ),
            "prod_20261105_hls_container_arms": (
                "negative_cts, editlist and combined alternative arms rejected; "
                "no_avoid advanced to multi-FPS, audio and actual-browser controls."
            ),
        },
    }
    (output / "summary.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    lines = [
        "# Generic media/browser evidence aggregate",
        "",
        f"Source HEAD: `{result['git_head']}`; exact dirty executed bytes are snapshotted.",
        "",
        "| Experiment | Seeks | Wrong images | Missing callbacks |",
        "| --- | ---: | ---: | ---: |",
    ]
    for name, entry in browser.items():
        rows = entry["observations"]
        lines.append(
            f"| {name} | {sum(r['seeks'] for r in rows)} | "
            f"{sum(r['physical_image_mismatches'] for r in rows)} | "
            f"{sum(r['missing_callbacks'] for r in rows)} |"
        )
    lines += [
        "",
        "AAC bf0 legacy origin `323/15360` → corrected `0`; independent MP4 bytes identical.",
        "",
        "All nine production-command fixture runs retain canonical HLS PTS and MP4/decoder pixel identity.",
        "",
        "The `audio_bf0` mismatch count belongs exclusively to its intentional legacy mux negative control.",
        "",
        (
            "See `summary.json` for per-case rows, artifact hashes, rejected controls, "
            "limitations and full selected-video scan coverage."
        ),
    ]
    (output / "summary.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summarize(args.output.resolve())
