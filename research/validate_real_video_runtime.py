"""Fresh continuous badminton inference with isolated, reproducible results.

Run only on the configured GPU server after sourcing ../gpu-env.sh:
  .venv/bin/python research/validate_real_video_runtime.py --data-dir /path/data --list
  .venv/bin/python research/validate_real_video_runtime.py --data-dir /path/data \
      --session SampleRally --session RealVideo --output-dir /tmp/new-validation
  .venv/bin/python research/validate_real_video_runtime.py --session-json session.json \
      --proxy-path /tmp/test7/proxy.mp4 --output-dir /tmp/new-test7

The original catalogue, media and models are read-only inputs. Existing pinned
artifacts are copied into the new output; fetching is disabled, and Internet
sockets are blocked during model initialization/inference. Output data/ is a
normal isolated session catalogue with events and tracks, suitable for the
existing evaluate_session.py. Source session IDs are preserved for label binding.
SQLite mode=ro preserves logical records but may create/manage its WAL/SHM read
coordination sidecars. They are never unlinked by this command; immutable mode is
not used, so committed rows in an active WAL remain visible.
Optional --retain-perception writes observation-codec blobs before ingestion.
These are diagnostic model observations, not labels or restored private model state.
Inference remains fresh; no cached observations are consumed.
No prior score decisions or identity reviews are seeded; recorded calibration
and roster are explicit inputs. Overlay images are model evidence, not labels.

Windows are canonical half-open [start,end). Inference ALWAYS begins at zero;
end limits the processed prefix and flush is marked incomplete when truncated.
Start selects the review window only. Whole-video runs are the default.
Exit: 0 complete/consistent, 2 partial or required capability unavailable,
1 failed. Counts and consistency checks are never accuracy measurements.
"""

from __future__ import annotations

