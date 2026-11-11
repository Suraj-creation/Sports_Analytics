"""Source-bound offline failure cases from genuine completed inference and replay.

No inference or annotation conversion is performed. The source PTS map must
prove exact zero-origin CFR correspondence; this tool deliberately refuses to
invent a mapping for VFR, trimmed, offset or differing-rate media.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def write(path: Path, value) -> None:
    with path.open("x") as stream:
        json.dump(value, stream, allow_nan=False, separators=(",", ":"))
        stream.write("\n")


def verified_pts(path: Path, n_frames: int, rate: Fraction) -> dict[int, tuple[int, Fraction]]:
    """Bind every source frame to exact PTS; decimal display values are unused."""
    result = {}
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        expected = ["source_frame", "pts", "time_base_num", "time_base_den", "source_time_sec"]
        if reader.fieldnames != expected:
            raise ValueError("source frame PTS audit schema differs")
        for index, row in enumerate(reader):
            frame, pts = int(row["source_frame"]), int(row["pts"])
            time_base = Fraction(int(row["time_base_num"]), int(row["time_base_den"]))
            if frame != index or pts < 0 or time_base <= 0 or pts * time_base != Fraction(frame, 1) / rate:
                raise ValueError("source PTS map is not exact ordered zero-origin CFR")
            result[frame] = pts, time_base
    if list(result) != list(range(n_frames)):
        raise ValueError("source PTS map does not cover the full input")
    return result


def verify_replay(proof: dict, recorded, trace_path: Path, traces: list[dict], sid: str) -> None:
    n = recorded.media["n_frames"]
    if (
        proof.get("schema") != "cached-external-semantic:v2"
        or proof.get("baseline_parity") is not True
        or proof.get("geometry_bracket") is not False
        or proof.get("contact_motion_reliability") is not False
        or proof.get("no_GT_or_neural_model_input") is not True
        or proof.get("session_id") != sid
        or proof.get("source_report_sha256") != sha(recorded.report_path)
        or proof.get("cache_sha256") != recorded.expected_caches
        or proof.get("frames") != n
        or proof.get("trace_step_count") != n
    ):
        raise ValueError("exact own-source baseline replay proof required")
    if proof.get("output_artifact_sha256", {}).get(trace_path.name) != sha(trace_path):
        raise ValueError("replay manifest must bind the actual trace digest")
    steps = [row["frame"] for row in traces if row.get("call") == "step"]
    if steps != list(range(n)):
        raise ValueError("replay must retain exactly every ordered step frame")


def case_ranges(
    case: dict, predictions: list[dict], frame_count: int, ground_truth: list[dict] | None = None
) -> tuple[list[tuple[int, int]], tuple[int, int]]:
    """Half-open source windows at EVERY relevant boundary; never pick by score."""
    intervals = []
    if "gt_start_frame" in case:
        intervals.append((case["gt_start_frame"], case["gt_end_frame"]))
    if case.get("pred_start_frame") is not None:
        intervals.append((case["pred_start_frame"], case["pred_end_frame"]))
    if case["matching_status"] == "unmatched_prediction":
        intervals.append((case["start_frame"], case["end_frame"]))
    for number in case.get("positive_overlap_prediction_ids", []):
        prediction = predictions[number - 1]
        intervals.append((prediction["start_frame"], prediction["end_frame"]))
    for number in case.get("positive_overlap_gt_ids", []):
        if ground_truth is None:
            raise ValueError("overlapping ground-truth intervals required for unmatched prediction context")
        annotation = ground_truth[number - 1]
        intervals.append((annotation["start_frame"], annotation["end_frame"]))
    if not intervals:
        raise ValueError("case has no source interval")
    radius = 45 if case["matching_status"] != "matched" else 30
    anchors = sorted({boundary for interval in intervals for boundary in interval})
    windows = [(max(0, frame - radius), min(frame_count, frame + radius + 1)) for frame in anchors]
    return merge_ranges(windows), (
        max(0, min(interval[0] for interval in intervals) - 45),
        min(frame_count, max(interval[1] for interval in intervals) + 46),
    )


def merge_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    merged = []
    for start, end in sorted(ranges):
        if not 0 <= start < end:
            raise ValueError("invalid source replay range")
        if merged and start <= merged[-1][1]:
            merged[-1] = merged[-1][0], max(end, merged[-1][1])
        else:
            merged.append((start, end))
    return merged


def finite_json(value):
    """Preserve missing values and render recorded nonfinite floats explicitly."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: finite_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite_json(item) for item in value]
    return value


