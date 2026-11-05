"""Actual isolated HTTP/Firefox product smoke; no neural accuracy claim.

The retained 67-frame synthetic-pattern MP4 is real decoded video. A separate
FastAPI/EngineService/LocalBus process owns a new data tree and serves the
existing isolated frontend build. All model providers are explicitly disabled.
Only FFmpeg's encoder capability enumeration is restricted to CPU encoders;
every actual media operation executes the installed FFmpeg unchanged.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import csv
import hashlib
import importlib
import io
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts/benchmarking/experiments"
DEFAULT_BUILD = ARTIFACTS / "prod_20261105_frontend_release_v2/build"
DEFAULT_FIXTURE = ARTIFACTS / "prod_20261105_external_binding_regression_v1/actual_weightless_fixture.mp4"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def cpu_ffmpeg(output: Path) -> Path:
    """Expose actual CPU encoders without attempting a CUDA capability probe."""
    executable = shutil.which("ffmpeg")
    if not executable:
        raise RuntimeError("Existing FFmpeg is required")
    wrapper = output / "ffmpeg_cpu"
    # This is an explicit test-tool boundary, never installed into the application.
    wrapper.write_text(
        f"#!{sys.executable}\n"
        "import json,os,subprocess,sys,time\n"
        f"real={executable!r}\nlog={str(output / 'ffmpeg_commands.jsonl')!r}\n"
        "with open(log,'a') as f: f.write(json.dumps({'time':time.time(),'argv':sys.argv[1:]})+'\\n')\n"
        "if '-encoders' in sys.argv:\n"
        " p=subprocess.run([real,*sys.argv[1:]],capture_output=True,check=False)\n"
        " sys.stdout.buffer.write(b'\\n'.join(x for x in p.stdout.splitlines() if b'_nvenc' not in x)+b'\\n')\n"
        " sys.stderr.buffer.write(p.stderr);sys.exit(p.returncode)\n"
        "if any('_nvenc' in x for x in sys.argv[1:]):\n"
        " sys.stderr.write('GPU encoders disabled by isolated diagnostic harness\\n');sys.exit(64)\n"
        "os.execv(real,[real,*sys.argv[1:]])\n"
    )
    wrapper.chmod(0o700)
    return wrapper


def prepare(output: Path, build: Path, fixture: Path) -> dict:
    if not (build / "index.html").is_file() or not (build / "assets").is_dir():
        raise ValueError("An existing isolated frontend build is required")
    if build.resolve() == (ROOT / "apps/web/dist").resolve():
        raise ValueError("The deployment build is excluded")
    if not fixture.is_file():
        raise ValueError("Retained real video fixture is missing")
    output.mkdir(parents=True, exist_ok=False)
    for name in ["profiles", "models", "downloads", "browser_profiles", "evidence", "executed_source"]:
        (output / name).mkdir()
    (output / "models/manifest.yaml").write_text("models: {}\n")
    (output / "profiles/diagnostic.yaml").write_text(
        "description: Product plumbing only; every neural provider disabled\n"
        "device: cpu\nanalysis_height: 180\nchunk_frames: 64\nlead_buffer_s: 0.0\n"
        "shuttle: {model: none, backend: none}\n"
        "player_detector: {model: none, backend: none}\n"
        "pose: {model: none, backend: none}\n"
        "stroke: {model: none, backend: none}\n"
    )
    (output / "invalid.mp4").write_bytes(b"This is deliberately not a media container.\n")
    (output / "empty.mp4").write_bytes(b"")
    wrapper = cpu_ffmpeg(output)
    source_files = [Path(__file__)]
    for directory in ["engine/src", "sports/badminton/src", "agents/src", "apps/api/src", "apps/web/src"]:
        source_files += sorted(p for p in (ROOT / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    sources = {str(p.relative_to(ROOT)): digest(p) for p in source_files}
    (output / "executed_source/production_product_smoke.py").write_bytes(Path(__file__).read_bytes())
    config = {
        "mode": "actual_product_http_browser_all_neural_models_disabled",
        "accuracy_claim": False,
        "app_port": port(),
        "driver_port": port(),
        "output": str(output.resolve()),
        "build": str(build.resolve()),
        "fixture": str(fixture.resolve()),
        "fixture_sha256": digest(fixture),
        "frontend_files_sha256": {
            str(p.relative_to(build)): digest(p) for p in sorted(build.rglob("*")) if p.is_file()
        },
        "source_sha256": sources,
        "ffmpeg": str(wrapper.resolve()),
        "ffprobe": shutil.which("ffprobe"),
        "cpu_encoder_adapter": "Only encoder enumeration excludes NVENC; actual FFmpeg commands execute unchanged",
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "main_head": subprocess.check_output(["git", "rev-parse", "main"], cwd=ROOT, text=True).strip(),
        "settings": {
            "data_dir": str(output.resolve() / "data"),
            "models_dir": str(output.resolve() / "models"),
            "profiles_dir": str(output.resolve() / "profiles"),
            "profile": "diagnostic",
            "bind_host": "127.0.0.1",
            "redis_url": None,
            "engine_mode": "embedded",
            "proxy_height": 180,
            "llm_provider": "local",
            "local_llm_url": "http://127.0.0.1:9/v1",
            "passphrase": None,
        },
    }
    dump(output / "configuration.json", config)
    return config


def serve(config_path: Path) -> None:
    """A new runtime process configures the real factory; no production edits."""
    import msgpack
    import uvicorn

    from bai_engine.bus import LocalBus
    from bai_engine.config import Settings

    config = json.loads(config_path.read_text())
    output = Path(config["output"])
    module = importlib.import_module("bai_api.app")
    module.WEB_DIST = Path(config["build"])
    settings = Settings(
        _env_file=None,
        **config["settings"],
        port=config["app_port"],
        ffmpeg=config["ffmpeg"],
        ffprobe=config["ffprobe"],
    )
    actual = module.create_app(settings=settings, bus=LocalBus(), start_engine=config.get("start_engine", True))

    class Capture:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            if scope["type"] not in {"http", "websocket"}:
                return await self.app(scope, receive, send)
            started = time.time()
            row = {
                "started": started,
                "kind": scope["type"],
                "method": scope.get("method"),
                "path": scope.get("path"),
                "query": scope.get("query_string", b"").decode(),
                "peer": scope.get("client"),
                "status": None,
            }
            body, messages = bytearray(), []

            async def observe(message):
                if message["type"] == "http.response.start":
                    row["status"] = message["status"]
                if message["type"] == "http.response.body" and len(body) < 65536:
                    body.extend(message.get("body", b"")[: 65536 - len(body)])
                if message["type"] == "websocket.send" and len(messages) < 300:
                    text = message.get("text", "")
                    binary = message.get("bytes")
                    if text or binary:
                        try:
                            parsed = json.loads(text) if text else msgpack.unpackb(binary, raw=False)
                            messages.append(
                                {
                                    k: parsed[k]
                                    for k in ["type", "status", "frontier_frame", "seq", "detail"]
                                    if k in parsed
                                }
                            )
                        except (ValueError, TypeError):
                            messages.append({"unparsed_chars": len(text)})
                await send(message)

            try:
                await self.app(scope, receive, observe)
            finally:
                row["elapsed_s"] = time.time() - started
                path = row["path"] or ""
                if path == "/api/sessions" or (path.startswith("/api/sessions/") and path.count("/") == 3):
                    with contextlib.suppress(ValueError):
                        row["session_response"] = json.loads(body)
                if messages:
                    row["messages"] = messages
                with (output / "requests.jsonl").open("a") as stream:
                    stream.write(json.dumps(row) + "\n")

    uvicorn.run(Capture(actual), host="127.0.0.1", port=config["app_port"], access_log=True)


def http(
    base: str, path: str, *, method: str = "GET", body: bytes | None = None, content_type: str | None = None
) -> dict:
    headers = {} if content_type is None else {"Content-Type": content_type}
    parsed = urllib.parse.urlparse(base + path)
    if parsed.scheme != "http" or parsed.hostname != "127.0.0.1":
        raise ValueError("The diagnostic HTTP client accepts only owned loopback HTTP")
    req = urllib.request.Request(base + path, data=body, method=method, headers=headers)  # noqa: S310 - checked loopback
    try:
        response = urllib.request.urlopen(req, timeout=40)  # noqa: S310 - owned loopback only
    except urllib.error.HTTPError as error:
        response = error
    with response:
        payload = response.read()
        return {"status": response.code, "headers": dict(response.headers), "body": payload}


def multipart(path: Path) -> tuple[bytes, str]:
    boundary = "OwnDiagnosticUploadBoundary"
    payload = (
        (
            f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
            "Content-Type: video/mp4\r\n\r\n"
        ).encode()
        + path.read_bytes()
        + f"\r\n--{boundary}--\r\n".encode()
    )
    return payload, f"multipart/form-data; boundary={boundary}"


def export_summary(contents: dict[str, bytes]) -> dict:
    rallies = list(csv.reader(io.StringIO(contents["rallies.csv"].decode())))
    legacy = list(csv.reader(io.StringIO(contents["legacy.csv"].decode())))
    events = [json.loads(line) for line in contents["events.jsonl"].decode().splitlines() if line]
    return {
        "rallies_columns": rallies[0] if rallies else [],
        "rally_rows": max(0, len(rallies) - 1),
        "legacy_columns": legacy[0] if legacy else [],
        "legacy_rows": max(0, len(legacy) - 1),
        "events": len(events),
        "event_types": sorted({e.get("type", "") for e in events}),
        "summary": json.loads(contents["summary.json"]),
    }


def validate_result(result: dict, *, expect_fixes: bool = False) -> None:
    """Check measured contracts; documented pre-fix defects remain observable."""
    measured = result["completed"]
    if measured["media"]["n_frames"] != 67 or measured["frontier_frame"] != 66:
        raise AssertionError("The 67-frame input did not reach its exact final frontier")
    if any(person["name"] is not None for person in measured["players"]):
        raise AssertionError("Anonymous input acquired an unprovided athlete name")
    rows = result["browser_seeks"]
    if (
        not isinstance(rows, list)
        or len(rows) != 6
        or any(row["target"] != row["identity"] or row["callback_missing"] for row in rows)
    ):
        raise AssertionError("Actual browser pixels failed a frame identity seek")
    if result["unknown_session"] != {"session_status": 404, "export_status": 404}:
        raise AssertionError("An unknown session acquired results or exports")
    if result["same_source_reuse"] != {"status": 200, "session_id": result["completed_session_id"], "same_id": True}:
        raise AssertionError("Content-addressed same-source reuse changed ownership")
    if result["exports"]["rally_rows"] or result["exports"]["legacy_rows"]:
        raise AssertionError("The model-disabled fixture fabricated a counted rally")
    if expect_fixes:
        if len(result["exports"]["rallies_columns"]) != 17:
            raise AssertionError("Empty application CSV lost its populated schema")
        if "Detailed diagnostics are retained on the server" not in result["failed"]["status_detail"]:
            raise AssertionError("Failure detail is not projected for the public response")


def stage_completed_run(run_path: Path, config: dict) -> dict:
    """Physically copy a closed completed run; never open an original database."""
    from bai_api.routes.exports import _rally_rows
    from bai_engine.schema import Session
    from bai_engine.store import SessionRepository

    report_path, session_path = run_path / "inference.json", run_path / "session.json"
    report = json.loads(report_path.read_text())
    session = Session.model_validate_json(session_path.read_text())
    if report["status"] != "completed" or session.status != "analysed":
        raise ValueError("Only a durably completed neural run can be copied for product replay")
    if report["frames_processed"] != session.media.n_frames or session.frontier_frame != session.media.n_frames - 1:
        raise ValueError("Completed run does not cover its exact canonical frame extent")
    source_session = run_path / "data/sessions" / session.session_id
    database = source_session / "events.sqlite"
    sidecars = [Path(str(database) + suffix) for suffix in ["-wal", "-shm"]]
    if any(path.exists() for path in sidecars):
        raise ValueError("Original SQLite sidecars are present; byte-copy snapshot would not be safe")
    original_media = run_path / "data/media" / session.source.sha256
    if "#EXT-X-ENDLIST" not in (original_media / "hls/index.m3u8").read_text():
        raise ValueError("Only finalized immutable playback assets can be copied")
    output = Path(config["output"])
    data = output / "data"
    consumed = {str(path): digest(path) for path in [report_path, session_path, database]}
    copies = []

    def copy(source: Path, destination: Path) -> None:
        expected = digest(source)
        consumed[str(source)] = expected
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        if source.samefile(destination) or digest(destination) != expected:
            raise ValueError("A product replay asset was not an independent exact byte copy")
        copies.append({"source": str(source), "destination": str(destination), "sha256": expected})

    copy(database, data / "sessions" / session.session_id / "events.sqlite")
    for path in sorted((source_session / "tracks").rglob("*.parquet")):
        copy(path, data / "sessions" / session.session_id / path.relative_to(source_session))
    for path in sorted(original_media.rglob("*")):
        if path.is_file() and (
            "hls" in path.relative_to(original_media).parts
            or path.name == "proxy.mp4"
            or path.name.startswith("sprite")
        ):
            copy(path, data / "media" / session.source.sha256 / path.relative_to(original_media))
    repository = SessionRepository(data)
    try:
        saved = repository.save(session)
        events = repository.events(saved.session_id).all_live()
        rows = _rally_rows(saved, repository)
        expected = {
            "session_id": saved.session_id,
            "source_sha256": saved.source.sha256,
            "media": saved.media.model_dump(mode="json"),
            "live_event_counts": dict(Counter(e.type for e in events)),
            "live_event_ids": [e.event_id for e in events],
            "official_rally_rows": rows,
            "producer_event_counts": report["event_counts"],
        }
    finally:
        repository.close()
    if any(path.exists() for path in sidecars) or any(digest(Path(path)) != value for path, value in consumed.items()):
        raise ValueError("An original completed result changed during its independent copy")
    record = {
        "mode": "read_only_product_rendering_of_completed_neural_results_no_new_inference",
        "source_run": str(run_path.resolve()),
        "original_sqlite_connection_opened": False,
        "original_file_access": "read-only byte hashing/copying; no original SQLite connection or sidecar handling",
        "start_engine": False,
        "copies_are_independent_inodes": True,
        "metadata_transform": "Session values retained; new isolated catalogue save refreshes only updated_at",
        "consumed_files_sha256": consumed,
        "physical_copies": copies,
        "expected": expected,
    }
    dump(output / "completed_run_import.json", record)
    config.update({"mode": record["mode"], "start_engine": False, "completed_source_run": str(run_path.resolve())})
    dump(output / "configuration.json", config)
    return record


def check_completed_product(seed: dict, output: Path, app_base: str, navigate, js, wait, screenshot) -> dict:
    """Exercise the same actual browser/routes against copied neural outputs."""
    expected = seed["expected"]
    sid = expected["session_id"]
    strokes = expected["live_event_counts"].get("stroke", 0)

    def event_backlog_ready():
        return js(
            "const n=arguments[0],t=document.body.innerText;"
            "return n===0||t.includes('of '+n+' shot events classified')"
            "||t.includes(n+' shot events · classification unavailable');",
            [strokes],
        )

    navigate(f"/sessions/{sid}")
    wait(lambda: js("return document.body.innerText.includes('Analysed') && !!document.querySelector('video');"))
    wait(lambda: js("return document.querySelector('video').readyState>=2;"))
    wait(event_backlog_ready)
    screenshot("neural_01_completed_results")
    public = json.loads(http(app_base, f"/api/sessions/{sid}")["body"])
    if public["source"]["uri"] or public["source"]["sha256"] != expected["source_sha256"]:
        raise AssertionError("Copied neural results lost their original source binding or public URI projection")
    js("[...document.querySelectorAll('button')].find(x=>x.textContent.trim()==='Export').click();")
    wait(lambda: js("return !!document.querySelector('a[href$=\"/exports/rallies.csv\"]');"))
    screenshot("neural_02_exports")
    contents = {}
    for kind in ["rallies.csv", "legacy.csv", "events.jsonl", "summary.json"]:
        js("document.querySelector(arguments[0]).click();", [f'a[href$="/exports/{kind}"]'])
        response = http(app_base, f"/api/sessions/{sid}/exports/{kind}")
        if response["status"] != 200:
            raise AssertionError(f"Copied neural results export failed: {kind}")
        (output / "evidence" / kind).write_bytes(response["body"])
        contents[kind] = response["body"]
    desired_hashes = {hashlib.sha256(value).hexdigest() for value in contents.values()}
    wait(
        lambda: desired_hashes.issubset({digest(p) for p in (output / "downloads").iterdir() if p.is_file()}),
        seconds=20,
    )
    events = [json.loads(line) for line in contents["events.jsonl"].splitlines()]
    observed_counts = dict(Counter(event["type"] for event in events))
    if (
        observed_counts != expected["live_event_counts"]
        or [e["event_id"] for e in events] != expected["live_event_ids"]
    ):
        raise AssertionError("The actual public event export differs from the copied durable live fold")
    rows = list(csv.DictReader(io.StringIO(contents["rallies.csv"].decode())))
    if len(rows) != len(expected["official_rally_rows"]):
        raise AssertionError("Application CSV does not preserve the durable official rally projection")
    for observed, durable in zip(rows, expected["official_rally_rows"], strict=True):
        if any(int(observed[key]) != durable[key] for key in ["frame_start", "frame_end"]):
            raise AssertionError("Application CSV changed a copied neural rally boundary")
    dump(output / "evidence/public_neural_session.json", public)
    contact = next((event for event in events if event["type"] == "contact"), None)
    if contact:
        navigate(f"/sessions/{sid}?tab=shots&f={contact['frame_start']}")
        wait(lambda: js("return document.body.innerText.includes('Analysed');"))
        wait(event_backlog_ready)
        wait(lambda: js("return document.querySelector('video')?.readyState>=2;"))
        wait(lambda: js("return !document.body.innerText.includes('Loading recorded analysis');"))
        screenshot("neural_03_shots")
    return {
        "mode": seed["mode"],
        "start_engine": False,
        "new_inference": False,
        "session_id": sid,
        "source_sha256": public["source"]["sha256"],
        "source_uri_redacted": True,
        "durable_live_event_counts": observed_counts,
        "producer_event_counts": expected["producer_event_counts"],
        "producer_count_parity": observed_counts == expected["producer_event_counts"],
        "exported_official_rallies": len(rows),
        "all_official_boundaries_exact": True,
        "downloads": [{"name": p.name, "sha256": digest(p)} for p in (output / "downloads").iterdir() if p.is_file()],
    }


def run(
    output: Path, build: Path, fixture: Path, *, expect_fixes: bool = False, completed_run: Path | None = None
) -> dict:
    config = prepare(output, build, fixture)
    seed = stage_completed_run(completed_run, config) if completed_run is not None else None
    config_path = output / "configuration.json"
    app_base, driver_base = f"http://127.0.0.1:{config['app_port']}", f"http://127.0.0.1:{config['driver_port']}"
    env = {k: v for k, v in os.environ.items() if not k.startswith("BAI_")}
    env.update({"CUDA_VISIBLE_DEVICES": "", "BAI_LLM_PROVIDER": "local", "BAI_LOCAL_LLM_URL": "http://127.0.0.1:9/v1"})
    commands = {
        "server": [sys.executable, str(Path(__file__).resolve()), "serve", "--configuration", str(config_path)],
        "driver": [
            "geckodriver",
            "--host",
            "127.0.0.1",
            "--port",
            str(config["driver_port"]),
            "--profile-root",
            str(output / "browser_profiles"),
        ],
    }
    dump(
        output / "commands.json",
        {**commands, "environment_overrides": {"CUDA_VISIBLE_DEVICES": "", "BAI_LLM_PROVIDER": "local"}},
    )
    logs, processes, session = [], {}, None
    results = {"status": "running", "mode": config["mode"], "accuracy_claim": False, "steps": []}

    def wd(method, path, value=None):
        response = http(
            driver_base,
            path,
            method=method,
            body=None if value is None else json.dumps(value).encode(),
            content_type="application/json",
        )
        parsed = json.loads(response["body"])
        if response["status"] >= 400:
            raise RuntimeError(str(parsed))
        return parsed["value"]

    def js(script, args=None):
        return wd("POST", f"/session/{session}/execute/sync", {"script": script, "args": args or []})

    def wait(predicate, seconds=90):
        deadline = time.monotonic() + seconds
        last = None
        while time.monotonic() < deadline:
            try:
                last = predicate()
                if last:
                    return last
            except (urllib.error.URLError, TimeoutError, RuntimeError):
                pass
            time.sleep(0.2)
        raise TimeoutError(f"Owned product smoke wait expired; last={last!r}")

    def screenshot(name):
        (output / "evidence" / f"{name}.png").write_bytes(base64.b64decode(wd("GET", f"/session/{session}/screenshot")))
        dump(
            output / "evidence" / f"{name}.json",
            js(
                "return {url:location.href,title:document.title,text:document.body.innerText,"
                "videos:[...document.querySelectorAll('video')].map(v=>({time:v.currentTime,duration:v.duration,"
                "readyState:v.readyState,error:v.error?.message,width:v.videoWidth,height:v.videoHeight}))};"
            ),
        )

    def navigate(path):
        wd("POST", f"/session/{session}/url", {"url": app_base + path})

    try:
        for key, command in commands.items():
            stream = (output / f"{key}.log").open("wb")
            logs.append(stream)
            processes[key] = subprocess.Popen(
                command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True
            )
        dump(output / "processes.json", {k: {"pid": p.pid, "command": commands[k]} for k, p in processes.items()})
        wait(lambda: http(app_base, "/api/health")["status"] == 200)
        wait(lambda: wd("GET", "/status").get("ready"))
        created = wd(
            "POST",
            "/session",
            {
                "capabilities": {
                    "alwaysMatch": {
                        "browserName": "firefox",
                        "moz:firefoxOptions": {
                            "binary": "/snap/firefox/current/usr/lib/firefox/firefox",
                            "args": ["-headless"],
                            "prefs": {
                                "browser.startup.page": 0,
                                "toolkit.telemetry.enabled": False,
                                "browser.download.folderList": 2,
                                "browser.download.dir": str((output / "downloads").resolve()),
                                "browser.helperApps.neverAsk.saveToDisk": (
                                    "text/csv,application/x-ndjson,application/json,application/pdf"
                                ),
                                "pdfjs.disabled": True,
                            },
                        },
                    }
                }
            },
        )
        session = created["sessionId"]
        dump(output / "browser_capabilities.json", created["capabilities"])
        wd("POST", f"/session/{session}/window/rect", {"width": 1440, "height": 1000})
        if seed is not None:
            results["completed_neural_product"] = check_completed_product(
                seed, output, app_base, navigate, js, wait, screenshot
            )
            results["status"] = "completed"
            return results
        navigate("/library")
        wait(lambda: js("return !!document.querySelector('input[type=file]');"))
        screenshot("01_upload_empty")
        element = wd("POST", f"/session/{session}/element", {"using": "css selector", "value": "input[type=file]"})
        key = element["element-6066-11e4-a52e-4f735466cecf"]
        wd("POST", f"/session/{session}/element/{key}/value", {"text": str(fixture.resolve())})
        screenshot("02_upload_selected")
        js("document.querySelector('form[aria-labelledby=upload-video-heading] button[type=submit]').click();")
        timeline = []
        recording_id = None
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            response = http(app_base, "/api/sessions")
            records = json.loads(response["body"])
            if records:
                current = records[0]
                recording_id = current["session_id"]
                point = {
                    "time": time.time(),
                    "session_id": recording_id,
                    "status": current["status"],
                    "frontier_frame": current.get("frontier_frame"),
                    "media": current.get("media"),
                }
                if not timeline or (point["status"], point["frontier_frame"]) != (
                    timeline[-1]["status"],
                    timeline[-1]["frontier_frame"],
                ):
                    timeline.append(point)
                    dump(output / "status_timeline.json", timeline)
                    if len(timeline) == 1:
                        screenshot("03_processing")
                if current["status"] in {"analysed", "failed"}:
                    break
            time.sleep(0.1)
        if not recording_id or current["status"] != "analysed":
            raise RuntimeError(f"Actual upload did not finish: {records!r}")
        response = http(app_base, f"/api/sessions/{recording_id}")
        completed = json.loads(response["body"])
        dump(output / "completed_session.json", completed)
        results["completed_session_id"] = recording_id
        results["public_source"] = {
            "uri_redacted": completed["source"]["uri"] == "",
            "input_sha256_matches": completed["source"]["sha256"] == config["fixture_sha256"],
        }
        results["status_timeline"] = timeline
        results["completed"] = {
            "status": completed["status"],
            "frontier_frame": completed["frontier_frame"],
            "media": completed.get("media"),
            "players": completed.get("players"),
            "roster": completed.get("roster"),
        }
        wait(
            lambda: js(
                "return location.pathname.includes(arguments[0]) && document.body.innerText.includes('Analysed');",
                [recording_id],
            ),
            seconds=15,
        )
        screenshot("04_completed_empty_analytics")
        # Seek the real mounted player, then independently decode its barcode.
        # The expected frame number is not used to select or alter pixels.
        wd("POST", f"/session/{session}/timeouts", {"script": 45000})
        seek_rows = wd(
            "POST",
            f"/session/{session}/execute/async",
            {
                "script": """
            const done=arguments[arguments.length-1];
            const video=document.querySelector('video');
            const run=async()=>{
              const deadline=performance.now()+15000;
              while(video.readyState<2 || !video.buffered.length || video.buffered.end(video.buffered.length-1)<2.2){
                if(performance.now()>deadline) throw Error('Actual player readiness timeout');
                await new Promise(r=>setTimeout(r,20));
              }
              video.pause();
              const canvas=document.createElement('canvas');canvas.width=320;canvas.height=180;
              const context=canvas.getContext('2d',{willReadFrequently:true});
              const rows=[];
              for(const target of [66,0,30,59,60,1]){
                const row=await new Promise(resolve=>{
                  let settled=false,callback;
                  const finish=(meta,missing)=>{
                    if(settled)return;settled=true;clearTimeout(timer);
                    if(callback!=null)video.cancelVideoFrameCallback(callback);
                    context.drawImage(video,0,0,320,180);
                    let identity=0;
                    for(let bit=0;bit<9;bit++){
                      const x=Math.round(320*(.03+.105*bit))+3;
                      const pixels=context.getImageData(x,65,14,50).data;let sum=0;
                      for(let i=0;i<pixels.length;i+=4)sum+=pixels[i]+pixels[i+1]+pixels[i+2];
                      if(sum/(pixels.length/4*3)>127)identity|=1<<bit;
                    }
                    resolve({target,identity,current_time:video.currentTime,media_time:meta?.mediaTime??null,
                      callback_missing:missing,text:document.querySelector('[data-testid=video-stage]')?.innerText,
                      timeline:document.querySelector('[aria-label="Recording timeline"]')?.innerText});
                  };
                  const timer=setTimeout(()=>finish(null,true),3000);
                  const onFrame=(_now,meta)=>{
                    if(video.seeking||Math.abs(meta.mediaTime-video.currentTime)>1.01/30){
                      callback=video.requestVideoFrameCallback(onFrame);return;
                    }
                    setTimeout(()=>finish(meta,false),50);
                  };
                  callback=video.requestVideoFrameCallback(onFrame);
                  video.currentTime=target/30;
                });rows.push(row);
              }
              return rows;
            };run().then(done).catch(e=>done({error:String(e.stack||e)}));
        """,
                "args": [],
            },
        )
        results["browser_seeks"] = seek_rows
        dump(output / "evidence/browser_seeks.json", seek_rows)
        screenshot("04b_player_seek_frame1")
        js("[...document.querySelectorAll('button')].find(x=>x.textContent.trim()==='Export').click();")
        wait(lambda: js("return !!document.querySelector('a[href$=\"/exports/rallies.csv\"]');"))
        screenshot("05_exports")
        exports = {}
        for kind in ["rallies.csv", "legacy.csv", "events.jsonl", "summary.json"]:
            js("document.querySelector(arguments[0]).click();", [f'a[href$="/exports/{kind}"]'])
            response = http(app_base, f"/api/sessions/{recording_id}/exports/{kind}")
            if response["status"] != 200:
                raise RuntimeError(f"Export {kind} failed {response['status']}")
            (output / "evidence" / kind).write_bytes(response["body"])
            exports[kind] = response["body"]
        results["exports"] = export_summary(exports)
        results["download_links_clicked"] = list(exports)
        expected_download_hashes = {hashlib.sha256(payload).hexdigest() for payload in exports.values()}
        wait(
            lambda: expected_download_hashes.issubset(
                {digest(path) for path in (output / "downloads").iterdir() if path.is_file()}
            ),
            seconds=15,
        )
        results["downloaded_files"] = [
            {"name": p.name, "sha256": digest(p), "bytes": p.stat().st_size}
            for p in (output / "downloads").iterdir()
            if p.is_file()
        ]
        for name, path in [
            ("analytics", "analytics"),
            ("individual", "individual-analytics"),
            ("estimated_individual", "estimated-individual-analytics"),
        ]:
            response = http(app_base, f"/api/sessions/{recording_id}/{path}")
            dump(
                output / "evidence" / f"{name}.json",
                {"status": response["status"], "payload": json.loads(response["body"])},
            )
        missing = http(app_base, "/api/sessions/NotOwnedRecording")
        foreign_export = http(app_base, "/api/sessions/NotOwnedRecording/exports/events.jsonl")
        results["unknown_session"] = {"session_status": missing["status"], "export_status": foreign_export["status"]}
        # A real invalid container enters the same browser upload route and real worker.
        navigate("/library")
        wait(lambda: js("return !!document.querySelector('input[type=file]');"))
        element = wd("POST", f"/session/{session}/element", {"using": "css selector", "value": "input[type=file]"})
        key = element["element-6066-11e4-a52e-4f735466cecf"]
        wd("POST", f"/session/{session}/element/{key}/value", {"text": str((output / "invalid.mp4").resolve())})
        js("document.querySelector('form[aria-labelledby=upload-video-heading] button[type=submit]').click();")
        failed = wait(
            lambda: next(
                (
                    x
                    for x in json.loads(http(app_base, "/api/sessions")["body"])
                    if x["source"]["sha256"] != completed["source"]["sha256"] and x["status"] == "failed"
                ),
                None,
            )
        )
        dump(output / "failed_session.json", failed)
        results["failed_session_id"] = failed["session_id"]
        results["failed"] = {
            "status": failed["status"],
            "status_detail": failed.get("status_detail"),
            "media": failed.get("media"),
        }
        wait(
            lambda: js("return document.body.innerText.includes('This analysis stopped before completion');"),
            seconds=15,
        )
        results["failed_video_pane"] = js("return document.querySelector('[data-testid=video-stage]')?.innerText;")
        screenshot("06_failed_container")
        js("[...document.querySelectorAll('button')].find(x=>x.textContent.trim()==='Export').click();")
        screenshot("07_failed_exports")
        js(
            "[...document.querySelectorAll('p')].find(x=>x.textContent.includes('analysis proxy frames processed')"
            "||x.textContent.includes('Analysis coverage unavailable'))?.scrollIntoView({block:'center'});"
        )
        screenshot("08_failed_coverage")
        response = http(app_base, f"/api/sessions/{failed['session_id']}/exports/rallies.csv")
        (output / "evidence/failed_rallies.csv").write_bytes(response["body"])
        results["failed_export"] = {"status": response["status"], "body": response["body"].decode()}
        payload, content_type = multipart(output / "empty.mp4")
        response = http(app_base, "/api/sessions", method="POST", body=payload, content_type=content_type)
        results["empty_upload"] = {"status": response["status"], "payload": json.loads(response["body"])}
        if response["status"] == 201:
            empty_id = results["empty_upload"]["payload"]["session_id"]
            empty_failed = wait(
                lambda: (lambda value: value if value["status"] == "failed" else None)(
                    json.loads(http(app_base, f"/api/sessions/{empty_id}")["body"])
                )
            )
            dump(output / "empty_failed_session.json", empty_failed)
            results["empty_upload"]["final_status"] = empty_failed["status"]
        # Reupload exercises real content-addressed reuse without rerunning inference.
        payload, content_type = multipart(fixture)
        reused = http(app_base, "/api/sessions", method="POST", body=payload, content_type=content_type)
        reuse_payload = json.loads(reused["body"])
        results["same_source_reuse"] = {
            "status": reused["status"],
            "session_id": reuse_payload.get("session_id"),
            "same_id": reuse_payload.get("session_id") == recording_id,
        }
        validate_result(results, expect_fixes=expect_fixes)
        if expect_fixes:
            failed_screen = json.loads((output / "evidence/07_failed_exports.json").read_text())["text"]
            if (
                "Analysis coverage unavailable" not in failed_screen
                or "100% of analysis proxy frames processed" in failed_screen
            ):
                raise AssertionError("Failed recording displays fabricated complete coverage")
            if "Analysis stopped before completion — exports contain partial results." not in failed_screen:
                raise AssertionError("Failed export panel does not disclose partial results")
            if "Analysis is still running" in failed_screen or "/data/media/" in failed_screen:
                raise AssertionError("Failed page still displays stale running copy or private source path")
            pane = results["failed_video_pane"] or ""
            if "Video unavailable" not in pane or "Loading video" in pane or "Preparing the video" in pane:
                raise AssertionError("Failed undecodable video still claims that playback is loading")
        results["expected_fixes_checked"] = expect_fixes
        results["status"] = "completed"
    except Exception as error:
        results["status"] = "failed"
        results["error"] = f"{type(error).__name__}: {error}"
        if session:
            with contextlib.suppress(Exception):
                screenshot("failure")
        raise
    finally:
        if session:
            with contextlib.suppress(Exception):
                wd("DELETE", f"/session/{session}")
        for process in reversed(list(processes.values())):
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=5)
        for stream in logs:
            stream.close()
        results["process_cleanup"] = {
            name: {"pid": p.pid, "exit_code": p.returncode, "reaped": p.poll() is not None}
            for name, p in processes.items()
        }
        if results.get("failed_session_id"):
            from bai_engine.store import SessionRepository

            repository = SessionRepository(output / "data")
            try:
                private = repository.get(results["failed_session_id"])
                results["private_failure_diagnostics"] = {
                    "source_uri_retained": private.source.uri.startswith(str(output / "data")),
                    "full_detail_retained": str(output / "data") in (private.status_detail or ""),
                    "detail_sha256": hashlib.sha256((private.status_detail or "").encode()).hexdigest(),
                }
            finally:
                repository.close()
        results["source_guard"] = {
            "changed": [name for name, value in config["source_sha256"].items() if digest(ROOT / name) != value]
        }
        results["input_guard"] = digest(fixture) == config["fixture_sha256"]
        if seed is not None:
            results["completed_run_input_guard"] = {
                "changed": [
                    name for name, value in seed["consumed_files_sha256"].items() if digest(Path(name)) != value
                ]
            }
        results["frontend_guard"] = {
            "changed": [
                name for name, value in config["frontend_files_sha256"].items() if digest(build / name) != value
            ]
        }
        dump(output / "results.json", results)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    run_parser = sub.add_parser("run")
    run_parser.add_argument("--output", type=Path, required=True)
    run_parser.add_argument("--build", type=Path, default=DEFAULT_BUILD)
    run_parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    run_parser.add_argument("--expect-fixes", action="store_true")
    run_parser.add_argument("--completed-run", type=Path)
    server_parser = sub.add_parser("serve")
    server_parser.add_argument("--configuration", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "serve":
        serve(args.configuration)
    else:
        print(
            json.dumps(
                run(
                    args.output.resolve(),
                    args.build.resolve(),
                    args.fixture.resolve(),
                    expect_fixes=args.expect_fixes,
                    completed_run=None if args.completed_run is None else args.completed_run.resolve(),
                ),
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
