"""Opt-in, bounded Redis/external-worker validation in the configured GPU runtime.

Example (Redis itself is started/stopped by the operator, never by this script)::

    source ../gpu-env.sh
    export BAI_VALIDATION_REDIS_URL=redis://127.0.0.1:16379/0
    .venv/bin/python research/validate_redis_runtime.py --confirm-private-redis \
        --output-dir /tmp/bai-redis-validation-new --video /path/to/short-clip.mp4

Plan: reject shared/nonempty Redis; probe real bounded BLPOP and cross-process
command/pubsub; start separate API/engine processes; upload a short real clip with
all models disabled; exercise synthetic score correction, WS replay/reconnect,
graceful API/worker restart, and uploaded-session reanalysis/generation refresh.
Synthetic score observations are propagation evidence, never video accuracy.
No install, download, Redis FLUSH, source mutation or production code changes.
Logs/data/report remain under a NEW directory. Only spawned process groups stop.
Exit 0 means all requested checks passed; exit 1 preserves the failing evidence.
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import hashlib
import importlib.metadata
import json
import os
import signal
import socket
import sqlite3
import subprocess
import sys
import time
import traceback
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, BinaryIO
from urllib.parse import unquote, urlencode, urlsplit
from uuid import uuid4

REPO = Path(__file__).resolve().parents[1]
PROFILE = "redis-validation-none"
PROFILE_YAML = """description: Redis runtime validation; all learned models disabled
device: cpu
analysis_height: 360
chunk_frames: 60
lead_buffer_s: 2.0
shuttle: {model: none, backend: none}
player_detector: {model: none, backend: none}
pose: {model: none, backend: none}
stroke: {model: none, backend: none}
racket: {model: none, backend: none}
contact: {model: none, backend: none}
ocr: {model: none, backend: none}
escalation_budget: 0.0
"""


class ValidationRuntimeError(RuntimeError):
    """A concrete failed assertion, missing prerequisite, or refused unsafe setup."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationRuntimeError(message)


def validate_redis_url(url: str, *, confirmed_private: bool, allow_default_port: bool = False) -> dict[str, Any]:
    """Return credential-free endpoint metadata; this never opens a connection."""
    require(confirmed_private, "Explicit --confirm-private-redis is required")
    parsed = urlsplit(url)
    require(parsed.scheme in {"redis", "rediss"}, "A redis:// or rediss:// URL is required")
    require(parsed.hostname in {"127.0.0.1", "localhost", "::1"}, "Only a private loopback Redis is supported")
    require(not parsed.query and not parsed.fragment, "Redis URL query/fragment options are not supported")
    try:
        port = parsed.port if parsed.port is not None else 6379
    except ValueError as exc:
        raise ValidationRuntimeError("Invalid Redis port") from exc
    require(1 <= port <= 65535, "Invalid Redis port")
    require(port != 6379 or allow_default_port, "Default Redis port 6379 requires --allow-default-port")
    database = parsed.path.removeprefix("/") or "0"
    require(database.isdecimal(), "Redis database must be a nonnegative integer")
    return {"scheme": parsed.scheme, "host": parsed.hostname, "port": port, "database": int(database)}


def fresh_output(path: Path) -> Path:
    require(not path.exists() and not path.is_symlink(), "Output directory must be new; existing results are preserved")
    path = path.resolve()
    require(not path.is_relative_to((REPO / "models").resolve()), "Output must not be inside model artifacts")
    require(not path.is_relative_to((REPO / "data").resolve()), "Output must not be inside existing application data")
    path.mkdir(parents=True, mode=0o700)
    return path


