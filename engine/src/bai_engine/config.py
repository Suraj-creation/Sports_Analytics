"""Process configuration (environment / .env) and compute profiles (YAML)."""

from __future__ import annotations

import functools
import secrets
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """All runtime settings. Read from environment variables prefixed ``BAI_`` and ``.env``."""

    model_config = SettingsConfigDict(env_prefix="BAI_", env_file=".env", extra="ignore")

    data_dir: Path = REPO_ROOT / "data"
    models_dir: Path = REPO_ROOT / "models"
    profiles_dir: Path = REPO_ROOT / "config" / "profiles"
    profile: str = "cpu-dev"

    # transport
    bind_host: str = "127.0.0.1"
    port: int = 8000
    redis_url: str | None = None  # None → in-process bus (single-process dev mode)
    engine_mode: Literal["embedded", "external"] = "embedded"

    # security (single user)
    passphrase: SecretStr | None = None  # required when bind_host is not loopback
    session_secret: SecretStr = Field(default_factory=lambda: SecretStr(secrets.token_urlsafe(32)))
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # ingest limits
    max_upload_bytes: int = 4 * 1024**3
    max_duration_s: int = 3 * 3600
    youtube_ingest: bool = False
    youtube_max_height: int = 1080
    ffmpeg: str = "ffmpeg"
    ffprobe: str = "ffprobe"
    ffprobe_timeout_s: float = 30.0

    # analysis proxy
    proxy_height: int = 720
    hls_segment_s: float = 2.0

    # LLM
    llm_provider: str = "azure_openai"
    llm_budget_tokens_per_session: int = 400_000

    @property
    def is_loopback(self) -> bool:
        return self.bind_host in {"127.0.0.1", "localhost", "::1"}


@functools.cache
def get_settings() -> Settings:
    return Settings()


# ---------------------------------------------------------------------- profiles
class ModelChoice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str  # registry name in models/manifest.yaml, or "none"
    backend: Literal["tensorrt", "onnx-cuda", "onnx-cpu", "torch-cuda", "torch-cpu", "none"] = "onnx-cpu"
    precision: Literal["fp32", "fp16", "int8"] = "fp32"
    batch: int = 1
    input_size: tuple[int, int] | None = None  # (width, height)
    params: dict[str, Any] = Field(default_factory=dict)


class Rates(BaseModel):
    """Frames-between-inferences (stride) per rally state. 1 = every frame, 0 = disabled."""

    model_config = ConfigDict(extra="forbid")

    in_play: int = 1
    idle: int = 1
    replay: int = 0


class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str = ""
    device: Literal["cuda", "cpu"] = "cpu"
    analysis_height: int = 720
    chunk_frames: int = 64
    lead_buffer_s: float = 5.0

    shuttle: ModelChoice
    shuttle_live: ModelChoice | None = None
    shuttle_second_opinion: ModelChoice | None = None
    player_detector: ModelChoice
    pose: ModelChoice
    racket: ModelChoice | None = None
    stroke: ModelChoice
    contact: ModelChoice | None = None
    ocr: ModelChoice | None = None

    detector_rates: Rates = Rates(in_play=2, idle=6, replay=0)
    pose_rates: Rates = Rates(in_play=1, idle=6, replay=0)
    shuttle_rates: Rates = Rates(in_play=1, idle=1, replay=0)
    ocr_every_s: float = 1.0
    court_verify_every_s: float = 2.0

    escalation_budget: float = 0.15  # max fraction of extra GPU time spent on refinement
    racket_window: int = 6  # ± frames around a contact candidate


def load_profile(name: str, profiles_dir: Path | None = None) -> Profile:
    d = profiles_dir or get_settings().profiles_dir
    path = d / f"{name}.yaml"
    if not path.exists():
        available = sorted(p.stem for p in d.glob("*.yaml"))
        raise FileNotFoundError(f"profile {name!r} not found in {d}; available: {available}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data.setdefault("name", name)
    return Profile.model_validate(data)