import argparse
import contextlib
import gc
import hashlib
import importlib.metadata
import json
import platform
import shutil
import socket
import sqlite3
import subprocess
import sys
import time
import traceback
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[1]
# An existing server venv may have editable installs pointing at another
# checkout. This command measures the checkout that contains this script.
for source_root in (REPO / "engine/src", REPO / "sports/badminton/src"):
    sys.path.insert(0, str(source_root))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def json_hash(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def validation_input_metadata(meta, *, media, proxy_sha256: str) -> dict:
    """Carry a checked crop transform, never prior review or benchmark labels."""
    if "source_window" not in meta:
        return {}
    raw = meta["source_window"]
    if not isinstance(raw, dict) or media is None:
        raise ValueError("source_window transform requires canonical media")
    allowed = {"source_decode_frames", "source_window_s", "proxy_frames", "proxy_fps_num", "proxy_fps_den",
               "source_frame_for_proxy_frame", "source_decode_start", "source_timestamps_preserved",
               "source_pts_mapping", "proxy_sha256"}
    mapping = json.loads(json.dumps({key: value for key, value in raw.items() if key in allowed}, allow_nan=False))
    bounds = mapping.get("source_decode_frames")
    start = mapping.get("source_decode_start")
    valid = (
        isinstance(bounds, list) and len(bounds) == 2 and all(type(v) is int for v in bounds)
        and type(start) is int and start >= 0 and bounds == [start, start + media.n_frames]
        and mapping.get("proxy_frames") == [0, media.n_frames]
        and type(mapping.get("proxy_fps_num")) is int and mapping["proxy_fps_num"] == media.fps_num
        and type(mapping.get("proxy_fps_den")) is int and mapping["proxy_fps_den"] == media.fps_den
        and mapping.get("proxy_sha256") == proxy_sha256
    )
    if not valid:
        raise ValueError("source_window transform differs from the actual canonical proxy")
    return {"source_window": mapping}


def read_catalogue(data: Path) -> list[dict]:
    """Read committed catalogue rows; permit SQLite's own WAL coordination files."""
    catalogue = (data / "sessions.sqlite").resolve(strict=True)
    with contextlib.closing(sqlite3.connect(f"{catalogue.as_uri()}?mode=ro", uri=True)) as connection:
        rows = connection.execute("SELECT body FROM sessions ORDER BY created_at,session_id").fetchall()
    return [json.loads(row[0]) for row in rows]


def select_sessions(rows: list[dict], selectors: list[str]) -> list[dict]:
    selected = {}
    for selector in selectors:
        key = selector.casefold()
        exact = [row for row in rows if key == row["session_id"].casefold()]
        candidates = exact or [
            row for row in rows
            if not row.get("meta", {}).get("reused_session_id") and any(
                key in str(value or "").casefold()
                for value in (row.get("title"), row.get("source", {}).get("original_name"))
            )
        ]
        if len(candidates) != 1:
            raise ValueError(f"session selector {selector!r} matched {len(candidates)} rows; use an exact session ID")
        selected[candidates[0]["session_id"]] = candidates[0]
    return list(selected.values())


def validate_output(output: Path, protected: list[Path]) -> Path:
    destination = output.resolve()
    if any(destination == root.resolve() or root.resolve() in destination.parents for root in protected):
        raise ValueError("output must be outside the source repository, data and model directories")
    if destination.exists():
        raise ValueError("output directory must be new; existing results are never overwritten")
    return destination


def code_provenance() -> dict:
    files = [Path(__file__).resolve()]
    for root in (REPO / "engine/src", REPO / "sports/badminton/src"):
        files.extend(sorted(root.rglob("*.py")))
    hashes = {path.relative_to(REPO).as_posix(): sha256(path) for path in sorted(set(files))}
    result = {"files": hashes, "tree_sha256": json_hash(hashes)}
    for key, args in (("git_commit", ["rev-parse", "HEAD"]), ("git_status", ["status", "--short"])):
        try:
            result[key] = subprocess.run(
                ["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True, timeout=30,
            ).stdout.strip()
        except (OSError, subprocess.SubprocessError) as exc:
            result[key] = f"unavailable: {type(exc).__name__}"
    return result


def package_versions() -> dict:
    result = {"python": sys.version, "platform": platform.platform()}
    for name in ("torch", "onnxruntime-gpu", "onnxruntime", "rapidocr", "rtmlib", "av", "numpy", "opencv-python"):
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = None
    return result


@contextlib.contextmanager
def offline_network():
    """Block accidental downloads even for package-owned optional model loaders."""
    connect, connect_ex = socket.socket.connect, socket.socket.connect_ex

    def guarded(sock, address):
        if sock.family in (socket.AF_INET, socket.AF_INET6):
            raise OSError("network/model downloads disabled for isolated validation")
        return connect(sock, address)

    def guarded_ex(sock, address):
        if sock.family in (socket.AF_INET, socket.AF_INET6):
            raise OSError("network/model downloads disabled for isolated validation")
        return connect_ex(sock, address)

    with patch.object(socket.socket, "connect", guarded), patch.object(socket.socket, "connect_ex", guarded_ex):
        yield


def effective_model_choices(profile) -> dict:
    """Resolve the same component overrides used by the production factories."""
    legacy = {
        name: choice for name, choice in vars(profile).items()
        if hasattr(choice, "model") and hasattr(choice, "backend")
    }
    return {**legacy, **getattr(profile, "components", {})}


def override_shuttle_precision(profile, precision: str):
    selected = getattr(profile, "components", {})
    if "shuttle" in selected:
        choices = {**selected, "shuttle": selected["shuttle"].model_copy(update={"precision": precision})}
        return profile.model_copy(update={"components": choices})
    return profile.model_copy(update={"shuttle": profile.shuttle.model_copy(update={"precision": precision})})


def validation_roster_metadata(session) -> dict:
    roster = session.roster.model_dump(mode="json") if session.roster is not None else None
    return {
        "roster": roster, "roster_sha256": json_hash(roster),
        "discipline": session.roster.match_format if session.roster is not None else "unknown",
    }


def prepare_models(source: Path, destination: Path, profiles: list) -> tuple[object, dict]:
    """Copy only executable choices; preserve the original registry and its pins."""
    import yaml

    from bai_engine.runtime.registry import ModelError, ModelRegistry

    class OfflineRegistry(ModelRegistry):
        def _fetch(self, spec, dest):
            raise ModelError(f"{spec.name}: missing local verified artifact; downloads disabled")

    destination.mkdir()
    manifest_path = source / "manifest.yaml"
    manifest_bytes = manifest_path.read_bytes()
    manifest = yaml.safe_load(manifest_bytes)
    (destination / "manifest.yaml").write_bytes(manifest_bytes)
    pins_path = source / "cache/lock.json"
    pins = json.loads(pins_path.read_bytes()) if pins_path.is_file() else {}
    (destination / "cache").mkdir()
    write_json(destination / "cache/lock.json", pins)
    names = set()
    for profile in profiles:
        for choice in effective_model_choices(profile).values():
            # A weightless custom provider may use a descriptive model label.
            # Backend/model none declares no registry artifact to copy or fetch.
            if choice is not None and choice.model != "none" and choice.backend != "none":
                names.add(choice.model)
    report = {"manifest_sha256": sha256(manifest_path), "pins_sha256": json_hash(pins), "artifacts": {}}
    for name in sorted(names):
        spec = manifest["models"].get(name)
        if spec is None:
            report["artifacts"][name] = {"status": "unknown_registry_entry"}
            continue
        if spec["format"] in ("builtin", "package"):
            continue
        reference = spec.get("source", {})
        filename = Path(reference.get("file") or reference.get("url", name).rsplit("/", 1)[-1]).name
        original = source / "cache" / name / filename
        expected = spec.get("sha256")
        if expected in (None, "pin-on-first-fetch"):
            expected = pins.get(name)
        record = {"source_path": str(original), "expected_sha256": expected, "version": str(spec.get("version"))}
        report["artifacts"][name] = record
        if not original.is_file() or not expected:
            record["status"] = "missing_artifact_or_existing_pin"
            continue
        digest = sha256(original)
        if digest != expected:
            raise ValueError(f"{name}: source artifact differs from its existing integrity pin")
        target = destination / "cache" / name / filename
        target.parent.mkdir(parents=True)
        shutil.copyfile(original, target)
        if sha256(target) != digest:
            raise ValueError(f"{name}: artifact changed while copying")
        record.update(status="verified_copy", sha256=digest, staged_path=str(target))
    return OfflineRegistry(destination), report


def source_calibrations(data: Path, sid: str, supplied: Path | None) -> list:
    from bai_engine.schema import Event
    from bai_engine.schema.events import current_view

    if supplied is not None:
        value = json.loads(supplied.read_bytes())
        events = [Event.model_validate(row) for row in (value if isinstance(value, list) else [value])]
        if any(event.type != "calibration" for event in events):
            raise ValueError("--calibration-json accepts only full calibration Event records")
        return current_view(events)
    path = data / "sessions" / sid / "events.sqlite"
    if not path.is_file():
        return []
    with contextlib.closing(sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)) as connection:
        rows = connection.execute("SELECT seq,body FROM events ORDER BY seq").fetchall()
    return [event for event in current_view([Event.model_validate_json(body).with_seq(seq) for seq, body in rows])
            if event.type == "calibration"]


class CanonicalProxy:
    """Decode existing CFR MP4; verify its frame timestamps, never transcode."""

    def __init__(self, path: Path, media, chunk_frames: int):
        self.path, self.media, self.chunk_frames = path, media, chunk_frames

    def chunks(self, end: int | None):
        import av

        from bai_engine.decode import DecodedChunk

        count, frames = 0, []
        with av.open(str(self.path)) as container:
            stream = container.streams.video[0]
            stream.codec_context.thread_count = 2
            for frame in container.decode(stream):
                if end is not None and count >= end:
                    break
                if frame.pts is None or frame.time_base is None:
                    raise ValueError(f"proxy frame {count} has no timestamp")
                actual = frame.pts * frame.time_base
                expected = Fraction(count, 1) / self.media.fps
                if abs(actual - expected) > max(frame.time_base, Fraction(1, 1_000_000)):
                    raise ValueError(f"proxy frame {count} is off the canonical CFR timeline: {actual} != {expected}")
                image = frame.to_ndarray(format="bgr24")
                if image.shape[:2] != (self.media.height, self.media.width):
                    raise ValueError("proxy dimensions differ from recorded MediaInfo")
                frames.append(image)
                count += 1
                if len(frames) == self.chunk_frames:
                    yield DecodedChunk(count - len(frames), frames)
                    frames = []
            if frames:
                yield DecodedChunk(count - len(frames), frames)

    def frame_at(self, index: int):
        import av

        if not 0 <= index < self.media.n_frames:
            raise IndexError(index)
        target = Fraction(index, 1) / self.media.fps
        with av.open(str(self.path)) as container:
            stream = container.streams.video[0]
            container.seek(int(target / stream.time_base), stream=stream, any_frame=False)
            for frame in container.decode(stream):
                if frame.pts is not None and frame.pts * frame.time_base >= target:
                    return frame.to_ndarray(format="bgr24")
        raise IndexError(index)


def annotate(image, frame, calibration, path: Path) -> dict:
    import cv2
    import numpy as np

    canvas = image.copy()
    state = frame.calibration_state.value if frame.calibration_state is not None else "unknown"
    if calibration is not None and frame.cam is not None and state == "VALID" and frame.scene == "main":
        points = np.array([[-3.05, -6.7], [3.05, -6.7], [3.05, 6.7], [-3.05, 6.7]], np.float64)
        mapped = calibration.court_to_image(points)
        mapped = cv2.perspectiveTransform(mapped.reshape(-1, 1, 2), frame.cam).reshape(-1, 2)
        if np.isfinite(mapped).all() and np.abs(mapped).max() < 1e6:
            cv2.polylines(canvas, [np.rint(mapped).astype(np.int32)], True, (255, 220, 0), 2)
    for person in frame.persons:
        box = np.asarray(person.bbox)
        if not np.isfinite(box).all():
            continue
        x1, y1, x2, y2 = np.rint(box).astype(int)
        color = (70, 220, 70) if person.detector_matched is True else (0, 170, 255)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)
        cv2.putText(canvas, f"visual {person.track_id} matched={person.detector_matched}",
                    (max(0, x1), max(38, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
        if person.kps is not None:
            for x, y, confidence in person.kps:
                if np.isfinite([x, y, confidence]).all() and confidence >= 0.5:
                    cv2.circle(canvas, (round(x), round(y)), 2, color, -1)
    if frame.shuttle_xy is not None:
        x, y = frame.shuttle_xy
        cv2.circle(canvas, (round(x), round(y)), 6, (255, 0, 255), 2)
    label = f"frame {frame.frame_idx} view={frame.scene} calibration={state} shot={frame.shot_id} MODEL EVIDENCE"
    cv2.rectangle(canvas, (0, 0), (canvas.shape[1], 28), (0, 0, 0), -1)
    cv2.putText(canvas, label, (7, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1)
    if not cv2.imwrite(str(path), canvas):
        raise OSError(f"could not write {path}")
    return {
        "frame": frame.frame_idx, "path": str(path), "sha256": sha256(path),
        "label_status": "unreviewed_model_overlay",
    }


def instrument_models(perception) -> dict:
    """Count real adapter calls without retaining images/tensors or changing outputs."""
    counts = {}

    def counted(function, stage):
        counts[stage] = {"attempted": 0, "completed": 0}

        def call(*args, **kwargs):
            counts[stage]["attempted"] += 1
            result = function(*args, **kwargs)
            counts[stage]["completed"] += 1
            return result

        return call

    class CallableCounter:
        def __init__(self, original, stage):
            self.original, self.call = original, counted(original, stage)

        def __call__(self, *args, **kwargs):
            return self.call(*args, **kwargs)

        def __getattr__(self, name):
            return getattr(self.original, name)

    if perception.shuttle is not None:
        shuttle = getattr(perception.shuttle, "raw_model", perception.shuttle)
        if hasattr(shuttle, "_forward"):
            shuttle._forward = counted(shuttle._forward, "shuttle_forward")
    for attr, stage in (("detector", "player_detector"), ("pose", "pose")):
        original = getattr(perception.players, attr)
        if original is not None:
            setattr(perception.players, attr, CallableCounter(original, stage))
    if perception.scoreboard is not None:
        scoreboard = getattr(perception.scoreboard, "raw_model", perception.scoreboard)
        if hasattr(scoreboard, "ocr"):
            scoreboard.ocr = CallableCounter(scoreboard.ocr, "ocr")
    return counts


def event_log(store) -> list:
    # since() defaults to 10,000 rows; a long fresh run must export the full log.
    return sorted(store.query(live_only=False), key=lambda event: event.seq or 0)


class PerceptionRetention:
    """Optional private, write-only observations for diagnostic semantic replay."""

    def __init__(self, root: Path, *, enabled: bool = False):
        self.root = Path(root)
        if self.root.is_symlink() or not self.root.is_dir():
            raise ValueError("retention requires a real session output directory")
        self.enabled = enabled
        self.directory = self.root / "perception"
        self.manifest = self.directory / "manifest.jsonl"
        self.records = []
        if enabled:
            self.directory.mkdir(mode=0o700)
            with self.manifest.open("x", encoding="utf-8"):
                pass

    def capture(self, sport, chunk) -> dict | None:
        if not self.enabled:
            return None
        start, end = chunk.start, chunk.end
        if (
            type(start) is not int or type(end) is not int or start < 0 or end < start
            or len(chunk.frames) != end - start + 1
            or any(frame.frame_idx != start + index for index, frame in enumerate(chunk.frames))
        ):
            raise ValueError("invalid retained perception frame bounds")
        target = self.directory / f"seg_{start:09d}.msgpack"
        if target.exists() or target.is_symlink():
            raise FileExistsError(target)
        if self.directory.is_symlink() or self.manifest.is_symlink():
            raise ValueError("retention output cannot be redirected by a symlink")
        payload = sport.encode_perception(chunk)
        if not isinstance(payload, bytes):
            raise TypeError("perception encoder must return bytes")
        import msgpack

        header = msgpack.unpackb(payload, raw=False)
        encoded_frames = header.get("frames") if isinstance(header, dict) else None
        if (
            not isinstance(header, dict) or type(header.get("v")) is not int or header["v"] < 1
            or header.get("start") != start or header.get("end") != end
            or header.get("cr") != chunk.cam_ref or not isinstance(header.get("ci"), dict)
            or not isinstance(encoded_frames, list) or len(encoded_frames) != len(chunk.frames)
            or any(not isinstance(frame, dict) or frame.get("f") != start + index
                   for index, frame in enumerate(encoded_frames))
        ):
            raise ValueError("encoded perception differs from canonical frame bounds or codec identity")
        detached = json.loads(json.dumps({
            "codec_identity": header["ci"], "capabilities": sport.capabilities(), "models": header.get("models", {}),
        }, allow_nan=False))
        digest = hashlib.sha256(payload).hexdigest()
        with target.open("xb") as stream:
            stream.write(payload)
        target.chmod(0o600)
        if sha256(target) != digest:
            raise ValueError("retained perception changed while writing")
        record = {
            "path": str(target.relative_to(self.root)), "sha256": digest, "bytes": len(payload),
            "canonical_frame_bounds": [start, end + 1], "frame_bounds_convention": "half_open",
            "frame_count": len(chunk.frames), "codec_version": header["v"], "cam_ref": header.get("cr"),
            "codec_identity_sha256": json_hash(detached["codec_identity"]),
            "capabilities_sha256": json_hash(detached["capabilities"]),
            "captured_before_ingest": True, "label_status": "unreviewed_model_observations", **detached,
        }
        with self.manifest.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")
        self.records.append(record)
        return record

    def describe(self) -> dict:
        return json.loads(json.dumps({
            "enabled": self.enabled, "cached_perception_used": False, "private_perception_state_restored": False,
            "purpose": "diagnostic_semantic_replay_only", "saved_chunks": len(self.records),
            "saved_bytes": sum(record["bytes"] for record in self.records),
            "manifest": str(self.manifest.relative_to(self.root)) if self.enabled else None,
            "manifest_sha256": sha256(self.manifest) if self.enabled else None, "chunks": self.records,
            "replay_context": {"source_calibrations": "source-calibrations.json", "live_event_log": "events.jsonl"},
        }, allow_nan=False))


def ingest_with_retention(sport, chunk, retention: PerceptionRetention) -> tuple[dict | None, float]:
    started = time.monotonic()
    record = retention.capture(sport, chunk)
    retention_seconds = time.monotonic() - started
    sport.ingest(chunk)
    return record, retention_seconds


def score_checks(sport, store, session, end: int) -> dict:
    from bai_badminton.engine import BadmintonMatchEngine
    from bai_engine.schema.events import EventStatus, current_view

    raw = event_log(store)
    live = current_view(raw)
    ids = {event.event_id for event in raw}
    issues = []
    for event in raw:
        if event.type != "calibration" and event.frame_end >= end:
            issues.append({"event": event.event_id, "reason": "event_outside_processed_prefix"})
        if event.pts_us != session.media.timeline().frame_to_pts_us(event.frame_start):
            issues.append({"event": event.event_id, "reason": "event_timestamp_mismatch"})
        if event.supersedes is not None and event.supersedes not in ids:
            issues.append({"event": event.event_id, "reason": "missing_superseded_event"})
    points = [event for event in live if event.type == "point"]
    accepted = (EventStatus.CONFIRMED, EventStatus.CORRECTED, EventStatus.HUMAN_VERIFIED)
    parents = Counter(event.parent_id for event in points if event.status in accepted)
    for point in points:
        if point.status in accepted and (point.parent_id not in ids or parents[point.parent_id] != 1):
            issues.append({"event": point.event_id, "reason": "missing_or_duplicate_point_parent"})
    restored = BadmintonMatchEngine(
        session.session_id, sport.engine.cfg, store,
        player_names={player.player_id: player.name for player in session.players},
        score_rules=sport.engine.score_rules,
    )
    try:
        restored.restore_from_log(end - 1)
        restored_state = restored.public_state()
    finally:
        restored.close()
    # Product projections can add format/evidence views without changing the
    # canonical rule fold. Never compare or strip a projection to hide a real
    # live-engine state difference from its durable replay.
    live_state = sport.engine.public_state()
    public_view_state = sport.public_state()
    if live_state != restored_state:
        issues.append({"reason": "live_vs_restored_public_score_state_mismatch"})
    return {
        "issues": issues, "consistent": not issues,
        "live_state": live_state, "restored_state": restored_state, "public_view_state": public_view_state,
        "current_event_types": dict(Counter(event.type for event in live)),
        "current_event_statuses": dict(Counter(event.status.value for event in live)),
        "unknown_outcomes": sum(event.type == "rally_end" and not event.payload.get("winner") for event in live),
        "raw_events": len(raw), "current_events": len(live), "accuracy_claim_eligible": False,
    }


def run_session(raw: dict, profile, registry, args, output: Path) -> dict:
    import numpy as np

    from bai_badminton.plugin import REF_FILE, BadmintonSession
    from bai_engine.media import Tools, probe
    from bai_engine.runtime.runner import SessionRunner
    from bai_engine.schema import Event, Session, SessionStatus, TrackObject, samples_to_table
    from bai_engine.schema.events import current_view
    from bai_engine.schema.session import ParticipantRoster
    from bai_engine.store import SessionRepository

    session = Session.model_validate(raw)
    sid = session.session_id
    if not sid.isalnum() or session.media is None:
        raise ValueError("a valid source session ID and canonical MediaInfo are required")
    media = session.media
    end = args.window_end_frame if args.window_end_frame is not None else media.n_frames
    start = args.window_start_frame
    if not 0 <= start < end <= media.n_frames:
        raise ValueError("review window must satisfy 0 <= start < end <= canonical n_frames")
    root = output / "results" / sid
    root.mkdir(parents=True)
    (root / "samples").mkdir()
    report = {
        "schema": "fresh-real-video-validation-v1", "session_id": sid, "title": session.title,
        "status": "running", "accuracy_claim_eligible": False,
        "review_window_frames": [start, end], "inference_window_frames": [0, end],
        "prefix_truncated": end < media.n_frames, "started_utc": datetime.now(UTC).isoformat(),
        "cached_perception_used": False, "score_or_identity_reviews_seeded": False,
        "calibration_policy": "latest current recorded calibration; production seed/restore behavior",
        "warm_start_policy": "production source-keyframe sampler; whole-video VOD context",
        "profile": profile.model_dump(mode="json"), "profile_sha256": json_hash(profile.model_dump(mode="json")),
    }
    retention = PerceptionRetention(root, enabled=getattr(args, "retain_perception", False))
    report["perception_retention"] = retention.describe()
    write_json(root / "source-session.json", raw)
    write_json(root / "report.json", report)
    started = time.monotonic()
    repo = None
    sport = None
    try:
        source = Path(session.source.uri)
        if not source.is_file():
            choices = sorted((args.data_dir / "media" / str(session.source.sha256)).glob("source.*"))
            if len(choices) != 1:
                raise ValueError("source file missing or ambiguous; provide a local source URI")
            source = choices[0]
        source = source.resolve(strict=True)
        actual_source = sha256(source)
        if actual_source != session.source.sha256:
            raise ValueError("actual source bytes differ from the catalogue source SHA-256")
        proxy = (args.proxy_path or args.data_dir / "media" / actual_source / "proxy.mp4").resolve(strict=True)
        tools = Tools.resolve(args.ffmpeg, args.ffprobe)
        proxy_info = probe(proxy, tools)
        if proxy_info.fps != media.fps or proxy_info.display_size != (media.width, media.height):
            raise ValueError("proxy FPS/display dimensions differ from canonical MediaInfo")
        if proxy_info.rotation or proxy_info.variable_frame_rate:
            raise ValueError("proxy must already be unrotated CFR media")
        source_info = probe(source, tools)
        report["media"] = {
            "source_path": str(source), "source_sha256": actual_source,
            "proxy_path": str(proxy), "proxy_sha256": sha256(proxy),
            "canonical": media.model_dump(mode="json"), "source_pts_mapping": "unavailable",
            "duplicated_source_observations": "not identified by current pipeline",
        }
        input_metadata = validation_input_metadata(
            session.meta, media=media, proxy_sha256=report["media"]["proxy_sha256"],
        )
        report["media"].update(input_metadata)
        calibrations = source_calibrations(args.data_dir, sid, args.calibration_json)
        write_json(root / "source-calibrations.json", [event.model_dump(mode="json") for event in calibrations])
        report["calibration_input_sha256"] = sha256(root / "source-calibrations.json")
        chosen = calibrations[-1] if calibrations else None
        report["chosen_calibration_event_id"] = chosen.event_id if chosen else None
        if args.roster_json is not None:
            supplied_roster = ParticipantRoster.model_validate_json(args.roster_json.read_bytes())
            session = session.model_copy(update={"roster": supplied_roster})
        report.update(validation_roster_metadata(session))
        segment_frames = int(session.meta.get("frames_per_segment") or max(1, round(float(media.fps) * 2)))
        report["chunk_frames"] = segment_frames
        session = session.model_copy(update={
            "source": session.source.model_copy(update={"uri": str(source)}),
            "profile": profile.name, "status": SessionStatus.ANALYSING, "frontier_frame": 0, "analysed_frames": 0,
            "status_detail": "Fresh isolated real-video validation",
            "meta": {
                **input_metadata,
                "analysis_generation": "validation-" + root.parent.parent.name,
                "analysis_revision": 0, "source_session_id": sid,
                "frames_per_segment": segment_frames, "source_rotation": source_info.rotation,
                "source_video_stream_index": source_info.video_stream_index,
                "validation_window_frames": [start, end], "validation_prefix_truncated": end < media.n_frames,
            },
        })
        repo = SessionRepository(output / "data")
        repo.save(session)
        paths = repo.paths(sid)
        paths.root.mkdir(parents=True, exist_ok=True)
        media_root = repo.media_paths(actual_source).root
        media_root.mkdir(parents=True, exist_ok=True)
        proxy_link = media_root / "proxy.mp4"
        if not proxy_link.exists():
            proxy_link.symlink_to(proxy)
        store, tracks = repo.events(sid), repo.tracks(sid)
        if chosen is not None:
            copied = chosen.model_dump(exclude={"event_id", "seq", "supersedes", "parent_id"})
            # A corrected event cannot retain its supersedes link after importing
            # only geometry. Keep the original record verbatim in the input file;
            # do not manufacture a reviewed/confirmed status for the isolated copy.
            imported_status = "provisional" if chosen.status.value == "corrected" else chosen.status.value
            copied.update(session_id=sid, status=imported_status)
            store.append(Event.model_validate(copied))
            report["calibration_import_status"] = imported_status
        camera_ref = args.data_dir / "sessions" / sid / REF_FILE
        if camera_ref.is_file():
            shutil.copyfile(camera_ref, paths.root / REF_FILE)
            report["camera_reference_sha256"] = sha256(camera_ref)
        decoder = CanonicalProxy(proxy, media, segment_frames)
        # Production session obtains only its runtime cache root through settings.
        # Registry artifacts and derived caches both live in this isolated copy.
        with patch("bai_badminton.plugin.get_settings", return_value=SimpleNamespace(models_dir=output / "models")):
            sport = BadmintonSession(session, store, profile, registry, emit=lambda events: None)
        report["model_calls"] = instrument_models(sport.perception)
        sport.attach_frames(decoder.frame_at, paths.root)
        sampler = SessionRunner.__new__(SessionRunner)
        sampler.session_id, sampler.repo, sampler.tools = sid, repo, tools
        sampler.settings = SimpleNamespace(ffprobe_timeout_s=30)
        seeds = sampler._sample_keyframes(n=args.seed_frames)
        report["seed_images_sha256"] = [hashlib.sha256(image.tobytes()).hexdigest() for image in seeds]
        report["seed_images"] = len(seeds)
        sport.seed(seeds)
        del seeds
        report["capabilities_at_start"] = sport.capabilities()
        write_json(root / "report.json", report)
        sample_frames = set(np.linspace(start, end - 1, min(args.samples, end - start), dtype=int).tolist())
        counters, last_tracks, samples = Counter(), {}, []
        frame_count, timings = 0, []

        def persist_tracks():
            batch = sport.drain_tracks()
            for obj in TrackObject:
                part = [row for row in batch if row.obj == obj]
                if not part:
                    continue
                lo, hi = min(row.frame_idx for row in part), max(row.frame_idx for row in part)
                if lo <= last_tracks.get(obj, -1):
                    raise ValueError(f"overlapping drained {obj} tracks")
                if hi >= frame_count:
                    raise ValueError("track output extends beyond ingested frames")
                tracks.write_chunk(obj, lo, hi, samples_to_table(part))
                last_tracks[obj] = hi
                counters[f"track_rows_{obj.value}"] += len(part)

        with (root / "frame-coverage.jsonl").open("w", encoding="utf-8") as coverage:
            for chunk in decoder.chunks(None if end == media.n_frames else end):
                if chunk.start != frame_count:
                    raise ValueError("non-contiguous canonical inference")
                tick = time.monotonic()
                perception = sport.perceive(chunk)
                if (perception.start, perception.end) != (chunk.start, chunk.end):
                    raise ValueError("perception changed canonical chunk bounds")
                infer_seconds = time.monotonic() - tick
                for frame, pixels in zip(perception.frames, chunk.frames, strict=True):
                    cs = frame.calibration_state.value if frame.calibration_state is not None else "unknown"
                    row = {
                        "frame": frame.frame_idx, "view": frame.scene, "shot_id": frame.shot_id,
                        "calibration_state": cs, "shuttle_observed": frame.shuttle_xy is not None,
                        "detector_observed": frame.detector_observed, "persons": len(frame.persons),
                        "detector_matched_persons": sum(p.detector_matched is True for p in frame.persons),
                        "posed_persons": sum(p.kps is not None for p in frame.persons),
                        "unresolved_visual_ids": sum(p.track_id < 0 for p in frame.persons),
                        "review_window": start <= frame.frame_idx < end,
                    }
                    coverage.write(json.dumps(row, allow_nan=False) + "\n")
                    counters[f"view_{frame.scene}"] += 1
                    counters[f"calibration_{cs}"] += 1
                    counters["observed_shuttle_frames"] += row["shuttle_observed"]
                    counters["detector_observed_frames"] += frame.detector_observed is True
                    if frame.frame_idx in sample_frames:
                        sample_path = root / "samples" / f"f{frame.frame_idx:09d}.jpg"
                        samples.append(annotate(pixels, frame, sport.calibration, sample_path))
                tick = time.monotonic()
                _, retention_seconds = ingest_with_retention(sport, perception, retention)
                frame_count = chunk.end + 1
                report["frames_processed"] = frame_count
                persist_tracks()
                timings.append({"start": chunk.start, "end": chunk.end, "perception_s": infer_seconds,
                                "ingest_and_track_s": time.monotonic() - tick - retention_seconds,
                                "perception_retention_s": retention_seconds})
                repo.update(sid, frontier_frame=chunk.end, analysed_frames=frame_count)
                print(json.dumps({"type": "progress", "session_id": sid, "frames": frame_count,
                                  "target_frames": end, "elapsed_s": round(time.monotonic() - started, 2)}), flush=True)
        report["frames_processed"] = frame_count
        if frame_count != end:
            raise ValueError(f"decoded {frame_count} canonical frames, expected {end}")
        sport.flush()
        persist_tracks()
        report["flush_boundary"] = "truncated_prefix_incomplete_rally" if end < media.n_frames else "end_of_media"
        report["coverage"] = dict(counters)
        report["samples"] = samples
        report["chunk_timings"] = timings
        report["capabilities"] = sport.capabilities()
        report["degraded"] = sport.degraded()
        report["score_consistency"] = score_checks(sport, store, session, frame_count)
        report["analytics"] = sport.analytics()
        raw_events = event_log(store)
        for name, events in (("events.jsonl", raw_events), ("current-events.jsonl", current_view(raw_events))):
            (root / name).write_text("".join(event.model_dump_json() + "\n" for event in events), encoding="utf-8")
        required_unavailable = [
            name for name, value in report["capabilities"].items()
            if value.get("required") and value.get("status") in ("unavailable", "disabled", "unsupported")
        ]
        report["required_unavailable"] = required_unavailable
        report["required_stages_not_exercised"] = [
            name for name in ("shuttle_forward", "player_detector", "pose")
            if report["model_calls"].get(name, {}).get("completed", 0) == 0
        ]
        report["status"] = "failed" if report["score_consistency"]["issues"] else "partial" if (
            required_unavailable or report["required_stages_not_exercised"] or end < media.n_frames
        ) else "complete"
        completed_status = (
            SessionStatus.ANALYSED if end == media.n_frames and report["status"] != "failed" else SessionStatus.FAILED
        )
        final = repo.update(
            sid, status=completed_status, status_detail=f"Isolated validation: {report['status']}",
            meta={**session.meta, "capabilities": report["capabilities"], "degraded": report["degraded"]},
        )
        write_json(root / "session.json", final.model_dump(mode="json"))
        report["artifact_hashes"] = {name: sha256(root / name) for name in (
            "events.jsonl", "current-events.jsonl", "session.json", "frame-coverage.jsonl",
        )}
        report["track_files"] = {
            str(path.relative_to(output)): sha256(path) for path in sorted(paths.tracks.rglob("*.parquet"))
        }
        # Detect concurrent replacement of the immutable media inputs.
        if sha256(source) != actual_source or sha256(proxy) != report["media"]["proxy_sha256"]:
            raise ValueError("source/proxy bytes changed during validation")
    except Exception as exc:
        report.update(status="failed", error={"type": type(exc).__name__, "message": str(exc),
                                               "traceback": traceback.format_exc()})
        if repo is not None:
            with contextlib.suppress(Exception):
                repo.set_status(sid, SessionStatus.FAILED, str(exc))
    finally:
        report["perception_retention"] = retention.describe()
        if repo is not None:
            camera_reference = repo.paths(sid).root / REF_FILE
            report["perception_retention"]["replay_context"]["camera_reference"] = {
                "path_relative_to_run": str(camera_reference.relative_to(output)),
                "sha256": sha256(camera_reference) if camera_reference.is_file() else None,
                "note": "existing runtime reference only; no extra images are retained in perception artifacts",
            }
        if sport is not None:
            report["capabilities"] = sport.capabilities()
            report["degraded"] = sport.degraded()
        if repo is not None:
            try:
                rows = event_log(repo.events(sid))
                for name, events in (("events.jsonl", rows), ("current-events.jsonl", current_view(rows))):
                    content = "".join(event.model_dump_json() + "\n" for event in events)
                    (root / name).write_text(content, encoding="utf-8")
                saved = repo.get(sid)
                if saved is not None:
                    write_json(root / "session.json", saved.model_dump(mode="json"))
                report["artifact_hashes"] = {name: sha256(root / name) for name in (
                    "events.jsonl", "current-events.jsonl", "session.json", "frame-coverage.jsonl",
                ) if (root / name).is_file()}
            except Exception as exc:
                report["export_error"] = {"type": type(exc).__name__, "message": str(exc)}
                report["status"] = "failed"
        report["elapsed_s"] = time.monotonic() - started
        report["finished_utc"] = datetime.now(UTC).isoformat()
        write_json(root / "report.json", report)
        if repo is not None:
            repo.close()
        sport = None
        gc.collect()
        with contextlib.suppress(ImportError):
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", type=Path, default=REPO / "data")
    parser.add_argument("--models-dir", type=Path, default=REPO / "models")
    parser.add_argument("--profiles-dir", type=Path, default=REPO / "config/profiles")
    parser.add_argument(
        "--session", action="append", default=[], help="exact ID or unique title/original-name substring",
    )
    parser.add_argument("--session-json", type=Path, help="one Session descriptor instead of the source catalogue")
    parser.add_argument("--proxy-path", type=Path, help="existing canonical CFR proxy; one selected session only")
    parser.add_argument("--calibration-json", type=Path, help="full calibration Event JSON; one selected session only")
    parser.add_argument("--roster-json", type=Path, help="explicit ParticipantRoster override, recorded in provenance")
    parser.add_argument("--profile", help="override source session compute profile")
    parser.add_argument("--shuttle-precision", choices=("fp32", "fp16"), help="explicit, recorded profile override")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--window-start-frame", type=int, default=0)
    parser.add_argument("--window-end-frame", type=int)
    parser.add_argument("--seed-frames", type=int, default=24)
    parser.add_argument("--samples", type=int, default=12)
    parser.add_argument("--retain-perception", action="store_true",
                        help="retain private pre-ingest observation blobs for diagnostic replay; inference stays fresh")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.list:
            rows = read_catalogue(args.data_dir)
            print(json.dumps([{"session_id": row["session_id"], "title": row["title"],
                               "n_frames": (row.get("media") or {}).get("n_frames"),
                               "profile": row.get("profile"),
                               "original_name": row.get("source", {}).get("original_name")}
                              for row in rows], indent=2))
            return 0
        if args.output_dir is None:
            raise ValueError("--output-dir is required for inference")
        output = validate_output(args.output_dir, [REPO, args.data_dir, args.models_dir])
        if not 1 <= args.seed_frames <= 100 or not 1 <= args.samples <= 100:
            raise ValueError("seed/sample counts must be between 1 and 100")
        if args.session_json is not None:
            if args.session:
                raise ValueError("choose --session-json or --session, not both")
            rows = [json.loads(args.session_json.read_bytes())]
        else:
            if not args.session:
                raise ValueError("provide --session selectors or --session-json; --list shows available sessions")
            rows = select_sessions(read_catalogue(args.data_dir), args.session)
        if len(rows) != 1 and (args.proxy_path is not None or args.calibration_json is not None):
            raise ValueError("explicit proxy/calibration paths require exactly one session")
    except (OSError, ValueError, sqlite3.Error) as exc:
        parser.error(str(exc))
    # Keep --list/safety preflight independent from optional inference dependencies.
    import bai_badminton.plugin as loaded_plugin
    import bai_engine.config as loaded_config
    import bai_engine.runtime.registry as loaded_registry
    from bai_engine.config import load_profile

    loaded_sources = {}
    for module in (loaded_config, loaded_registry, loaded_plugin):
        path = Path(module.__file__).resolve()
        if REPO not in path.parents:
            parser.error(f"loaded {module.__name__} from another checkout: {path}")
        loaded_sources[module.__name__] = {"path": str(path), "sha256": sha256(path)}

    profiles = [load_profile(args.profile or row.get("profile", "gpu-rtx4000"), args.profiles_dir) for row in rows]
    if args.shuttle_precision:
        profiles = [override_shuttle_precision(p, args.shuttle_precision) for p in profiles]
    output.mkdir(parents=True, exist_ok=False)
    manifest = {"schema": "fresh-real-video-run-v1", "started_utc": datetime.now(UTC).isoformat(),
                "argv": sys.argv[1:] if argv is None else argv,
                "code": code_provenance(), "runtime": package_versions(),
                "loaded_sources": loaded_sources,
                "source_sqlite_access": "mode=ro; SQLite-managed WAL/SHM coordination sidecars permitted",
                "accuracy_claim_eligible": False, "network": "Internet sockets blocked during model execution",
                "source_catalogue_sha256": (
                    sha256(args.data_dir / "sessions.sqlite") if args.session_json is None else None
                )}
    write_json(output / "run.json", manifest)
    try:
        registry, artifacts = prepare_models(args.models_dir, output / "models", profiles)
        manifest["models"] = artifacts
        write_json(output / "run.json", manifest)
        with offline_network():
            reports = [
                run_session(row, profile, registry, args, output)
                for row, profile in zip(rows, profiles, strict=True)
            ]
        manifest["sessions"] = [{"session_id": report["session_id"], "status": report["status"],
                                  "report": f"results/{report['session_id']}/report.json"} for report in reports]
        code = 1 if any(row["status"] == "failed" for row in reports) else 2 if any(
            row["status"] == "partial" for row in reports
        ) else 0
    except Exception as exc:
        manifest["error"] = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
        code = 1
    # Include derived ONNX/extraction manifests as well as raw copied weights.
    # RapidOCR package-selected model digests are separately recorded by its
    # production runtime capability metadata in each session report.
    manifest["staged_model_files"] = {
        path.relative_to(output).as_posix(): sha256(path)
        for path in sorted((output / "models").rglob("*")) if path.is_file()
    }
    manifest.update(exit_code=code, finished_utc=datetime.now(UTC).isoformat())
    write_json(output / "run.json", manifest)
    print(json.dumps({"run_report": str(output / "run.json"), "exit_code": code}), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
