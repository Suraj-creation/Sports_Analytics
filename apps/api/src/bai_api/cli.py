"""``bai`` command-line entry point.

bai serve                 API (+ embedded engine unless BAI_REDIS_URL / BAI_ENGINE_MODE=external)
bai engine                standalone GPU engine worker (consumes commands from Redis)
bai models list|fetch     model registry status / download + pin weights
bai analyse VIDEO         one-shot analysis of a local file from the command line (no browser)
"""

from __future__ import annotations

import argparse
import signal
import sys
import threading
import time
from pathlib import Path


def _serve(args: argparse.Namespace) -> None:
    import uvicorn

    from bai_api.app import create_app
    from bai_engine.config import get_settings

    s = get_settings()
    uvicorn.run(
        create_app(s),
        host=args.host or s.bind_host,
        port=args.port or s.port,
        log_level="info",
        proxy_headers=False,
        ws_max_size=4 * 1024 * 1024,
    )


def _engine(_: argparse.Namespace) -> None:
    from bai_engine.bus import make_bus
    from bai_engine.config import get_settings
    from bai_engine.obs import configure_logging
    from bai_engine.runtime.runner import EngineService
    from bai_engine.store import SessionRepository

    configure_logging(json_logs=True)
    s = get_settings()
    if not s.redis_url:
        sys.exit("bai engine requires BAI_REDIS_URL (standalone engine talks to the API through Redis)")
    svc = EngineService(SessionRepository(s.data_dir), make_bus(s.redis_url), s)
    svc.start()
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    while not stop.wait(1.0):
        pass
    svc.shutdown()


def _models(args: argparse.Namespace) -> None:
    from bai_engine.config import get_settings
    from bai_engine.runtime.registry import ModelRegistry

    reg = ModelRegistry(get_settings().models_dir)
    if args.action == "list":
        for m in reg.status():
            flag = "✓" if m["available"] else "·"
            print(f"{flag} {m['name']:<26} {m['task']:<18} {m['status']:<10} {m['license'][:60]}")
        return
    names = args.names or [
        n for n, sp in reg.specs.items() if sp.format not in ("builtin", "package") and sp.status == "active"
    ]
    for n in names:
        try:
            print(f"{n}: {reg.path(n)}")
        except Exception as e:
            print(f"{n}: FAILED — {e}")


def _analyse(args: argparse.Namespace) -> None:
    from bai_engine.bus import LocalBus
    from bai_engine.config import get_settings
    from bai_engine.obs import configure_logging
    from bai_engine.runtime.runner import EngineService
    from bai_engine.schema import Session, SessionStatus, Source, SourceKind
    from bai_engine.sources import store_upload
    from bai_engine.store import SessionRepository

    configure_logging()
    s = get_settings()
    if args.profile:
        s = s.model_copy(update={"profile": args.profile})
    repo = SessionRepository(s.data_dir)
    src = Path(args.video)
    with src.open("rb") as f:
        stored = store_upload(iter(lambda: f.read(1 << 20), b""), s.data_dir / "media", src.name, s.max_upload_bytes)
    session = repo.save(
        Session(
            title=src.stem,
            profile=s.profile,
            source=Source(kind=SourceKind.UPLOAD, uri=str(stored.path), original_name=src.name, sha256=stored.sha256),
        )
    )
    svc = EngineService(repo, LocalBus(), s)
    svc.dispatch({"cmd": "start", "session_id": session.session_id})
    while True:
        cur = repo.get(session.session_id)
        assert cur is not None
        print(f"\r{cur.status.value:<14} frame {cur.frontier_frame}/{cur.media.n_frames if cur.media else '?'}", end="")
        if cur.status in (SessionStatus.ANALYSED, SessionStatus.FAILED):
            break
        time.sleep(1.0)
    print()
    store = repo.events(session.session_id)
    print(
        f"session {session.session_id}: {store.count('rally_end')} rallies, {store.count('stroke')} strokes, "
        f"state={store.state_at(10**12).state if store.state_at(10**12) else None}"
    )


def main() -> None:
    p = argparse.ArgumentParser(prog="bai")
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("serve")
    sp.add_argument("--host")
    sp.add_argument("--port", type=int)
    sp.set_defaults(fn=_serve)
    sub.add_parser("engine").set_defaults(fn=_engine)
    mp = sub.add_parser("models")
    mp.add_argument("action", choices=["list", "fetch"])
    mp.add_argument("names", nargs="*")
    mp.set_defaults(fn=_models)
    ap = sub.add_parser("analyse")
    ap.add_argument("video")
    ap.add_argument("--profile")
    ap.set_defaults(fn=_analyse)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
