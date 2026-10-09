"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from bai_api.auth import Auth
from bai_engine.bus import Bus, make_bus
from bai_engine.config import REPO_ROOT, Settings, get_settings
from bai_engine.obs import configure_logging, get_logger
from bai_engine.store import SessionRepository

log = get_logger(__name__)
WEB_DIST = REPO_ROOT / "apps" / "web" / "dist"


def create_app(settings: Settings | None = None, bus: Bus | None = None, start_engine: bool = True) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configure_logging()
        app.state.settings = settings
        app.state.auth = Auth(settings)
        app.state.repo = SessionRepository(settings.data_dir)
        app.state.bus = bus or make_bus(settings.redis_url)
        app.state.engine = None
        if start_engine and settings.engine_mode == "embedded":
            from bai_engine.runtime.runner import EngineService

            app.state.engine = EngineService(app.state.repo, app.state.bus, settings)
            app.state.engine.start()
        from bai_api.analytics import AnalyticsCache

        app.state.analytics = AnalyticsCache(app.state.repo)
        log.info(
            "api.started",
            bind=settings.bind_host,
            port=settings.port,
            engine=settings.engine_mode,
            auth=app.state.auth.enabled,
        )
        yield
        if app.state.engine is not None:
            app.state.engine.shutdown()
        app.state.repo.close()
        app.state.bus.close()

    app = FastAPI(
        title="Badminton AI", version="0.1.0", lifespan=lifespan, docs_url="/api/docs", openapi_url="/api/openapi.json"
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):  # type: ignore[no-untyped-def]
        resp: Response = await call_next(request)
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "same-origin")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        return resp

    @app.exception_handler(ValueError)
    async def value_error(_: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=422)

    from bai_api.routes import agents, auth_routes, exports, media, sessions, system
    from bai_api.ws import router as ws_router

    for r in (
        auth_routes.router,
        sessions.router,
        media.router,
        exports.router,
        system.router,
        agents.router,
        ws_router,
    ):
        app.include_router(r)

    if WEB_DIST.exists():
        app.mount("/assets", StaticFiles(directory=WEB_DIST / "assets"), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        async def spa(path: str) -> FileResponse:
            # API, socket and metrics paths never fall through to the app shell
            if path.split("/", 1)[0] in ("api", "ws", "metrics") or ".." in path.split("/"):
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
            f = (WEB_DIST / path).resolve()
            if path and f.is_file() and str(f).startswith(str(WEB_DIST.resolve())):
                return FileResponse(f)
            return FileResponse(WEB_DIST / "index.html")

    return app


def data_path(app: FastAPI) -> Path:
    return Path(app.state.settings.data_dir)