def json_safe(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"bytes": len(value), "sha256": hashlib.sha256(value).hexdigest()}
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(json_safe(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


class Report:
    def __init__(self, output: Path, endpoint: dict[str, Any], timeout: float, redis_url: str = "") -> None:
        self.output = output
        self.deadline = time.monotonic() + timeout
        self._redactions = [value for value in (redis_url, unquote(urlsplit(redis_url).password or "")) if value]
        self.body: dict[str, Any] = {
            "schema": "redis-runtime-validation-v1", "run_id": uuid4().hex,
            "started_at": datetime.now(UTC).isoformat(), "status": "running", "endpoint": endpoint,
            "evidence": {
                "transport": "real Redis; separate processes; real HTTP and WebSocket sockets",
                "upload": "real input pixels; all learned models disabled; no perception accuracy claim",
                "score": "synthetic observations through real rules/store/correction code",
                "restart": "graceful owned API/worker restarts; no Redis persistence or crash-durability claim",
            },
            "stages": [], "processes": [], "cleanup": [],
        }
        self.save()

    def remaining(self, limit: float) -> float:
        value = min(limit, self.deadline - time.monotonic())
        require(value > 0, "Overall validation deadline expired")
        return value

    def save(self) -> None:
        write_json(self.output / "report.json", self.body)

    def redact(self, text: str) -> str:
        for secret in self._redactions:
            text = text.replace(secret, "<redacted>")
        return text

    @contextlib.contextmanager
    def stage(self, name: str) -> Iterator[dict[str, Any]]:
        row: dict[str, Any] = {"name": name, "status": "running"}
        self.body["stages"].append(row)
        self.save()
        started = time.monotonic()
        try:
            yield row
        except BaseException as exc:
            row.update(status="failed", error_type=type(exc).__name__, error=self.redact(str(exc)))
            raise
        else:
            row["status"] = "passed"
        finally:
            row["elapsed_s"] = round(time.monotonic() - started, 6)
            self.save()


@dataclass
class OwnedProcess:
    name: str
    process: subprocess.Popen[bytes]
    log: BinaryIO
    stopped: bool = False


class Processes:
    def __init__(self, report: Report, env: dict[str, str], workdir: Path) -> None:
        self.report, self.env, self.workdir = report, env, workdir
        self.owned: list[OwnedProcess] = []

    def start(self, name: str, arguments: list[str]) -> OwnedProcess:
        log = (self.report.output / f"{name}.log").open("xb")
        try:
            child = subprocess.Popen(
                [sys.executable, *arguments], cwd=self.workdir, env=self.env,
                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
            )
        except BaseException:
            log.close()
            raise
        owned = OwnedProcess(name, child, log)
        self.owned.append(owned)
        self.report.body["processes"].append({"name": name, "pid": child.pid, "log": f"{name}.log"})
        self.report.save()
        return owned

    def check(self, *children: OwnedProcess) -> None:
        for child in children:
            require(child.process.poll() is None, f"{child.name} exited; inspect {child.name}.log")

    def wait(self, child: OwnedProcess, timeout: float) -> None:
        try:
            code = child.process.wait(timeout=self.report.remaining(timeout))
        except subprocess.TimeoutExpired as exc:
            raise ValidationRuntimeError(f"{child.name} exceeded its deadline; inspect {child.name}.log") from exc
        require(code == 0, f"{child.name} failed with exit {code}; inspect {child.name}.log")

    def stop(self, child: OwnedProcess, *, timeout: float = 20) -> dict[str, Any]:
        if child.stopped:
            return {"name": child.name, "already_stopped": True}
        child.stopped = True
        forced = False
        # Every group was created by start_new_session here. Redis is never owned.
        if child.process.poll() is None:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(child.process.pid, signal.SIGTERM)
            try:
                child.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                forced = True
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(child.process.pid, signal.SIGKILL)
                child.process.wait(timeout=5)
        child.log.close()
        result = {"name": child.name, "pid": child.process.pid, "forced": forced,
                  "returncode": child.process.returncode}
        self.report.body["cleanup"].append(result)
        self.report.save()
        return result

    def close(self) -> None:
        for child in reversed(self.owned):
            try:
                self.stop(child, timeout=10)
            except Exception as exc:
                self.report.body["cleanup"].append({"name": child.name, "error": self.report.redact(str(exc)),
                                                    "forced": True})
                self.report.save()


def environment(output: Path, redis_url: str, allow_default_port: bool, token: str) -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("BAI_")}
    roots = [REPO, REPO / "engine/src", REPO / "sports/badminton/src", REPO / "agents/src", REPO / "apps/api/src"]
    env["PYTHONPATH"] = os.pathsep.join([*(str(path) for path in roots), env.get("PYTHONPATH", "")])
    env.update({
        "PYTHONUNBUFFERED": "1", "BAI_DATA_DIR": str(output / "data"),
        "BAI_PROFILES_DIR": str(output / "profiles"), "BAI_MODELS_DIR": str(output / "models"),
        "BAI_PROFILE": PROFILE, "BAI_ENGINE_MODE": "external", "BAI_REDIS_URL": redis_url,
        "BAI_BIND_HOST": "127.0.0.1", "BAI_PASSPHRASE": "", "BAI_YOUTUBE_INGEST": "false",
        "BAI_PROXY_HEIGHT": "360", "BAI_MAX_DURATION_S": "60",
        "BAI_FFMPEG": os.environ.get("BAI_FFMPEG", "ffmpeg"),
        "BAI_FFPROBE": os.environ.get("BAI_FFPROBE", "ffprobe"),
        "BAI_VALIDATION_TOKEN": token, "BAI_VALIDATION_PRIVATE": "1",
        "BAI_VALIDATION_ALLOW_DEFAULT": "1" if allow_default_port else "0",
    })
    return env


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _child_probe(kind: str, result_path: Path) -> None:
    """Owned helper process; its parent supplies private-service configuration."""
    url = os.environ["BAI_REDIS_URL"]
    token = os.environ["BAI_VALIDATION_TOKEN"]
    validate_redis_url(url, confirmed_private=os.environ.get("BAI_VALIDATION_PRIVATE") == "1",
                       allow_default_port=os.environ.get("BAI_VALIDATION_ALLOW_DEFAULT") == "1")
    if kind == "score":
        from apps.web.e2e.score_fixture import create_score_fixture
        from bai_engine.store import SessionRepository

        with contextlib.closing(SessionRepository(Path(os.environ["BAI_DATA_DIR"]))) as repo:
            fixture = create_score_fixture(repo, PROFILE, media=True)
        write_json(result_path, {**fixture, "evidence": "synthetic-score-observations; not video inference"})
        return
    from bai_engine.bus import RedisBus

    with contextlib.closing(RedisBus(url)) as bus:
        if kind == "timeouts":
            rows = []
            for timeout in (0.05, 0.5, 1.5):
                started = time.monotonic()
                message = bus.next_command(timeout=timeout)
                elapsed = time.monotonic() - started
                require(message is None, "Private command queue was not empty during BLPOP timing")
                require(timeout * 0.8 <= elapsed <= timeout + 2.0, "BLPOP did not honor a bounded fractional timeout")
                rows.append({"requested_s": timeout, "elapsed_s": elapsed})
            write_json(result_path, {"pid": os.getpid(), "timings": rows})
        elif kind == "command":
            message = bus.next_command(timeout=5.0)
            require(message == {"cmd": "validation_probe", "token": token}, "Cross-process command differed")
            write_json(result_path, {"pid": os.getpid(), "command": message})
        elif kind == "command-send":
            bus.send_command({"cmd": "validation_probe", "token": token})
            write_json(result_path, {"pid": os.getpid(), "sent": True})
        elif kind == "publish":
            bus.publish(f"validation.{token}.events", {
                "type": "validation", "token": token, "binary": b"redis-msgpack-roundtrip",
            })
            write_json(result_path, {"pid": os.getpid(), "published": True})
        elif kind == "subscriber":
            async def receive() -> dict[str, Any]:
                channel = f"validation.{token}.events"
                async with contextlib.aclosing(bus.subscribe(channel)) as messages:
                    return await asyncio.wait_for(anext(messages), timeout=10)

            message = asyncio.run(receive())
            expected = {"type": "validation", "token": token, "binary": b"redis-msgpack-roundtrip"}
            require(message == expected, "Cross-process pub/sub or binary payload differed")
            write_json(result_path, {"pid": os.getpid(), "message": message})
        else:
            raise ValidationRuntimeError("Unknown helper probe")


def transport(report: Report, children: Processes, redis_url: str) -> None:
    import redis

    from bai_engine.bus import RedisBus

    with redis.Redis.from_url(redis_url, socket_connect_timeout=3, socket_timeout=3) as control:
        with report.stage("private_redis_preflight") as row:
            require(control.ping(), "Redis PING failed")
            require(control.dbsize() == 0, "Selected Redis database is not empty; refusing shared/existing state")
            require(len(control.client_list()) == 1, "Redis already has other clients; refusing shared service")
            require(not control.pubsub_channels(), "Redis has pre-existing pub/sub channels; refusing shared service")
            row.update(redis_version=control.info("server")["redis_version"], empty_database=True)
        for kind in ("timeouts", "command", "subscriber"):
            with report.stage(f"real_redis_{kind}") as row:
                path = report.output / f"transport-{kind}.json"
                child = children.start(f"transport-{kind}", [str(Path(__file__).resolve()), "--_probe", kind,
                                                            "--_probe-output", str(path)])
                if kind == "subscriber":
                    channel = f"validation.{report.body['run_id']}.events"
                    deadline = time.monotonic() + report.remaining(8)
                    while control.pubsub_numsub(channel)[0][1] != 1:
                        children.check(child)
                        require(time.monotonic() < deadline, "Redis subscriber did not become ready")
                        time.sleep(0.05)
                if kind in {"command", "subscriber"}:
                    sending = "command-send" if kind == "command" else "publish"
                    sender = children.start(f"transport-{sending}", [
                        str(Path(__file__).resolve()), "--_probe", sending,
                        "--_probe-output", str(path.with_suffix(".sent.json")),
                    ])
                    children.wait(sender, 10)
                    children.stop(sender)
                children.wait(child, 12)
                children.stop(child)
                row.update(json.loads(path.read_text(encoding="utf-8")))
        require(control.llen(RedisBus.COMMAND_KEY) == 0, "Transport probes left commands behind")


def durable_rows(data: Path, sid: str) -> list[dict[str, Any]]:
    require(sid.isalnum(), "Invalid session identifier in server response")
    path = data / "sessions" / sid / "events.sqlite"
    with contextlib.closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as connection:
        return [json.loads(row[0]) for row in connection.execute("SELECT body FROM events ORDER BY seq")]


async def application(report: Report, children: Processes, video: Path, stage_timeout: float) -> None:
    import httpx
    import msgpack
    import websockets

    port = free_port()
    base = f"http://127.0.0.1:{port}"
    ws_base = f"ws://127.0.0.1:{port}"
    report.body["api"] = {"host": "127.0.0.1", "port": port}
    api_round, worker_round = 0, 0

    def start_api() -> OwnedProcess:
        nonlocal api_round
        api_round += 1
        return children.start(f"api-{api_round}", ["-m", "bai_api.cli", "serve", "--host", "127.0.0.1",
                                                  "--port", str(port)])

    def start_worker() -> OwnedProcess:
        nonlocal worker_round
        worker_round += 1
        return children.start(f"worker-{worker_round}", ["-m", "bai_api.cli", "engine"])

    api, worker = start_api(), start_worker()
    async with httpx.AsyncClient(base_url=base, timeout=10, trust_env=False) as client:
        async def request(method: str, path: str, **kwargs: Any) -> Any:
            children.check(api, worker)
            response = await client.request(method, path, **kwargs)
            require(response.is_success, f"{method} {path}: HTTP {response.status_code}: {response.text[:1000]}")
            return response.json() if response.content else None

        async def ready() -> None:
            deadline = time.monotonic() + report.remaining(40)
            while time.monotonic() < deadline:
                children.check(api, worker)
                try:
                    response = await client.get("/api/health")
                    if response.status_code == 200:
                        return
                except httpx.TransportError:
                    await asyncio.sleep(0.1)
                    continue
                await asyncio.sleep(0.1)
            raise ValidationRuntimeError("API did not become ready")

        async def analysed(sid: str, *, after_revision: int | None = None) -> dict[str, Any]:
            deadline = time.monotonic() + report.remaining(stage_timeout)
            while time.monotonic() < deadline:
                session = await request("GET", f"/api/sessions/{sid}")
                require(session["status"] != "failed", f"Session failed: {session.get('status_detail')}")
                newer = (
                    after_revision is None
                    or int(session.get("meta", {}).get("analysis_revision", 0)) > after_revision
                )
                if session["status"] == "analysed" and newer:
                    return session
                await asyncio.sleep(0.2)
            raise ValidationRuntimeError(f"Session {sid} did not finish before its deadline")

        async def receive(ws: Any, log_name: str, predicate: Any) -> dict[str, Any]:
            deadline = time.monotonic() + report.remaining(stage_timeout)
            while time.monotonic() < deadline:
                raw = await asyncio.wait_for(ws.recv(), timeout=max(0.01, deadline - time.monotonic()))
                message = msgpack.unpackb(raw, raw=False) if isinstance(raw, bytes) else json.loads(raw)
                with (report.output / f"{log_name}.jsonl").open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(json_safe(message)) + "\n")
                if predicate(message):
                    return message
            raise ValidationRuntimeError(f"WebSocket {log_name} did not receive its expected message")

        def connect(sid: str, **cursor: Any) -> Any:
            return websockets.connect(f"{ws_base}/ws/sessions/{sid}?{urlencode(cursor)}",
                                      open_timeout=10, close_timeout=5, max_size=16 * 1024**2)

        async def replay(ws: Any, name: str, start: int = 0) -> tuple[dict[str, Any], list[dict[str, Any]]]:
            hello = await receive(ws, name, lambda message: message.get("type") == "hello")
            if hello.get("reset"):
                start = 0
            target = int(hello["last_seq"])
            rows: list[dict[str, Any]] = []
            while start < target:
                page = await receive(ws, name, lambda message: message.get("type") == "events")
                rows.extend(page["events"])
                require(bool(page["events"]), "Empty replay page before the declared frontier")
                require(
                    [event["seq"] for event in page["events"]] ==
                    list(range(start + 1, start + len(page["events"]) + 1)),
                    "WS replay skipped/duplicated sequence",
                )
                start = page["events"][-1]["seq"]
            require(start == target, "WS replay crossed its captured frontier")
            return hello, rows

        with report.stage("external_api_worker_start") as row:
            await ready()
            system = await request("GET", "/api/system")
            require(system["engine_mode"] == "external" and not system["runners"], "API is not external-only")
            row.update(api_pid=api.process.pid, worker_pid=worker.process.pid, profile=PROFILE)

        with report.stage("real_clip_upload_model_free_completion") as row:
            with video.open("rb") as stream:
                uploaded = await request("POST", "/api/sessions", files={"file": (video.name, stream, "video/mp4")},
                                         data={"profile": PROFILE, "title": "Redis validation real clip"}, timeout=60)
            sid = uploaded["session_id"]
            session = await analysed(sid)
            events = await request("GET", f"/api/sessions/{sid}/events?since_seq=0")
            state = await request("GET", f"/api/sessions/{sid}/state")
            disk = durable_rows(report.output / "data", sid)
            require([event["event_id"] for event in events["events"]] == [event["event_id"] for event in disk],
                    "Uploaded-session API events differ from durable SQLite rows")
            require(session["analysed_frames"] > 0 and session["media"]["n_frames"] > 0,
                    "Uploaded source did not produce a canonical analysed timeline")
            row.update(session_id=sid, source_sha256=session["source"]["sha256"],
                       media=session["media"], analysed_frames=session["analysed_frames"],
                       event_count=len(disk), state=state, capabilities=session.get("meta", {}).get("capabilities"))

        with report.stage("synthetic_score_fixture_creation") as row:
            fixture_path = report.output / "synthetic-score-fixture.json"
            seed = children.start("seed-synthetic-score", [str(Path(__file__).resolve()), "--_probe", "score",
                                                           "--_probe-output", str(fixture_path)])
            await asyncio.to_thread(children.wait, seed, stage_timeout)
            children.stop(seed)
            fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
            score_sid = fixture["session_id"]
            require(fixture["score"] == {"P1": 1, "P2": 1}, "Unexpected synthetic fixture score")
            row.update(fixture)

        with report.stage("redis_score_correction_and_live_websocket") as row:
            async with connect(score_sid) as ws:
                hello, before = await replay(ws, "ws-score-live")
                require(hello["state"]["score"] == {"P1": 1, "P2": 1}, "Initial WS score differs")
                accepted = await request("POST", f"/api/sessions/{score_sid}/corrections", json={
                    "kind": "winner", "rally_event_id": fixture["rally_event_ids"][1], "winner": "P1",
                })
                require(accepted["status"] == "accepted", "Correction was not queued")
                changed = await receive(ws, "ws-score-live", lambda message:
                                        message.get("type") == "state" and
                                        (message.get("state") or {}).get("score") == {"P1": 2, "P2": 0})
                state = await request("GET", f"/api/sessions/{score_sid}/state")
                require(state["state"]["score"] == {"P1": 2, "P2": 0}, "Durable corrected score differs")
                after = await request("GET", f"/api/sessions/{score_sid}/events?since_seq=0")
                require(after["last_seq"] > hello["last_seq"], "Correction did not append durable events")
                disk = durable_rows(report.output / "data", score_sid)
                require([event["event_id"] for event in after["events"]] == [event["event_id"] for event in disk],
                        "Corrected API event log differs from SQLite")
                row.update(before_count=len(before), last_seq=after["last_seq"], state=changed["state"])

        with report.stage("websocket_reconnect_durable_replay") as row:
            cursor = after["last_seq"] // 2
            async with connect(score_sid, analysis_revision=after["analysis_revision"], last_seq=cursor) as ws:
                greeting, tail = await replay(ws, "ws-score-reconnect", cursor)
                require([event["event_id"] for event in tail] ==
                        [event["event_id"] for event in after["events"] if event["seq"] > cursor],
                        "Reconnect did not replay the exact durable tail")
                require(greeting["state"]["score"] == {"P1": 2, "P2": 0}, "Reconnect lost corrected score")
                row.update(cursor=cursor, replayed=len(tail), last_seq=greeting["last_seq"])

        with report.stage("api_restart_preserves_durable_score") as row:
            stopped = children.stop(api)
            require(not stopped["forced"], "API required forced shutdown")
            api = start_api()
            await ready()
            restarted = await request("GET", f"/api/sessions/{score_sid}/events?since_seq=0")
            require(restarted == after, "API restart changed durable event history")
            async with connect(score_sid, analysis_revision=after["analysis_revision"], last_seq=cursor) as ws:
                greeting, tail = await replay(ws, "ws-api-restart", cursor)
                require(greeting["state"]["score"] == {"P1": 2, "P2": 0}, "API restart lost score")
                row.update(api_pid=api.process.pid, replayed=len(tail), last_seq=greeting["last_seq"])

        with report.stage("worker_restart_restores_and_corrects_score") as row:
            stopped = children.stop(worker)
            require(not stopped["forced"], "Worker required forced shutdown")
            worker = start_worker()
            async with connect(
                score_sid, analysis_revision=after["analysis_revision"], last_seq=after["last_seq"]
            ) as ws:
                await replay(ws, "ws-worker-restart", after["last_seq"])
                current = await request("GET", f"/api/sessions/{score_sid}/events?types=rally_end")
                latest = max(current["events"], key=lambda event: event["frame_start"])
                await request("POST", f"/api/sessions/{score_sid}/corrections", json={
                    "kind": "winner", "rally_event_id": latest["event_id"], "winner": "P2",
                })
                changed = await receive(ws, "ws-worker-restart", lambda message:
                                        message.get("type") == "state" and
                                        (message.get("state") or {}).get("score") == {"P1": 1, "P2": 1})
                require((await request("GET", f"/api/sessions/{score_sid}/state"))["state"]["score"] ==
                        {"P1": 1, "P2": 1}, "Restarted worker correction did not persist")
                row.update(worker_pid=worker.process.pid, state=changed["state"])

        with report.stage("external_reanalysis_generation_refresh") as row:
            old = await request("GET", f"/api/sessions/{sid}/events?since_seq=0")
            old_session = await request("GET", f"/api/sessions/{sid}")
            async with connect(sid, analysis_revision=old["analysis_revision"], last_seq=old["last_seq"]) as ws:
                await replay(ws, "ws-reanalysis", old["last_seq"])
                await request("POST", f"/api/sessions/{sid}/reanalyse")
                renewed = await analysed(sid, after_revision=old["analysis_revision"])
                generation = renewed.get("meta", {}).get("analysis_generation")
                require(bool(generation) and generation != old_session.get("meta", {}).get("analysis_generation"),
                        "Reanalysis did not replace generation")
                # Also request a seek: durable sync must work if a pub/sub hint was missed.
                await ws.send(json.dumps({"type": "seek", "frame": 0}))
                reset = await receive(ws, "ws-reanalysis", lambda message:
                                      message.get("type") == "hello" and message.get("generation") == generation)
                require(reset["reset"], "Active WebSocket did not announce generation reset")
                fresh = await request("GET", f"/api/sessions/{sid}/events?since_seq=0")
                disk = durable_rows(report.output / "data", sid)
                require(fresh["analysis_revision"] == renewed["meta"]["analysis_revision"], "API revision is stale")
                require([event["event_id"] for event in fresh["events"]] == [event["event_id"] for event in disk],
                        "API cached old-generation event storage")
                row.update(session_id=sid, old_revision=old["analysis_revision"],
                           revision=fresh["analysis_revision"], generation=generation, events=len(disk))
            async with connect(sid, analysis_revision=old["analysis_revision"], last_seq=old["last_seq"]) as ws:
                greeting, rows = await replay(ws, "ws-generation-reconnect", old["last_seq"])
                require(greeting["reset"] and greeting["generation"] == generation, "Stale cursor was not reset")
                require([event["event_id"] for event in rows] == [event["event_id"] for event in disk],
                        "New-generation reconnect differs from durable rows")
        with report.stage("external_delete_fails_closed") as row:
            response = await client.delete(f"/api/sessions/{sid}")
            require(response.status_code == 409, "External deletion did not refuse without writer acknowledgement")
            require((await request("GET", f"/api/sessions/{sid}"))["session_id"] == sid, "Refused deletion lost data")
            row["http_status"] = response.status_code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--redis-url", default=os.environ.get("BAI_VALIDATION_REDIS_URL"))
    parser.add_argument("--confirm-private-redis", action="store_true")
    parser.add_argument("--allow-default-port", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--video", type=Path)
    parser.add_argument("--stage-timeout", type=float, default=180)
    parser.add_argument("--overall-timeout", type=float, default=900)
    parser.add_argument("--_probe", choices=("timeouts", "command", "command-send", "subscriber", "publish", "score"),
                        help=argparse.SUPPRESS)
    parser.add_argument("--_probe-output", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    require(sys.platform == "linux", "Run only in the configured Linux GPU-server environment")
    if args._probe:
        require(args._probe_output is not None, "Helper output path is required")
        _child_probe(args._probe, args._probe_output)
        return 0
    require(bool(args.redis_url), "--redis-url or BAI_VALIDATION_REDIS_URL is required")
    endpoint = validate_redis_url(args.redis_url, confirmed_private=args.confirm_private_redis,
                                  allow_default_port=args.allow_default_port)
    require(args.output_dir is not None, "--output-dir is required")
    require(args.video is not None and args.video.is_file(), "--video must identify a short existing local clip")
    require(0 < args.video.stat().st_size <= 256 * 1024**2, "Use a nonempty clip no larger than 256 MiB")
    require(10 <= args.stage_timeout <= 600 and 30 <= args.overall_timeout <= 3600, "Invalid bounded timeout")
    output = fresh_output(args.output_dir)
    report = Report(output, endpoint, args.overall_timeout, args.redis_url)
    report.body["input"] = {"path": str(args.video.resolve()), "bytes": args.video.stat().st_size}
    report.body["runtime"] = {"python": sys.version, "executable": sys.executable, "packages": {}}
    for package in ("redis", "fastapi", "uvicorn", "websockets", "httpx", "msgpack", "av"):
        try:
            report.body["runtime"]["packages"][package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            report.body["runtime"]["packages"][package] = None
    sources = ["research/validate_redis_runtime.py", "engine/src/bai_engine/bus.py",
               "engine/src/bai_engine/runtime/runner.py", "engine/src/bai_engine/store/sessions.py",
               "engine/src/bai_engine/store/events.py", "apps/api/src/bai_api/cli.py", "apps/api/src/bai_api/ws.py",
               "apps/api/src/bai_api/app.py", "apps/api/src/bai_api/routes/sessions.py",
               "apps/web/e2e/score_fixture.py"]
    report.body["source_sha256"] = {
        source: hashlib.sha256((REPO / source).read_bytes()).hexdigest() for source in sources
    }
    for name in ("profiles", "models", "workdir"):
        (output / name).mkdir()
    (output / "profiles" / f"{PROFILE}.yaml").write_text(PROFILE_YAML, encoding="utf-8")
    (output / "models" / "manifest.yaml").write_text("models: {}\n", encoding="utf-8")
    children = Processes(report, environment(output, args.redis_url, args.allow_default_port, report.body["run_id"]),
                         output / "workdir")

    def interrupted(signum: int, _frame: Any) -> None:
        raise KeyboardInterrupt(f"Validation interrupted by signal {signum}")

    previous_signals = {number: signal.signal(number, interrupted) for number in (signal.SIGINT, signal.SIGTERM)}
    try:
        transport(report, children, args.redis_url)
        asyncio.run(asyncio.wait_for(application(report, children, args.video.resolve(), args.stage_timeout),
                                     timeout=report.remaining(args.overall_timeout)))
        report.body["status"] = "passed"
    except BaseException as exc:
        # Do not persist credentials if a dependency includes the URL in its exception.
        detail = report.redact("".join(traceback.format_exception(exc)))
        report.body.update(status="failed", error_type=type(exc).__name__, traceback=detail)
    finally:
        children.close()
        if any(row.get("forced") for row in report.body["cleanup"]):
            report.body["status"] = "failed"
            report.body["cleanup_error"] = "At least one owned process required SIGKILL"
        report.body["finished_at"] = datetime.now(UTC).isoformat()
        report.save()
        for number, handler in previous_signals.items():
            signal.signal(number, handler)
    print(json.dumps({"status": report.body["status"], "report": str(output / "report.json")}))
    return 0 if report.body["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
