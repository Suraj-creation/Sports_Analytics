"""Real isolated Firefox + actual VideoStage/useHls/frameClock on tiny fixtures.

Uses the already installed geckodriver through standard WebDriver HTTP. No
browser/dependency installation, existing service, match media or GPU is used.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


ENTRY = (ROOT / "research/production_browser_media_entry.tsx").read_text()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def run(fixtures: Path, output: Path, growing: bool = False):
    output.mkdir(parents=True, exist_ok=False)
    (output / "profiles").mkdir()
    tracked = [Path(__file__), ROOT / "research/production_browser_media_entry.tsx"]
    tracked += [
        ROOT / "apps/web/src" / name
        for name in [
            "features/player/VideoStage.tsx",
            "features/player/useHls.ts",
            "lib/frameClock.ts",
            "stores/playback.ts",
            "stores/session.ts",
        ]
    ]
    sources = {}
    for path in tracked:
        relative = path.relative_to(ROOT)
        snapshot = output / "executed_source" / relative
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(path.read_bytes())
        sources[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    dump(output / "source_provenance.json", sources)
    app = ROOT / "apps/web"
    inputs = json.loads((fixtures / "results.json").read_text())
    cases = {}
    for case in inputs["cases"]:
        numerator, _, denominator = str(case["plan"]["fps"]).partition("/")
        cases[case["case"]] = {
            "fps_num": int(numerator),
            "fps_den": int(denominator or 1),
            "fps": int(numerator) / int(denominator or 1),
            "segment_frames": case["plan"]["frames_per_segment"],
            "has_audio": case["plan"]["audio"],
            "identities": [row["identity"] for row in case["proxy_frames"]],
        }
    dump(output / "cases.json", cases)
    harness = output / "harness"
    harness.mkdir()
    (harness / "entry.tsx").write_text(ENTRY)
    (harness / "index.html").write_text(
        "<!doctype html><style>video{width:320px;height:180px}canvas{display:none}</style>"
        '<div id="root"></div><script type="module" src="/entry.tsx"></script>'
    )
    config = output / "build.mjs"
    config.write_text(
        f"import {{build}} from {json.dumps((app / 'node_modules/vite/dist/node/index.js').as_uri())};\n"
        f"import react from {json.dumps((app / 'node_modules/@vitejs/plugin-react/dist/index.js').as_uri())};\n"
        f"await build({{configFile:false,root:{json.dumps(str(harness))},plugins:[react()],resolve:{{alias:"
        f"{{'@':{json.dumps(str(app / 'src'))},react:{json.dumps(str(app / 'node_modules/react'))},"
        f"'react-dom':{json.dumps(str(app / 'node_modules/react-dom'))}}}}},build:"
        f"{{outDir:{json.dumps(str(output / 'browser_build'))},sourcemap:true,emptyOutDir:false}}}});\n"
    )
    with (output / "build.log").open("wb") as log:
        subprocess.run(["node", str(config)], check=True, stdout=log, stderr=subprocess.STDOUT)

    manifest_started = {}
    manifest_requests = []

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            route = urllib.parse.urlparse(self.path).path.strip("/").split("/")
            if (
                growing
                and len(route) == 5
                and route[:2] == ["api", "sessions"]
                and route[2] in cases
                and route[3:] == ["hls", "index.m3u8"]
            ):
                name = route[2]
                elapsed = time.monotonic() - manifest_started.setdefault(name, time.monotonic())
                stage = "first_segment_event" if elapsed < 1 else "full_event" if elapsed < 2 else "ended"
                lines = (fixtures / name / "media/hls/index.m3u8").read_text().splitlines()
                selected = []
                for line in lines:
                    if line == "#EXT-X-ENDLIST" and stage != "ended":
                        continue
                    selected.append(line)
                    if stage == "first_segment_event" and line.endswith(".m4s"):
                        break
                payload = ("\n".join(selected) + "\n").encode()
                manifest_requests.append({"case": name, "elapsed": elapsed, "stage": stage})
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.apple.mpegurl")
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(payload)
                return
            super().do_GET()

        def log_message(self, *args):
            pass

        def translate_path(self, path):
            route = urllib.parse.urlparse(path).path
            if route == "/cases.json":
                return str(output / "cases.json")
            parts = route.strip("/").split("/")
            if len(parts) == 5 and parts[:2] == ["api", "sessions"] and parts[2] in cases and parts[3] == "hls":
                return str(fixtures / parts[2] / "media/hls" / parts[-1])
            if len(parts) == 3 and parts[0] == "fixture" and parts[1] in cases:
                return str(fixtures / parts[1] / "media/proxy.mp4")
            return super().translate_path(path)

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(output / "browser_build")))
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    log = (output / "geckodriver.log").open("wb")
    driver = subprocess.Popen(
        ["geckodriver", "--host", "127.0.0.1", "--port", str(port), "--profile-root", str(output / "profiles")],
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    session, results = None, []

    def request(method, path, value=None):
        req = urllib.request.Request(  # noqa: S310 - own loopback WebDriver
            base + path,
            method=method,
            headers={"Content-Type": "application/json"},
            data=None if value is None else json.dumps(value).encode(),
        )
        try:
            with urllib.request.urlopen(req, timeout=55) as response:  # noqa: S310 - own loopback WebDriver
                return json.load(response)["value"]
        except urllib.error.HTTPError as error:
            raise RuntimeError(error.read().decode()) from error

    try:
        for _ in range(50):
            try:
                request("GET", "/status")
                break
            except urllib.error.URLError:
                time.sleep(0.1)
        info = request(
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
                                "browser.startup.homepage": "about:blank",
                                "toolkit.telemetry.enabled": False,
                            },
                        },
                    }
                }
            },
        )
        session = info["sessionId"]
        dump(output / "capabilities.json", info["capabilities"])
        request("POST", f"/session/{session}/timeouts", {"script": 45000, "pageLoad": 30000})
        for name, case in cases.items():
            count, boundary = len(case["identities"]), case["segment_frames"]
            targets = list(dict.fromkeys([count - 1, 0, 1, boundary - 1, boundary, min(count - 2, boundary + 1)]))
            targets = [frame for frame in targets if 0 <= frame < count]
            for transport in ["mp4", "hls"]:
                url = f"http://127.0.0.1:{server.server_port}/?case={name}&transport={transport}"
                request("POST", f"/session/{session}/url", {"url": url})
                result = request(
                    "POST",
                    f"/session/{session}/execute/async",
                    {
                        "script": (
                            "const done=arguments[arguments.length-1];"
                            "window.ready.then(()=>window.auditRun(arguments[0])).then(done)"
                            ".catch(e=>done({error:String(e.stack||e),setupError:window.setupError}));"
                        ),
                        "args": [targets],
                    },
                )
                results.append(result)
                dump(output / "results_partial.json", results)
                print(json.dumps({"case": name, "transport": transport, "result": result}), flush=True)
    finally:
        if session:
            with contextlib.suppress(Exception):
                request("DELETE", f"/session/{session}")
        driver.terminate()
        try:
            driver.wait(timeout=5)
        except subprocess.TimeoutExpired:
            driver.kill()
            driver.wait()
        log.close()
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=5)
    dump(
        output / "results.json",
        {
            "mode": "real isolated Firefox; actual VideoStage/useHls for HLS; standalone MP4 control",
            "growing_event_playlist": growing,
            "manifest_requests": manifest_requests,
            "fixture_results_sha256": hashlib.sha256((fixtures / "results.json").read_bytes()).hexdigest(),
            "results": results,
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--growing", action="store_true")
    args = parser.parse_args()
    run(args.fixtures.resolve(), args.output.resolve(), args.growing)