def projected(matrix, xy):
    if not matrix or None in xy:
        return None
    x, y = xy
    denominator = matrix[6] * x + matrix[7] * y + matrix[8]
    if denominator == 0:
        return None
    return [
        (matrix[0] * x + matrix[1] * y + matrix[2]) / denominator,
        (matrix[3] * x + matrix[4] * y + matrix[5]) / denominator,
    ]


HTML = """<!doctype html><meta charset=utf-8><title>Test2 source-bound failure replay</title>
<style>body{font:15px system-ui;background:#151920;color:#edf0f7;margin:24px}button,select{font:inherit;padding:8px}
#stage{position:relative;max-width:960px}img{width:100%;display:block}canvas{position:absolute;inset:0;width:100%;height:100%}
input{width:min(940px,95vw)}pre{white-space:pre-wrap;background:#242b35;padding:12px;max-width:940px}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:10px 0}a{color:#9dc7ff}</style>
<h1>Test2 source-bound failure replay</h1><p>Original source pixels and exact PTS. Model evidence and
offline legacy reference boundaries are diagnostic; physical correctness requires independent review.</p>
<div class=row><select id=cases></select><select id=windows></select><button id=play>Play</button>
<label><input id=overlay type=checkbox checked style=width:auto>Evidence overlay</label>
<a id=detail>Full case JSON</a></div>
<div id=stage><img id=frame><canvas id=marks></canvas></div><input id=seek type=range min=0 step=1>
<pre id=info></pre><script>const D=__DATA__;const E=id=>document.getElementById(id);let current=[],timer=null;
const caseNames=Object.keys(D.cases);for(const name of caseNames){const o=document.createElement('option');
o.value=name;o.textContent=name;E('cases').append(o)}function chooseCase(){const c=D.cases[E('cases').value];
E('windows').replaceChildren();c.windows.forEach((r,i)=>{const o=document.createElement('option');o.value=i;
o.textContent=`Frames ${r[0]}–${r[1]-1}`;E('windows').append(o)});
E('detail').href='cases/'+E('cases').value+'.json';chooseWindow()}
function chooseWindow(){const r=D.cases[E('cases').value].windows[+E('windows').value];current=[];
for(let f=r[0];f<r[1];f++)current.push(f);E('seek').max=current.length-1;E('seek').value=0;show()}
function show(){const n=current[+E('seek').value],f=D.frames[n];E('frame').src=`frames/${n}.jpg`;
E('info').textContent=JSON.stringify({source_frame:n,source_pts:f.pts,time_base:f.time_base,
timestamp_seconds:f.timestamp_seconds,raw_shuttle:f.raw_xy,raw_support:f.raw_support,
processed_xy:f.processed_xy,view:f.view,calibration:f.calibration,association:f.association,
contacts:f.contacts,state:f.fsm,transitions:f.transitions,
case_evaluation:D.cases[E('cases').value].evaluation},null,2);draw(f)}
function draw(f){const c=E('marks');c.width=D.display_size[0];c.height=D.display_size[1];const x=c.getContext('2d');
if(!E('overlay').checked)return;const sx=c.width/D.proxy_size[0],sy=c.height/D.proxy_size[1];
function point(p,color){if(!p)return;x.strokeStyle=color;x.lineWidth=2;x.beginPath();
x.arc(p[0]*sx,p[1]*sy,6,0,7);x.stroke()}
point(f.raw_xy,'#ffda57');point(f.processed_xy,'#53e5fb');for(const p of f.people){if(!p.b)continue;
x.strokeStyle=p.dm?'#7df594':'#ee9dfd';x.strokeRect(p.b[0]*sx,p.b[1]*sy,(p.b[2]-p.b[0])*sx,(p.b[3]-p.b[1])*sy);
x.fillStyle='white';x.font='13px monospace';x.fillText(`${p.t} pose:${p.pf} racket:${p.rf}`,p.b[0]*sx,p.b[1]*sy-4)}
x.fillStyle='#10141cbb';x.fillRect(0,0,c.width,48);x.fillStyle='white';x.font='15px monospace';
const caption=`source ${current[+E('seek').value]} | ${f.timestamp_seconds.toFixed(6)}s | raw yellow / processed cyan`;
x.fillText(caption,8,18);const n=current[+E('seek').value];
const active=rows=>rows.map((r,i)=>r.start_frame<=n&&n<r.end_frame?i+1:null).filter(v=>v!==null);
x.fillText(`Legacy reference G${active(D.ground_truth)} | prediction P${active(D.predictions)}`,8,39)}
E('cases').onchange=chooseCase;E('windows').onchange=chooseWindow;E('seek').oninput=show;E('overlay').onchange=show;
E('play').onclick=()=>{if(timer){clearInterval(timer);timer=null;E('play').textContent='Play';return}
E('play').textContent='Pause';timer=setInterval(()=>{E('seek').value=(+E('seek').value+1)%current.length;show()},1000/D.fps)};
if(caseNames.length)chooseCase();</script>"""


