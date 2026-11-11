"""Actual isolated Test2 HTTP/Firefox coverage, no inference or provider call."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research import production_product_smoke as smoke  # noqa: E402
from research.production_external_semantic_replay import load_finished_input  # noqa: E402


def run(completed_run: Path, output: Path, build: Path, completion_recovery: Path | None = None):
    source_session = json.loads((completed_run / "session.json").read_text())
    finished = load_finished_input(completed_run, source_session["session_id"], completion_recovery=completion_recovery)
    original = smoke.check_completed_product

    def extended(seed, directory, app_base, navigate, js, wait, screenshot):
        result = original(seed, directory, app_base, navigate, js, wait, screenshot)
        sid = seed["expected"]["session_id"]
        frame_count = seed["expected"]["media"]["n_frames"]
        responses = {}
        endpoints = {
            "analytics": "analytics",
            "individual": "individual-analytics",
            "estimated_individual": "estimated-individual-analytics",
            "highlights": "highlights?k=10",
            "insights": "insights",
            "state": "state",
            "provider_status_only": "ask/provider",
            "heatmap_P1_presence": "heatmap?player=P1&kind=presence",
            "heatmap_P2_presence": "heatmap?player=P2&kind=presence",
            "heatmap_P1_movement": "heatmap?player=P1&kind=movement",
            "heatmap_P2_movement": "heatmap?player=P2&kind=movement",
        }
        for name, endpoint in endpoints.items():
            response = smoke.http(app_base, f"/api/sessions/{sid}/{endpoint}")
            payload = json.loads(response["body"])
            smoke.dump(
                directory / "evidence" / f"test2_{name}.json", {"status": response["status"], "payload": payload}
            )
            if response["status"] != 200:
                raise AssertionError(f"Test2 endpoint {endpoint} failed: {response['status']}")
            responses[name] = payload
        summary = json.loads((directory / "evidence/summary.json").read_text())
        if summary["session"]["session_id"] != sid:
            raise AssertionError("Summary lost Test2 session binding")
        if summary["session"]["source"]["sha256"] != seed["expected"]["source_sha256"]:
            raise AssertionError("Summary lost Test2 source binding")
        if summary["analytics"] != responses["analytics"]:
            raise AssertionError("Summary/API analytics are inconsistent")
        if summary["highlights"] != responses["highlights"]["highlights"]:
            raise AssertionError("Summary/API highlights are inconsistent")
        events = [json.loads(line) for line in (directory / "evidence/events.jsonl").read_text().splitlines()]
        ids = {event["event_id"] for event in events}
        highlight_checks = []
        for highlight in responses["highlights"]["highlights"]:
            refs = highlight.get("evidence_ids", [])
            valid = bool(refs) and set(refs).issubset(ids)
            in_range = 0 <= highlight["frame_start"] < highlight["frame_end"] <= frame_count
            highlight_checks.append(
                {
                    "rally_id": highlight["rally_id"],
                    "references": len(refs),
                    "all_references_in_export": valid,
                    "bounds_valid": in_range,
                    "evidence_status": highlight.get("evidence_status"),
                }
            )
            if not valid or not in_range:
                raise AssertionError("A Test2 highlight lacks same-session evidence or valid bounds")
        screenshots = []
        panels = {
            "overview": None,
            "moments": "The moments worth another look",
            "rallies": None,
            "court": "How did you use the court?",
            "movement": None,
            "h2h": "The two sides, compared",
            "ask": "Ask about what happened",
        }
        for tab, heading in panels.items():
            navigate(f"/sessions/{sid}?tab={tab}")
            wait(
                lambda: js("return document.body.innerText.includes('Analysed') && !!document.querySelector('video');")
            )
            wait(lambda: js("return !document.body.innerText.includes('Loading recorded analysis');"))
            if heading is not None:
                wait(lambda heading=heading: js("return document.body.innerText.includes(arguments[0]);", [heading]))
            wait(lambda: js("return document.querySelector('video')?.readyState>=2;"))
            screenshot(f"test2_{tab}")
            state = js(
                "return {title:document.title,text:document.body.innerText,"
                "video:{duration:document.querySelector('video').duration,"
                "width:document.querySelector('video').videoWidth,"
                "height:document.querySelector('video').videoHeight}};"
            )
            if source_session["title"] not in state["text"]:
                raise AssertionError("The browser does not identify its actual completed source session")
            for case in ("test1", "test2", "test7", "india", "denmark", "doubles", "amateur"):
                title = f"Fresh complete upload: {case}"
                if title != source_session["title"] and title in state["text"]:
                    raise AssertionError("Foreign source session appears in completed results")
            screenshots.append(
                {"tab": tab, "video": state["video"], "source_session_exact": True, "text_chars": len(state["text"])}
            )
        request_rows = [json.loads(line) for line in (directory / "requests.jsonl").read_text().splitlines()]
        ask_posts = [
            row for row in request_rows if row.get("method") == "POST" and row.get("path", "").endswith("/ask")
        ]
        if ask_posts:
            raise AssertionError("A provider request unexpectedly ran in technical product validation")
        result["source_bound_extended"] = {
            "http_endpoints": list(endpoints),
            "all_endpoint_statuses": 200,
            "summary_analytics_equal": True,
            "summary_highlights_equal": True,
            "summary_kind": "deterministic session/analytics/highlights export; no LLM synthesis",
            "provider_calls": 0,
            "provider_status_only": responses["provider_status_only"],
            "highlight_evidence_checks": highlight_checks,
            "browser_panels": screenshots,
            "sporting_accuracy_validated": False,
            "source_report_sha256": smoke.digest(finished.report_path),
            "component_accuracy_limit": "Transport, evidence references and model coverage only; no component labels.",
        }
        return result

    smoke.check_completed_product = extended
    try:
        return smoke.run(
            output,
            build,
            smoke.DEFAULT_FIXTURE,
            completed_run=completed_run,
            expect_fixes=True,
            completion_recovery=completion_recovery,
        )
    finally:
        smoke.check_completed_product = original
        if output.is_dir():
            (output / "pipeline_repair_product.py").write_bytes(Path(__file__).read_bytes())
            command = {
                "argv": sys.argv,
                "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "source_report_sha256": smoke.digest(finished.report_path),
                "scope": "Own completed run copied read-only into isolated product; no neural or LLM inference",
            }
            smoke.dump(output / "test2_executor_receipt.json", command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--completed-run", type=Path, required=True)
    parser.add_argument("--completion-recovery", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--build", type=Path, required=True)
    args = parser.parse_args()
    result = run(
        args.completed_run.resolve(strict=True),
        args.output.resolve(),
        args.build.resolve(strict=True),
        args.completion_recovery.resolve(strict=True) if args.completion_recovery else None,
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "output": str(args.output),
                "completed_neural_product": result["completed_neural_product"],
            },
            indent=2,
        )
    )
