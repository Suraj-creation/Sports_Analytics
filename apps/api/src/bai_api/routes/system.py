"""System status, models, profiles, health and Prometheus metrics."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from bai_api.deps import SettingsDep, User
from bai_engine.config import load_profile
from bai_engine.obs import REGISTRY
from bai_engine.runtime.device import system_info
from bai_engine.runtime.registry import ModelRegistry

router = APIRouter(tags=["system"])


@router.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/system")
def system(request: Request, s: SettingsDep, _: User) -> dict[str, Any]:
    engine = request.app.state.engine
    runners = []
    if engine is not None:
        for sid, r in list(engine.runners.items()):
            runners.append({"session_id": sid, "alive": r.is_alive(), "main_segment": r.main_k})
    try:
        prof = load_profile(s.profile, s.profiles_dir).model_dump()
    except FileNotFoundError:
        prof = None
    return {
        "system": system_info(),
        "profile": prof,
        "engine_mode": s.engine_mode,
        "runners": runners,
        "youtube_ingest": s.youtube_ingest,
        "limits": {"max_upload_mb": s.max_upload_bytes // 2**20, "max_duration_min": s.max_duration_s // 60},
    }


@router.get("/api/models")
def models(s: SettingsDep, _: User) -> list[dict[str, Any]]:
    return ModelRegistry(s.models_dir).status()


@router.get("/api/profiles")
def profiles(s: SettingsDep, _: User) -> list[dict[str, Any]]:
    out = []
    for p in sorted(s.profiles_dir.glob("*.yaml")):
        prof = load_profile(p.stem, s.profiles_dir)
        out.append({"name": prof.name, "description": prof.description, "device": prof.device})
    return out


@router.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