def content_transition_summary(raw, all_frames):
    """Separate measured evidence, hypotheses and actual tracking-epoch resets."""
    return {
        "content_evidence_frames": [row["f"] for row in raw if row.get("cc") is not None],
        "content_hypothesis_frames": [row["f"] for row in raw if (row.get("cc") or {}).get("hypothesis") is True],
        "content_change_frames": [
            row["f"]
            for row in raw
            if row["f"] > 0 and row["f"] - 1 in all_frames and row.get("ce", 0) != all_frames[row["f"] - 1].get("ce", 0)
        ],
        "content_decision_frames": [row["f"] for row in raw if row.get("cd") is not None],
        "layout_no_barrier_frames": [row["f"] for row in raw if (row.get("cd") or {}).get("decision") == "no_barrier"],
        "layout_unknown_frames": [row["f"] for row in raw if (row.get("cd") or {}).get("decision") == "unknown"],
        "scene_count_semantics": "pixel evidence/hypotheses and tracking epochs; not labelled physical cuts",
    }


def build(
    run: Path,
    sid: str,
    replay: Path,
    source: Path,
    pts_csv: Path,
    evaluation: Path,
    output: Path,
    *,
    max_images: int = 16000,
    source_frames: Path | None = None,
    completion_recovery: Path | None = None,
) -> dict:
    import av
    import cv2
    import msgpack

    from bai_engine.schema.events import Event, current_view
    from research.production_external_semantic_replay import load_finished_input, verify_replay_output_artifacts

    recorded = (
        load_finished_input(run, sid)
        if completion_recovery is None
        else load_finished_input(run, sid, completion_recovery=completion_recovery)
    )
    proof_path, trace_path = replay / "replay_manifest.json", replay / "bounded_fsm_trace.jsonl"
    proof = read(proof_path)
    traces = [json.loads(line) for line in trace_path.open() if line.strip()]
    verify_replay(proof, recorded, trace_path, traces, sid)
    verify_replay_output_artifacts(replay, proof)
    info = read(recorded.report_path)
    if sha(source) != info["source_sha256"]:
        raise ValueError("original source differs from actual fresh run")
    rate = Fraction(recorded.media["fps_num"], recorded.media["fps_den"])
    n = recorded.media["n_frames"]
    mapping = verified_pts(pts_csv, n, rate)
    container = av.open(str(source))
    stream = container.streams.video[0]
    if stream.average_rate != rate or any(base != stream.time_base for _, base in mapping.values()):
        container.close()
        raise ValueError("source stream rate/time base differs from verified PTS audit")
    # Annotations and their derived evaluation are read only after genuine
    # producer completion and own-source baseline proof have been checked.
    result = read(evaluation / "supplemental_metrics.json")
    if result.get("provenance", {}).get(str((run / "predicted_rallies.csv").resolve())) != sha(
        run / "predicted_rallies.csv"
    ) or result.get("provenance", {}).get(str(recorded.report_path.resolve())) != sha(recorded.report_path):
        container.close()
        raise ValueError("evaluation is not bound to this run's predictions")
    from scripts.benchmarking.evaluate_rallies import read_csv

    predictions = read_csv(run / "predicted_rallies.csv", float(rate))
    prediction_rows = [{"start_frame": p.start_frame, "end_frame": p.end_frame} for p in predictions]
    with (evaluation / "per_rally_comparison.csv").open(newline="") as comparison_stream:
        comparison = list(csv.DictReader(comparison_stream))
    ground_truth = [
        {"start_frame": int(row["gt_start_frame"]), "end_frame": int(row["gt_end_frame"])} for row in comparison
    ]
    cases = result["failure_cases"]
    layout, contexts = {}, {}
    for case in cases:
        windows, context = case_ranges(case, prediction_rows, n, ground_truth)
        layout[case["case_id"]] = {"windows": windows, "context": context, "evaluation": case}
        contexts[case["case_id"]] = context
    selected = sorted({f for case in layout.values() for lo, hi in case["windows"] for f in range(lo, hi)})
    if len(selected) > max_images:
        container.close()
        raise ValueError(
            f"{len(selected)} replay frames exceed explicit image budget {max_images}; no failures dropped"
        )
    all_frames, cache_hashes = {}, {}
    for path in sorted(recorded.cache_directory.glob("*.msgpack")):
        payload = path.read_bytes()
        cache_hashes[path.name] = hashlib.sha256(payload).hexdigest()
        if cache_hashes[path.name] != recorded.expected_caches.get(path.name):
            raise ValueError("own perception cache digest changed")
        for frame in msgpack.unpackb(payload, raw=False)["frames"]:
            if frame["f"] in all_frames:
                raise ValueError("duplicate source frame in perception cache")
            all_frames[frame["f"]] = frame
    if sorted(all_frames) != list(range(n)) or cache_hashes != proof["cache_sha256"]:
        raise ValueError("perception source population differs from own baseline")
    steps = {row["frame"]: row for row in traces if row["call"] == "step"}
    transitions = {}
    for row in traces:
        if row["call"] != "step" or row["before"]["state"] != row["after"]["state"] or any(row["update"].values()):
            transitions.setdefault(row["frame"], []).append(row)
    source_events = [json.loads(line) for line in recorded.events_path.open() if line.strip()]
    live = current_view([Event.model_validate(row) for row in source_events])
    contacts = {}
    for event in live:
        if event.type == "contact":
            contacts.setdefault(event.frame_start, []).append(event.model_dump(mode="json"))
    output.mkdir(parents=True, exist_ok=False)
    (output / "cases").mkdir()
    (output / "frames").mkdir()
    case_index = []
    for case in cases:
        name = case["case_id"]
        lo, hi = contexts[name]
        raw = [all_frames[f] for f in range(lo, hi)]
        document = {
            "case": case,
            "context_half_open": [lo, hi],
            "replay_windows_half_open": layout[name]["windows"],
            "source_sha256": info["source_sha256"],
            "proxy_sha256": info["proxy_sha256"],
            "raw_perception": raw,
            "semantic_trace": [row for row in traces if lo <= row["frame"] < hi],
            "events": [e for e in source_events if e["frame_start"] < hi and e["frame_end"] >= lo],
            "calibration_events": [e for e in source_events if e["type"] == "calibration"],
            "latest_prior_format_decision": next(
                (e for e in reversed(source_events) if e["type"] == "format_decision" and e["frame_start"] < lo),
                None,
            ),
            "diagnostic_summary": {
                "raw_shuttle_frames": sum(row.get("s") is not None for row in raw),
                "view_counts": dict(Counter(row.get("v") or "unknown" for row in raw)),
                "calibration_counts": dict(Counter(row.get("cs") or "unknown" for row in raw)),
                "detector_run_frames": sum(bool(row.get("do")) for row in raw),
                "camera_lost_frames": sum(bool(row.get("l")) for row in raw),
                **content_transition_summary(raw, all_frames),
                "first_processed_observation_frame": next(
                    (f for f in range(lo, hi) if steps[f]["observation"].get("kind") == "observed"), None
                ),
            },
            "interpretation": "Diagnostic model and state evidence; physical failure mechanism requires source review.",
        }
        write(output / "cases" / (name + ".json"), finite_json(document))
        case_index.append({**case, **layout[name], "case_json": "cases/" + name + ".json"})
    width = 960
    height = round(stream.height * width / stream.width)
    viewer = {
        "fps": float(rate),
        "proxy_size": [recorded.media["width"], recorded.media["height"]],
        "display_size": [width, height],
        "cases": layout,
        "frames": {},
        "ground_truth": ground_truth,
        "predictions": prediction_rows,
    }
    image_hashes, cache_receipt = {}, None
    if source_frames is not None:
        import shutil

        from research.test2_source_frame_cache import verified_cache

        image_manifest, verified_paths = verified_cache(
            source_frames,
            source_sha256=info["source_sha256"],
            pts_csv=pts_csv,
            n_frames=n,
            rate=rate,
            source_size=[stream.width, stream.height],
            mapping=mapping,
            selected=selected,
        )
        for f, path in verified_paths.items():
            target = output / "frames" / f"{f}.jpg"
            shutil.copyfile(path, target)
            image_hashes[target.name] = sha(target)
            if image_hashes[target.name] != image_manifest["frames"][f]["sha256"]:
                raise ValueError("copied source-frame JPEG differs from verified original image")
        cache_receipt = {
            "path": str(source_frames),
            "manifest_sha256": sha(source_frames / "manifest.json"),
            "selected_images_verified_and_copied": len(verified_paths),
            "transform": image_manifest["transform"],
        }
    else:
        for lo, hi in merge_ranges([tuple(window) for case in layout.values() for window in case["windows"]]):
            container.seek(mapping[lo][0], stream=stream, backward=True)
            for decoded in container.decode(stream):
                if decoded.pts is None:
                    raise ValueError("decoded source frame has no PTS")
                exact = decoded.pts * stream.time_base * rate
                if exact.denominator != 1:
                    raise ValueError("decoded source PTS has no verified canonical correspondence")
                f = int(exact)
                if f < lo:
                    continue
                if f >= hi:
                    break
                if mapping[f] != (decoded.pts, stream.time_base):
                    raise ValueError("actual decoded frame differs from source PTS audit")
                target = output / "frames" / f"{f}.jpg"
                pixels = cv2.resize(decoded.to_ndarray(format="bgr24"), (width, height), interpolation=cv2.INTER_AREA)
                if not cv2.imwrite(str(target), pixels, [cv2.IMWRITE_JPEG_QUALITY, 86]):
                    raise ValueError("source JPEG write failed")
                image_hashes[target.name] = sha(target)
    container.close()
    if sorted(int(Path(name).stem) for name in image_hashes) != selected:
        raise ValueError("source decode did not supply every selected replay frame")
    for f in selected:
        raw, semantic = all_frames[f], steps[f]
        pts, time_base = mapping[f]
        viewer["frames"][f] = finite_json(
            {
                "pts": pts,
                "time_base": str(time_base),
                "timestamp_seconds": float(pts * time_base),
                "raw_xy": raw.get("s"),
                "raw_support": raw.get("c"),
                "processed_xy": projected(raw.get("g"), semantic["processed_xy"]),
                "view": raw.get("v"),
                "calibration": raw.get("cs"),
                "association": raw.get("sa"),
                "content_hypothesis": raw.get("cc"),
                "content_decision": raw.get("cd"),
                "people": raw.get("p", []),
                "contacts": contacts.get(f, []),
                "fsm": semantic["after"],
                "transitions": transitions.get(f, []),
            }
        )
    if sha(source) != info["source_sha256"]:
        raise ValueError("original source changed during failure rendering")
    serialized = json.dumps(viewer, allow_nan=False, separators=(",", ":")).replace("</", "<\\/")
    (output / "index.html").write_text(HTML.replace("__DATA__", serialized))
    write(output / "failure_case_index.json", case_index)
    inputs = [
        source,
        pts_csv,
        proof_path,
        trace_path,
        evaluation / "supplemental_metrics.json",
        recorded.report_path,
        recorded.events_path,
        evaluation / "per_rally_comparison.csv",
        Path(__file__),
    ]
    manifest = {
        "schema": "source-bound-failure-package-v1",
        "source_run": str(run),
        "session_id": sid,
        "source_dimensions": [stream.width, stream.height],
        "fps": str(rate),
        "source_sha256": info["source_sha256"],
        "proxy_sha256": info["proxy_sha256"],
        "all_failures_included": True,
        "failure_count": len(cases),
        "source_images": len(selected),
        "original_source_pts_exact": True,
        "full_perception_and_trace_coverage_verified": True,
        "baseline_semantic_parity": True,
        "cache_sha256": cache_hashes,
        "input_sha256": {str(path.resolve()): sha(path) for path in inputs},
        "image_sha256": image_hashes,
        "source_frame_cache": cache_receipt,
        "case_sha256": {path.name: sha(path) for path in sorted((output / "cases").glob("*.json"))},
        "html_sha256": sha(output / "index.html"),
        "review_status": "Unreviewed assistant diagnostic package; no independent physical labels added.",
        "limits": [
            "No generic VFR mapping",
            "No inference or manual prediction changes",
            "Raw cache includes model/tracker uncertainty; not physical ground truth",
        ],
    }
    write(output / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("run", "replay", "source", "source-pts", "evaluation", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--session", required=True)
    parser.add_argument("--max-images", type=int, default=16000)
    parser.add_argument("--completion-recovery", type=Path)
    parser.add_argument(
        "--source-frames", type=Path, help="Optional verified source-only JPEG cache; no NN cache reuse"
    )
    a = parser.parse_args()
    result = build(
        a.run.resolve(),
        a.session,
        a.replay.resolve(),
        a.source.resolve(),
        a.source_pts.resolve(),
        a.evaluation.resolve(),
        a.output.resolve(),
        max_images=a.max_images,
        source_frames=a.source_frames.absolute() if a.source_frames else None,
        completion_recovery=a.completion_recovery.resolve(strict=True) if a.completion_recovery else None,
    )
    print(json.dumps({key: result[key] for key in ("failure_count", "source_images", "original_source_pts_exact")}))


if __name__ == "__main__":
    main()
