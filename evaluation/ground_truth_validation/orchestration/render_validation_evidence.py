"""Render curated exact-PTS evidence from completed uploads; no inference or metrics.

Reads genuine original worker/parent/plan/catalogue receipts directly, without
importing a different checkout's pipeline or rewriting its recorded ROOT.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import platform
import sys
from fractions import Fraction
from pathlib import Path

MAX_FRAMES = 128
SKELETON = [
    (0, 1),
    (0, 2),
    (1, 3),
    (2, 4),
    (5, 6),
    (5, 7),
    (7, 9),
    (6, 8),
    (8, 10),
    (5, 11),
    (6, 12),
    (11, 12),
    (11, 13),
    (13, 15),
    (12, 14),
    (14, 16),
]


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def safe_child(root, relative):
    p = Path(relative)
    if p.is_absolute() or ".." in p.parts:
        raise ValueError("Unsafe artifact-relative path")
    result = root / p
    if any(x.is_symlink() for x in (result, *result.parents)) or not result.is_file():
        raise ValueError("Regular non-symlink artifact required: " + str(result))
    return result


def new_output(path, runs):
    path = path.absolute()
    if path.exists() or any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("Require NEW output without symlink ancestors; existing evidence is immutable")
    if any(path == run or run in path.parents for run in runs):
        raise ValueError("Output cannot be inside an input run")
    return path


def bind(path):
    p = Path(path).resolve(strict=True)
    return {"path": str(p), "sha256": sha(p), "bytes": p.stat().st_size}


def scene_foreground(frame, codec):
    """Detached image-context provenance; legacy absence is unknown, not zero GT."""
    if codec < 22:
        return None
    values = frame.get("fg")
    if not isinstance(values, list) or len(values) > 8:
        raise ValueError("Codec22 requires bounded scene-only foreground metadata")
    keys = set()
    for region in values:
        fields = {"frame", "key", "bbox", "detector_matched", "detector_observed"}
        if not isinstance(region, dict) or set(region) != fields:
            raise ValueError("Invalid scene-only foreground fields")
        box, key = region["bbox"], region["key"]
        if (
            type(region["frame"]) is not int
            or region["frame"] != frame["f"]
            or not isinstance(key, str)
            or not 1 <= len(key) <= 160
            or key in keys
            or not isinstance(box, (list, tuple))
            or len(box) != 4
            or any(type(v) not in (int, float) or not math.isfinite(v) for v in box)
            or not box[0] < box[2]
            or not box[1] < box[3]
            or any(
                region[k] is not None and type(region[k]) is not bool for k in ("detector_matched", "detector_observed")
            )
        ):
            raise ValueError("Scene-only foreground frame/key/coordinate/freshness mismatch")
        keys.add(key)
    return values


def verify_model_metadata(arm):
    """Match prepare_models: manifest byte hash, pins sorted-JSON value hash.

    Pin files are reserialized during staging. Their exact raw bytes remain a
    separate binding; the worker's pins_sha256 is never a raw-file checksum.
    """
    models, verified = arm["info"].get("models", {}), []
    for label, relative, field in (
        ("model_manifest", "models/manifest.yaml", "manifest_sha256"),
        ("model_pins", "models/cache/lock.json", "pins_sha256"),
    ):
        expected = models.get(field)
        if not expected:
            continue
        path = safe_child(arm["run"], relative)
        actual = sha(path)
        semantics = "SHA256 of exact manifest file bytes"
        if label == "model_pins":
            actual = hashlib.sha256(json.dumps(read(path), sort_keys=True, allow_nan=False).encode()).hexdigest()
            semantics = "SHA256 of json.dumps(parsed pins, sort_keys=True, allow_nan=False) UTF-8 bytes"
        if actual != expected:
            raise ValueError("Recorded model metadata changed: " + label + " (" + semantics + ")")
        entry = {
            "label": label,
            "file_binding": bind(path),
            "worker_field": field,
            "worker_value_sha256": expected,
            "verified_value_sha256": actual,
            "hash_semantics": semantics,
        }
        if label == "model_pins":
            source = Path(arm["recorded_pipeline_root"]) / "models/cache/lock.json"
            source_expected = arm["plan"]["input_files_sha256"].get(str(source))
            if source_expected is None or sha(source) != source_expected:
                raise ValueError("Original source pin file differs from its exact plan byte binding")
            source_value = hashlib.sha256(
                json.dumps(read(source), sort_keys=True, allow_nan=False).encode()
            ).hexdigest()
            if source_value != expected:
                raise ValueError("Staged pins do not equal the original source pin values")
            entry["original_source_declared_path"] = str(source)
            entry["original_source_file_binding"] = bind(source)
        verified.append(entry)
    return verified


def verify_run(run, source, pipeline_root=None):
    """Strict completed production-upload receipt and full cache integrity guard."""
    import msgpack

    run = run.resolve(strict=True)
    info_path, parent_path = run / "inference.json", run.with_suffix(".executor.json")
    info, parent = read(info_path), read(parent_path)
    media, receipt = info["media"], info.get("perception_cache_catalog", {})
    n = media["n_frames"]
    if (
        any(
            type(media.get(k)) is not int or media[k] <= 0
            for k in ("n_frames", "width", "height", "fps_num", "fps_den", "source_width", "source_height")
        )
        or n > 2_000_000
        or info.get("status") != "completed"
        or info.get("cached_perception_used") is not False
        or info.get("frames_processed") != n
        or info.get("frontier_frame") != n - 1
        or parent.get("status") != "completed"
        or parent.get("worker_exit_code") != 0
        or parent.get("frozen_source_inputs_unchanged") is not True
        or parent.get("worker_report_sha256") != sha(info_path)
        or parent.get("output_proxy_sha256") != info["proxy_sha256"]
    ):
        raise ValueError("Genuine completed fresh worker+parent and full frontier required")
    command = parent["command"]
    if command.count("--plan") != 1:
        raise ValueError("Exactly one original recorded plan required")
    plan_path = Path(command[command.index("--plan") + 1])
    if sha(plan_path) != parent.get("plan_sha256"):
        raise ValueError("Original plan changed")
    plan = read(plan_path)
    item = plan["cases"][parent["case"]]
    original = Path(item["session"])
    if item.get("kind") != "production_upload" or sha(original) != plan["input_files_sha256"].get(str(original)):
        raise ValueError("Source-bound original upload session required")
    session = read(run / "session.json")
    original_session = read(original)
    sid = session["session_id"]
    if (
        not isinstance(sid, str)
        or not sid.isalnum()
        or len(sid) > 96
        or session.get("status") != "analysed"
        or session["media"] != media
        or session.get("frontier_frame") != n - 1
        or item["frames"] != n
        or original_session["session_id"] != sid
        or any(
            x != info["source_sha256"]
            for x in (item["source_sha256"], session["source"]["sha256"], original_session["source"]["sha256"])
        )
        or Path(original_session["source"]["uri"]).absolute() != Path(item["source"]).absolute()
        or sha(source) != info["source_sha256"]
    ):
        raise ValueError("Source SHA/session/media/complete-frame identity mismatch")
    # Source restoration is explicit by bytes, never by changing historical URIs.
    proxy = run / "data/media" / info["source_sha256"] / "proxy.mp4"
    if sha(proxy) != info["proxy_sha256"]:
        raise ValueError("Canonical proxy changed")
    verification = parent.get("perception_cache_catalog_verification", {})
    if (
        receipt.get("path") != "perception_completion_catalog.json"
        or receipt.get("schema") != "production-perception-completion-catalog:v1"
        or verification.get("status") != "verified"
        or verification.get("catalog_sha256") != receipt.get("sha256")
        or verification.get("frames") != n
        or verification.get("files") != receipt.get("file_count")
        or type(receipt.get("file_count")) is not int
        or not 0 < receipt["file_count"] <= 10_000
    ):
        raise ValueError("Original parent-verified full cache catalogue required")
    catalogue_path = safe_child(run, receipt["path"])
    if sha(catalogue_path) != receipt["sha256"]:
        raise ValueError("Cache catalogue changed")
    catalogue = read(catalogue_path)
    if (
        catalogue.get("schema") != receipt["schema"]
        or catalogue.get("session_id") != sid
        or catalogue.get("source_sha256") != info["source_sha256"]
        or catalogue.get("proxy_sha256") != info["proxy_sha256"]
        or catalogue.get("frame_count") != n
        or receipt.get("frame_count") != n
        or catalogue.get("snapshot_stage") != "after_analysis_before_worker_completion_receipt"
        or catalogue.get("file_count") != receipt["file_count"]
        or len(catalogue["files"]) != receipt["file_count"]
        or catalogue["media"] != {k: media[k] for k in ("n_frames", "width", "height", "fps_num", "fps_den")}
    ):
        raise ValueError("Catalogue source/session/media/completion mismatch")
    cache_dir = run / "data/sessions" / sid / "perception"
    actual = sorted(p.name for p in cache_dir.iterdir())
    if actual != [f"seg_{i:05d}.msgpack" for i in range(len(catalogue["files"]))]:
        raise ValueError("Missing/foreign cache file population")
    frontier, total, cache_bindings = 0, 0, []
    for i, row in enumerate(catalogue["files"]):
        path = safe_child(run, row["path"])
        if path.parent != cache_dir or path.name != actual[i] or not 0 < path.stat().st_size <= 16 * 1024**2:
            raise ValueError("Cache path/size does not match canonical population")
        blob = path.read_bytes()
        if hashlib.sha256(blob).hexdigest() != row["sha256"] or len(blob) != row["bytes"]:
            raise ValueError("Closed cache bytes changed")
        c = msgpack.unpackb(
            blob, raw=False, max_array_len=4096, max_map_len=4096, max_str_len=1024**2, max_bin_len=16 * 1024**2
        )
        ci = c["ci"]
        header = {key: c.get(key) for key in ("v", "start", "end", "cr", "ci", "models")}
        if (
            c["v"] not in (20, 21, 22, 23, 24, 25)
            or c["v"] != row["codec_version"]
            or c["start"] != frontier
            or c["start"] != row["start"]
            or c["end"] != row["end"]
            or not c["start"] <= c["end"] < n
            or len(c["frames"]) != row["frame_count"]
            or len(c["frames"]) != c["end"] - c["start"] + 1
            or any(type(f.get("f")) is not int for f in c["frames"])
            or [f["f"] for f in c["frames"]] != list(range(c["start"], c["end"] + 1))
            or ci.get("frame_size") != [media["width"], media["height"]]
            or not math.isclose(ci["fps"], media["fps_num"] / media["fps_den"], rel_tol=0, abs_tol=1e-9)
            or hashlib.sha256(json.dumps(header, sort_keys=True, allow_nan=False).encode()).hexdigest()
            != row["header_sha256"]
            or (c["v"] >= 21 and (ci.get("loaded_models") != c.get("models") or ci.get("profile") != info["profile"]))
        ):
            raise ValueError("Cache header/models/profile/frame extent mismatch")
        for frame in c["frames"]:
            scene_foreground(frame, c["v"])
        frontier, total = c["end"] + 1, total + len(blob)
        cache_bindings.append({"path": str(path), "sha256": row["sha256"], "bytes": row["bytes"]})
    if frontier != n or total != catalogue.get("total_bytes"):
        raise ValueError("Incomplete catalogue timeline/byte population")
    roots = {
        str(Path(p.split(marker)[0]))
        for p in plan["source_files_sha256"]
        for marker in ("/engine/src/", "/sports/badminton/src/")
        if marker in p
    }
    if len(roots) != 1 or (pipeline_root is not None and str(pipeline_root.resolve()) not in roots):
        raise ValueError("Explicit pipeline root differs from recorded source root; no rebasing")
    paths = [info_path, parent_path, plan_path, original, run / "session.json", run / "events.jsonl", catalogue_path]
    return {
        "run": run,
        "info": info,
        "plan": plan,
        "proxy": proxy,
        "media": media,
        "catalogue": catalogue,
        "sid": sid,
        "recorded_pipeline_root": next(iter(roots)),
        "inputs": [bind(p) for p in paths],
        "cache_bindings": cache_bindings,
    }


def verify_pts(path, audit_path, bound):
    audit, media = read(audit_path), bound["media"]
    n, fps = media["n_frames"], Fraction(media["fps_num"], media["fps_den"])
    expected_report = str((bound["run"] / "inference.json").resolve())
    if (
        audit.get("source_sha256") != bound["info"]["source_sha256"]
        or audit.get("proxy_sha256") != bound["info"]["proxy_sha256"]
        or audit.get("source_pts_csv_sha256") != sha(path)
        or audit.get("frames_decoded") != n
        or audit.get("exact_pts_frames") != n
        or audit.get("source_proxy_full_rational_pts_equal") is not True
        or Fraction(audit.get("origin_rational_seconds", "-1")) != 0
        or audit.get("input_sha256", {}).get(expected_report) != sha(bound["run"] / "inference.json")
    ):
        raise ValueError("PTS audit is incomplete, changed or from another source/run")
    times = []
    with path.open(newline="") as stream:
        for i, row in enumerate(csv.DictReader(stream)):
            t = int(row["pts"]) * Fraction(int(row["time_base_num"]), int(row["time_base_den"]))
            if int(row["source_frame"]) != i or t != i / fps:
                raise ValueError("Source PTS CSV must fully map unchanged zero-origin canonical CFR")
            times.append(t)
    if len(times) != n:
        raise ValueError("Incomplete source PTS CSV")
    return times


def requested_frames(values, n, source_sha):
    if isinstance(values, dict):
        if values.get("source_sha256") != source_sha:
            raise ValueError("Frame manifest belongs to another source")
        values = values["frames"]
    if not isinstance(values, list) or not 0 < len(values) <= MAX_FRAMES:
        raise ValueError("Require 1–128 curated frames")
    result = [dict(frame=x) if type(x) is int else x for x in values]
    if any(not isinstance(x, dict) or type(x.get("frame")) is not int or not 0 <= x["frame"] < n for x in result):
        raise ValueError("Frame IDs must be integers within complete canonical bounds")
    if len({x["frame"] for x in result}) != len(result):
        raise ValueError("Duplicate frame IDs are not curated evidence")
    return sorted(result, key=lambda x: x["frame"])


def exact_frame(path, wanted, shape):
    import av

    with av.open(str(path)) as container:
        stream = container.streams.video[0]
        stream.codec_context.thread_count = 2
        ticks = wanted / stream.time_base
        if ticks.denominator != 1:
            raise ValueError("Requested time has no exact PTS in this stream")
        container.seek(int(ticks), stream=stream, backward=True, any_frame=False)
        for frame in container.decode(stream):
            time = frame.pts * frame.time_base
            if time < wanted:
                continue
            if time != wanted:
                raise ValueError("Decoded frame skipped requested exact PTS")
            if frame.rotation != 0:
                raise ValueError("Display-rotated media requires an explicit source-to-proxy image transform")
            image = frame.to_ndarray(format="bgr24")
            if tuple(image.shape) != tuple(shape):
                raise ValueError("Decoded dimensions differ from recorded media")
            return image, {
                "pts": frame.pts,
                "time_base": str(frame.time_base),
                "seconds_rational": str(time),
                "shape": list(image.shape),
                "pixels_sha256": hashlib.sha256(image.tobytes()).hexdigest(),
            }
    raise ValueError("Requested exact source/proxy frame missing")


def render(image, frame, title, *, foreground=None):
    import cv2

    image = image.copy()

    def point(x):
        return tuple(round(float(v)) for v in x[:2])

    def finite(x):
        return isinstance(x, (list, tuple)) and len(x) >= 2 and all(math.isfinite(float(v)) for v in x[:2])

    def label(text, xy, color):
        cv2.putText(image, str(text), xy, cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(image, str(text), xy, cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1, cv2.LINE_AA)

    # Scene context may include non-athletes or regions with expired court
    # authority. Its opaque keys never identify participants or physical GT.
    for region in foreground or []:
        b = region["bbox"]
        color = (255, 180, 0)
        cv2.rectangle(image, point(b[:2]), point(b[2:]), color, 1)
        label(f"IMAGE CONTEXT ONLY {region['key']}", point([b[0], max(15, b[1] + 12)]), color)
    for person in frame.get("p", []):
        b = person.get("b")
        color = (0, 255, 0) if person.get("dm") is True else (0, 165, 255)
        if b is not None and len(b) == 4 and finite(b[:2]) and finite(b[2:]):
            cv2.rectangle(image, point(b[:2]), point(b[2:]), color, 2)
            label(
                f"track {person.get('t')} raw {person.get('rt')} fresh={person.get('dm')}",
                point([b[0], max(15, b[1] - 5)]),
                color,
            )
        k = person.get("k")
        if k:
            for a, z in SKELETON:
                if max(a, z) < len(k) and finite(k[a]) and finite(k[z]):
                    cv2.line(image, point(k[a]), point(k[z]), (255, 0, 255), 1)
            for joint in k:
                if finite(joint):
                    cv2.circle(image, point(joint), 2, (255, 0, 255), -1)
        racket = person.get("rk")
        if racket and finite(racket.get("center")):
            cv2.ellipse(
                image,
                point(racket["center"]),
                tuple(max(1, round(float(v) / 2)) for v in racket["axes"]),
                float(racket["angle"]),
                0,
                360,
                (0, 0, 255),
                2,
            )
            label("raw racket estimate?", point(racket["center"]), (0, 0, 255))
    association = frame.get("sa") or {}
    for key, xy, color, radius in [
        ("raw", association.get("raw_xy", frame.get("s")), (0, 165, 255), 5),
        ("associated", association.get("selected_xy"), (255, 255, 0), 10),
    ]:
        if finite(xy):
            cv2.circle(image, point(xy), radius, color, 2)
            label(key + " shuttle?", point(xy), color)
    footer = [
        title,
        f"frame {frame['f']} | view={frame.get('v')} calibration={frame.get('cs')} epoch={frame.get('ce')}",
        "GREEN=fresh box ORANGE=carried MAGENTA=finite pose joints RED=raw racket estimate",
        "No confidence filter on drawn joints; raw support/freshness/uncertainty retained in JSON.",
        f"shuttle association={association.get('status')}/{association.get('association_status')} "
        f"{association.get('reasons')}",
        "Predictions / agent diagnostics; no independently reviewed physical GT or accuracy claim.",
        "BLUE=image context only; not athlete admission, identity or truth. "
        + ("Legacy scene context unknown." if foreground is None else f"Explicit scene regions={len(foreground)}."),
        f"Raw scene witnesses={(frame.get('cc') or {}).get('supporting_region_keys')}; "
        f"layout indices={(frame.get('cd') or {}).get('layout_indices')}",
    ]
    image = cv2.copyMakeBorder(image, 0, 170, 0, 0, cv2.BORDER_CONSTANT, value=(15, 15, 15))
    for i, text in enumerate(footer):
        label(text, (5, image.shape[0] - 150 + i * 20), (240, 240, 240))
    return image


def png(path, image):
    import cv2

    ok, data = cv2.imencode(".png", image)
    if not ok:
        raise ValueError("PNG encoding failed")
    with path.open("xb") as stream:
        stream.write(data.tobytes())


def main(args):
    import cv2
    import msgpack

    runs = [args.run.resolve(strict=True)] + ([args.baseline_run.resolve(strict=True)] if args.baseline_run else [])
    output = new_output(args.output, runs)
    source = args.source_video.resolve(strict=True)
    current = verify_run(runs[0], source, args.pipeline_root)
    arms = {"current": current}
    pts = args.source_pts.resolve(strict=True)
    audit = args.pts_audit or pts.parent / "timestamp_audit.json"
    times = verify_pts(pts, audit, current)
    audits = [audit]
    if args.baseline_run:
        baseline = verify_run(runs[1], source, args.baseline_pipeline_root)
        if any(
            baseline["media"][k] != current["media"][k]
            for k in ("n_frames", "width", "height", "fps_num", "fps_den", "source_width", "source_height")
        ):
            raise ValueError("Baseline has a different frame/coordinate basis")
        baseline_audit = args.baseline_pts_audit or runs[1].parent / "timestamps/timestamp_audit.json"
        verify_pts(pts, baseline_audit, baseline)
        audits.append(baseline_audit)
        arms["baseline"] = baseline
    values = read(args.frames_json) if args.frames_json else [int(x) for x in args.frames.split(",")]
    frames = requested_frames(values, current["media"]["n_frames"], current["info"]["source_sha256"])
    if not args.dataset_label.strip():
        raise ValueError("Explicit dataset label required")
    output.mkdir(parents=True, exist_ok=False)
    try:
        (output / "executed_tool.py.source").write_bytes(Path(__file__).read_bytes())
        import av

        dump(
            output / "invocation.json",
            {
                "argv": sys.argv,
                "arguments": {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
                "guard_mode": "read original receipts/catalogue; no pipeline imports or ROOT rebasing",
                "runtime": {
                    "python": sys.version,
                    "platform": platform.platform(),
                    "av": av.__version__,
                    "cv2": cv2.__version__,
                    "msgpack": msgpack.__version__,
                },
            },
        )
        bindings = [bind(source), bind(pts), *[bind(p) for p in audits]]
        provenance = output / "input_metadata"
        provenance.mkdir()
        (provenance / "source_frame_pts.csv").write_bytes(pts.read_bytes())
        for i, path in enumerate(audits):
            (provenance / f"timestamp_audit_{i}.json").write_bytes(path.read_bytes())
        if args.frames_json:
            bindings.append(bind(args.frames_json))
            (provenance / "requested_frames.json").write_bytes(args.frames_json.read_bytes())
        for name, arm in arms.items():
            folder = output / name
            folder.mkdir()
            for i, ref in enumerate(arm["inputs"]):
                (folder / f"receipt_{i:02d}_{Path(ref['path']).name}").write_bytes(Path(ref["path"]).read_bytes())
            dump(
                folder / "run_binding.json",
                {k: arm[k] for k in ("sid", "recorded_pipeline_root", "media", "info", "plan", "inputs")},
            )
            model_metadata = verify_model_metadata(arm)
            dump(folder / "model_metadata_binding.json", model_metadata)
            for entry in model_metadata:
                path = Path(entry["file_binding"]["path"])
                (folder / (entry["label"] + path.suffix)).write_bytes(path.read_bytes())
                bindings.append(entry["file_binding"])
                if "original_source_file_binding" in entry:
                    bindings.append(entry["original_source_file_binding"])
            for i, (path, digest) in enumerate(arm["plan"]["input_files_sha256"].items()):
                p = Path(path)
                if p.suffix.lower() in {".yaml", ".yml", ".json"} and p.exists() and p.stat().st_size <= 8 * 1024**2:
                    if sha(p) != digest:
                        raise ValueError("Original pinned configuration/session metadata changed")
                    (folder / f"input_{i:02d}_{p.name}").write_bytes(p.read_bytes())
                    bindings.append(bind(p))
            bindings += arm["inputs"] + arm["cache_bindings"] + [bind(arm["proxy"])]
        snapshots, results = {}, []
        for request in frames:
            f = request["frame"]
            directory = output / f"frame_{f:07d}"
            directory.mkdir()
            media = current["media"]
            original, source_meta = exact_frame(source, times[f], [media["source_height"], media["source_width"], 3])
            resized = cv2.resize(original, (media["width"], media["height"]), interpolation=cv2.INTER_AREA)
            png(directory / "source_original.png", original)
            png(directory / "source_resized.png", resized)
            refs = []
            if len(request.get("reference_rows", [])) > 8:
                raise ValueError("Curated frames permit at most8 supplied reference rows each")
            for ref in request.get("reference_rows", []):
                path = Path(ref["file"]).resolve(strict=True)
                value = read(path)
                if (
                    isinstance(value, dict)
                    and value.get("source_sha256", current["info"]["source_sha256"]) != current["info"]["source_sha256"]
                ):
                    raise ValueError("Supplied reference metadata belongs to another source")
                for part in ref["pointer"].strip("/").split("/") if ref["pointer"] else []:
                    part = part.replace("~1", "/").replace("~0", "~")
                    value = value[int(part)] if isinstance(value, list) else value[part]
                refs.append(
                    {
                        **ref,
                        "file_binding": bind(path),
                        "supplied_value": value,
                        "physical_truth_status": "supplied reference only; no adjudication inferred",
                    }
                )
                bindings.append(bind(path))
            entry = {
                "frame": f,
                "seconds_rational": str(times[f]),
                "request": request,
                "source_decode": source_meta,
                "reference_rows": refs,
                "arms": {},
            }
            for name, arm in arms.items():
                row = next(x for x in arm["catalogue"]["files"] if x["start"] <= f <= x["end"])
                cache = safe_child(arm["run"], row["path"])
                blob = cache.read_bytes()
                if hashlib.sha256(blob).hexdigest() != row["sha256"]:
                    raise ValueError("Cache changed after full guard")
                key = name + "_" + Path(row["path"]).name
                if key not in snapshots:
                    saved = output / name / key
                    saved.write_bytes(blob)
                    snapshots[key] = bind(saved)
                chunk = msgpack.unpackb(blob, raw=False)
                raw = chunk["frames"][f - chunk["start"]]
                foreground = scene_foreground(raw, chunk["v"])
                image, proxy_meta = exact_frame(arm["proxy"], times[f], [media["height"], media["width"], 3])
                png(directory / f"{name}_proxy.png", image)
                title = f"{args.dataset_label} | {name} | {f} / {float(times[f]):.6f}s"
                png(
                    directory / f"{name}_proxy_overlay.png",
                    render(image, raw, title + " | actual proxy", foreground=foreground),
                )
                png(
                    directory / f"{name}_source_overlay.png",
                    render(resized, raw, title + " | source resized to analysis basis", foreground=foreground),
                )
                dump(directory / f"{name}_raw_frame.json", raw)
                entry["arms"][name] = {
                    "cache_original": bind(cache),
                    "cache_snapshot": snapshots[key],
                    "proxy_decode": proxy_meta,
                    "models": chunk.get("models"),
                    "cache_identity": chunk.get("ci"),
                    "scene_foreground": {
                        "status": "unknown_legacy_codec" if foreground is None else "explicit_scene_only_context",
                        "regions": foreground,
                        "athlete_or_GT_authority": False,
                    },
                    "raw_frame_file": f"{name}_raw_frame.json",
                }
            dump(directory / "evidence.json", entry)
            results.append(entry)
        # Preserve selected semantic payloads verbatim, without rerunning semantics.
        for name, arm in arms.items():
            selected = {x["frame"]: [] for x in frames}
            with (arm["run"] / "events.jsonl").open() as stream:
                for line in stream:
                    event = json.loads(line)
                    if event["type"] in {
                        "contact",
                        "stroke",
                        "rally_start",
                        "rally_end",
                        "point",
                        "score_observation",
                        "racket_observation_ambiguity",
                        "highlight",
                        "identity_ambiguity",
                    }:
                        for f in selected:
                            if event["frame_start"] <= f <= event["frame_end"]:
                                selected[f].append(event)
            dump(output / name / "selected_events.json", selected)
        for binding in bindings:
            if sha(binding["path"]) != binding["sha256"]:
                raise ValueError("Bound input changed during evidence rendering")
        title = html.escape(args.dataset_label)
        md = [
            f"# {args.dataset_label}: source-bound visual diagnostics",
            "",
            "Predictions and supplied-reference captions only. "
            "Physical GT/accuracy unavailable unless separately reviewed.",
            "",
        ]
        page = [
            f'<!doctype html><meta charset="utf-8"><title>{title}</title><h1>{title}</h1>'
            "<p>Source-bound predictions; no new inference, metrics or reviewed physical GT.</p>"
        ]
        for item in results:
            f = item["frame"]
            stem = f"frame_{f:07d}"
            caption = item["request"].get("caption", "No supplied annotation caption")
            md += [
                f"## Frame {f} / {float(times[f]):.6f}s",
                "",
                caption,
                "",
                f"[Exact evidence and supplied reference rows]({stem}/evidence.json)",
                "",
            ]
            page += [
                f"<h2>Frame {f} / {float(times[f]):.6f}s</h2><p>{html.escape(caption)}</p>"
                f'<a href="{stem}/evidence.json">Exact evidence/reference rows</a>'
            ]
            for name in arms:
                md += [
                    f"![{name}: source]({stem}/{name}_source_overlay.png)",
                    f"![{name}: proxy]({stem}/{name}_proxy_overlay.png)",
                    "",
                ]
                md += [
                    f"Actual {name}: [raw bbox/pose/racket/shuttle]({stem}/{name}_raw_frame.json), "
                    f"[selected original semantic events]({name}/selected_events.json).",
                    "",
                ]
                page += [
                    f'<p>{name}: source / actual proxy; <a href="{stem}/{name}_raw_frame.json">actual raw output</a> · '
                    f'<a href="{name}/selected_events.json">original semantic events</a></p>'
                    f'<img width="48%" src="{stem}/{name}_source_overlay.png">'
                    f'<img width="48%" src="{stem}/{name}_proxy_overlay.png">'
                ]
            if item["reference_rows"]:
                text = json.dumps(item["reference_rows"], indent=2, ensure_ascii=False)
                md += [
                    "Supplied expected/reference rows (authority and physical validity remain as declared):",
                    "",
                    "```json",
                    text,
                    "```",
                    "",
                ]
                page += [
                    "<details><summary>Supplied expected/reference rows; not newly certified GT</summary><pre>"
                    + html.escape(text)
                    + "</pre></details>"
                ]
        (output / "index.md").write_text("\n".join(md) + "\n")
        (output / "index.html").write_text("\n".join(page) + "\n")
        files = {str(p.relative_to(output)): sha(p) for p in sorted(output.rglob("*")) if p.is_file()}
        dump(
            output / "completion.json",
            {
                "schema": "completed-validation-visual-evidence:v1",
                "status": "completed",
                "dataset_label": args.dataset_label,
                "source_sha256": current["info"]["source_sha256"],
                "frames": [x["frame"] for x in frames],
                "arms": list(arms),
                "input_bindings": bindings,
                "artifact_sha256": files,
                "executed_tool_sha256": sha(__file__),
                "neural_inference_performed": False,
                "physical_gt_created": False,
                "metrics_recomputed": False,
            },
        )
    except Exception as error:
        dump(output / "failure.json", {"status": "failed_evidence_preserved", "error": str(error)})
        raise


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    for option in ("run", "source-video", "source-pts", "output"):
        p.add_argument("--" + option, type=Path, required=True)
    p.add_argument("--dataset-label", required=True)
    for option in ("pipeline-root", "pts-audit", "baseline-run", "baseline-pipeline-root", "baseline-pts-audit"):
        p.add_argument("--" + option, type=Path)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--frames-json", type=Path)
    group.add_argument("--frames", help="Comma-separated integer canonical frame IDs (max128)")
    return p


if __name__ == "__main__":
    main(parser().parse_args())
