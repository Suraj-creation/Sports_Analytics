"""Model registry: resolve, fetch and verify model artifacts listed in ``models/manifest.yaml``.

* Artifacts are cached under ``models/cache/<name>/``.
* Every artifact's sha256 is pinned: either in the manifest, or — for ``pin-on-first-fetch`` —
  in ``models/cache/lock.json`` the first time it is downloaded.  A later load whose digest
  differs is refused (supply-chain / corrupted-download protection).
* Zip artifacts (OpenMMLab ONNX SDK bundles) are extracted and the ``.onnx`` inside is returned.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import threading
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from bai_engine.obs import get_logger

log = get_logger(__name__)
PIN = "pin-on-first-fetch"


class ModelError(RuntimeError):
    pass


@dataclass(frozen=True)
class ModelSpec:
    name: str
    task: str
    version: str
    format: str
    source: dict[str, str]
    sha256: str | None
    license: str
    input: dict[str, Any]
    size: int | None = None
    status: str = "active"

    @property
    def ref(self) -> str:
        return f"{self.name}@{self.version}"


class ModelRegistry:
    def __init__(self, models_dir: Path) -> None:
        self.models_dir = Path(models_dir)
        self.cache = self.models_dir / "cache"
        self.cache.mkdir(parents=True, exist_ok=True)
        manifest = yaml.safe_load((self.models_dir / "manifest.yaml").read_text(encoding="utf-8"))
        self.specs: dict[str, ModelSpec] = {
            name: ModelSpec(
                name=name,
                task=m["task"],
                version=str(m.get("version", "0")),
                format=m["format"],
                source=m.get("source", {}),
                sha256=m.get("sha256"),
                license=m.get("license", "unknown"),
                input=m.get("input", {}),
                size=m.get("size"),
                status=m.get("status", "active"),
            )
            for name, m in manifest["models"].items()
        }
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ lock file
    @property
    def _lock_path(self) -> Path:
        return self.cache / "lock.json"

    def _locked(self) -> dict[str, str]:
        try:
            data = json.loads(self._lock_path.read_text(encoding="utf-8"))
            assert isinstance(data, dict)
            return {str(k): str(v) for k, v in data.items()}
        except FileNotFoundError:
            return {}

    def _pin(self, name: str, digest: str) -> None:
        data = self._locked()
        data[name] = digest
        self._lock_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    # ------------------------------------------------------------------ public
    def get(self, name: str) -> ModelSpec:
        try:
            return self.specs[name]
        except KeyError as e:
            raise ModelError(f"model {name!r} is not in models/manifest.yaml") from e

    def is_available(self, name: str) -> bool:
        spec = self.get(name)
        if spec.format in ("builtin", "package"):
            return True
        return self._artifact_path(spec).exists()

    def path(self, name: str, *, fetch: bool = True) -> Path:
        """Local path of the (verified) artifact; downloads it when missing and ``fetch``."""
        spec = self.get(name)
        if spec.format in ("builtin", "package"):
            raise ModelError(f"{name} has no file artifact")
        with self._lock:
            art = self._artifact_path(spec)
            if not art.exists():
                if not fetch:
                    raise ModelError(f"{name} is not downloaded; run `bai models fetch {name}`")
                self._fetch(spec, art)
            self._verify(spec, art)
            if spec.format == "onnx-zip":
                return self._extract_onnx(spec, art)
            return art

    def status(self) -> list[dict[str, Any]]:
        out = []
        locked = self._locked()
        for name, spec in sorted(self.specs.items()):
            out.append(
                {
                    "name": name,
                    "task": spec.task,
                    "version": spec.version,
                    "format": spec.format,
                    "license": spec.license,
                    "status": spec.status,
                    "available": self.is_available(name),
                    "sha256": spec.sha256 if spec.sha256 not in (None, PIN) else locked.get(name),
                }
            )
        return out

    # ------------------------------------------------------------------ internals
    def _artifact_path(self, spec: ModelSpec) -> Path:
        fname = Path(spec.source.get("file") or spec.source.get("url", spec.name).rsplit("/", 1)[-1]).name
        return self.cache / spec.name / fname

    def _fetch(self, spec: ModelSpec, dest: Path) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".part")
        src = spec.source
        log.info("model.fetch", model=spec.name, source=src)
        if "hf" in src:
            from huggingface_hub import hf_hub_download

            p = hf_hub_download(repo_id=src["hf"], filename=src["file"], cache_dir=str(self.cache / ".hf"))
            shutil.copyfile(p, tmp)
        elif "url" in src:
            if not src["url"].startswith("https://"):
                raise ModelError("model URLs must be https")
            with urllib.request.urlopen(src["url"], timeout=120) as r, tmp.open("wb") as f:  # noqa: S310
                shutil.copyfileobj(r, f, length=1 << 20)
        elif "gdrive_folder" in src:
            raise ModelError(
                f"{spec.name} is distributed via Google Drive (folder {src['gdrive_folder']}); "
                f"download {src.get('file')} manually into {dest.parent} and re-run"
            )
        else:
            raise ModelError(f"{spec.name}: unsupported source {src}")
        if spec.size and tmp.stat().st_size != spec.size:
            tmp.unlink(missing_ok=True)
            raise ModelError(f"{spec.name}: size mismatch (expected {spec.size})")
        tmp.replace(dest)

    def _verify(self, spec: ModelSpec, art: Path) -> None:
        digest = _sha256(art)
        expected = spec.sha256 if spec.sha256 not in (None, PIN) else self._locked().get(spec.name)
        if expected is None:
            self._pin(spec.name, digest)
            log.info("model.pinned", model=spec.name, sha256=digest)
        elif expected != digest:
            raise ModelError(f"{spec.name}: sha256 mismatch ({digest} != pinned {expected}); refusing to load")

    def _extract_onnx(self, spec: ModelSpec, zpath: Path) -> Path:
        out_dir = zpath.parent / "extracted"
        existing = sorted(out_dir.rglob("*.onnx")) if out_dir.exists() else []
        if existing:
            return existing[0]
        out_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(zpath) as z:
            for member in z.infolist():
                target = (out_dir / member.filename).resolve()
                if not str(target).startswith(str(out_dir.resolve())):
                    raise ModelError("zip slip detected")
            z.extractall(out_dir)
        found = sorted(out_dir.rglob("*.onnx"))
        if not found:
            raise ModelError(f"{spec.name}: no .onnx inside archive")
        return found[0]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()
