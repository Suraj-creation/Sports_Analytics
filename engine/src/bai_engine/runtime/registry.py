"""Model registry: resolve, fetch and verify model artifacts listed in ``models/manifest.yaml``.

* Artifacts are cached under ``models/cache/<name>/``.
* Every artifact's sha256 is pinned: either in the manifest, or — for ``pin-on-first-fetch`` —
  in ``models/cache/lock.json`` the first time it is downloaded.  A later load whose digest
  differs is refused (integrity protection). First-use pinning does not
  authenticate the publisher or establish that a pickle is safe to execute.
* Zip artifacts (OpenMMLab ONNX SDK bundles) are extracted and the ``.onnx`` inside is returned.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import tempfile
import threading
import urllib.request
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO
from uuid import uuid4

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


@dataclass(frozen=True)
class VerifiedArtifact:
    """A private, seekable snapshot whose bytes match a registry integrity pin.

    ``path`` describes provenance; loaders must read ``stream``. First-use pins
    establish later integrity, not publisher authenticity or pickle safety.
    The registry owns the stream and closes it when its context exits.
    """

    path: Path
    sha256: str
    stream: BinaryIO


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
        """Commit pins atomically; the caller owns the process transaction lock."""
        data = self._locked()
        data[name] = digest
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", prefix=".pins-", suffix=".tmp", dir=self.cache, delete=False
            ) as stream:
                temporary = Path(stream.name)
                stream.write(json.dumps(data, indent=2, sort_keys=True))
                stream.flush()
                os.fsync(stream.fileno())
            temporary.replace(self._lock_path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    @contextmanager
    def _pin_transaction(self) -> Iterator[None]:
        """Serialize read/compare/pin across registry instances and processes.

        The lock lives in a stable separate file because lock.json is replaced
        atomically. OS advisory locks are released on descriptor close/process
        exit; a leftover lock pathname is not a stale ownership marker.
        """
        with (self.cache / ".pins.lock").open("a+b") as stream:
            if os.name == "nt":
                import msvcrt

                stream.seek(0)
                if not stream.read(1):
                    stream.write(b"\0")
                    stream.flush()
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
                try:
                    yield
                finally:
                    stream.seek(0)
                    msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

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

    @contextmanager
    def open_verified(self, name: str, *, fetch: bool = True) -> Iterator[VerifiedArtifact]:
        """Open exact verified raw-artifact bytes without a path-to-load race.

        A disk-backed snapshot bounds memory and remains stable if another
        process replaces or mutates the cached path after verification. Archive
        extraction needs a separate derived-artifact contract and is deliberately
        unavailable through this raw-checkpoint API.
        """
        spec = self.get(name)
        if spec.format in ("builtin", "package", "onnx-zip"):
            raise ModelError(f"{name} has no supported raw file artifact")
        with tempfile.TemporaryFile(mode="w+b", prefix=".verified-", dir=self.cache) as snapshot:
            with self._lock:
                art = self._artifact_path(spec)
                if not art.exists():
                    if not fetch:
                        raise ModelError(f"{name} is not downloaded; run `bai models fetch {name}`")
                    self._fetch(spec, art)
                digest = hashlib.sha256()
                with art.open("rb") as original:
                    for block in iter(lambda: original.read(1 << 20), b""):
                        snapshot.write(block)
                        digest.update(block)
                verified_digest = digest.hexdigest()
                self._verify_digest(spec, verified_digest)
            snapshot.seek(0)
            yield VerifiedArtifact(path=art, sha256=verified_digest, stream=snapshot)

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
        src = spec.source
        log.info("model.fetch", model=spec.name, source=src)
        # Independent registry instances/processes may fetch the same missing
        # artifact. Never share a writable inode or expose it before the copy
        # completes; another downloader could otherwise truncate pinned bytes.
        with tempfile.TemporaryDirectory(prefix=".fetch-", dir=dest.parent) as staging:
            tmp = Path(staging) / dest.name
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
                raise ModelError(f"{spec.name}: size mismatch (expected {spec.size})")
            # Reject conflicting downloads before they replace a good artifact.
            # First-use compare/pin already uses the cross-process transaction.
            self._verify(spec, tmp)
            tmp.replace(dest)

    def _verify(self, spec: ModelSpec, art: Path) -> None:
        digest = _sha256(art)
        self._verify_digest(spec, digest)

    def _verify_digest(self, spec: ModelSpec, digest: str) -> None:
        if spec.sha256 not in (None, PIN):
            if spec.sha256 != digest:
                raise ModelError(
                    f"{spec.name}: sha256 mismatch ({digest} != pinned {spec.sha256}); refusing to load"
                )
            return
        # The thread lock alone cannot coordinate another registry/process.
        # Keep expected-read, mismatch rejection and first-pin commit together.
        with self._pin_transaction():
            expected = self._locked().get(spec.name)
            if expected is None:
                self._pin(spec.name, digest)
                log.info("model.pinned", model=spec.name, sha256=digest)
            elif expected != digest:
                raise ModelError(f"{spec.name}: sha256 mismatch ({digest} != pinned {expected}); refusing to load")

    def _extract_onnx(self, spec: ModelSpec, zpath: Path) -> Path:
        # Extraction consumes the same private bytes that pass verification.
        # Preserve legacy extracted/ artifacts, but never trust their provenance.
        with tempfile.TemporaryFile(mode="w+b", prefix=".archive-", dir=zpath.parent) as snapshot:
            digest = hashlib.sha256()
            with zpath.open("rb") as original:
                for block in iter(lambda: original.read(1 << 20), b""):
                    snapshot.write(block)
                    digest.update(block)
            archive_digest = digest.hexdigest()
            self._verify_digest(spec, archive_digest)
            snapshot.seek(0)
            cache = zpath.parent / "extracted-v1"
            cache.mkdir(exist_ok=True)
            for published in sorted(cache.glob(f"{archive_digest}-*")):
                graph = self._cached_archive_graph(published, archive_digest)
                if graph is not None:
                    return graph
            # Separate objects let concurrent workers publish complete bundles
            # without replacing a directory another loader may already be using.
            with tempfile.TemporaryDirectory(prefix=".extract-", dir=cache) as temporary:
                staged = Path(temporary)
                files_root = staged / "files"
                files_root.mkdir()
                files: dict[str, str] = {}
                with zipfile.ZipFile(snapshot) as archive:
                    for member in archive.infolist():
                        target = self._archive_member_path(files_root, member.filename)
                        mode = stat.S_IFMT(member.external_attr >> 16)
                        if mode not in (0, stat.S_IFREG, stat.S_IFDIR):
                            raise ModelError("archive links and special files are not supported")
                        if member.is_dir():
                            target.mkdir(parents=True, exist_ok=True)
                            continue
                        relative = target.relative_to(files_root).as_posix()
                        if relative in files:
                            raise ModelError("duplicate archive path")
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with archive.open(member) as source, target.open("xb") as output:
                            shutil.copyfileobj(source, output, length=1 << 20)
                        files[relative] = _sha256(target)
                graphs = sorted(name for name in files if name.endswith(".onnx"))
                if not graphs:
                    raise ModelError(f"{spec.name}: no .onnx inside archive")
                record = {
                    "schema": "verified-archive-extraction-v1",
                    "archive_sha256": archive_digest,
                    "graph": graphs[0],
                    "files": files,
                }
                (staged / "manifest.json").write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
                published = cache / f"{archive_digest}-{uuid4().hex}"
                staged.replace(published)
                return published / "files" / graphs[0]

    @staticmethod
    def _archive_member_path(root: Path, name: str) -> Path:
        path = PurePosixPath(name)
        if (
            not path.parts or path.is_absolute() or ".." in path.parts
            or "\\" in name or ":" in name or "\0" in name
        ):
            raise ModelError("unsafe archive path")
        target = root.joinpath(*path.parts)
        if not target.resolve().is_relative_to(root.resolve()):
            raise ModelError("unsafe archive path")
        return target

    @classmethod
    def _cached_archive_graph(cls, published: Path, archive_digest: str) -> Path | None:
        try:
            root = published / "files"
            if published.is_symlink() or root.is_symlink():
                return None
            record = json.loads((published / "manifest.json").read_text(encoding="utf-8"))
            if record["schema"] != "verified-archive-extraction-v1" or record["archive_sha256"] != archive_digest:
                return None
            files, graph = record["files"], record["graph"]
            if not isinstance(files, dict) or not isinstance(graph, str) or graph not in files:
                return None
            contents = list(root.rglob("*"))
            if any(path.is_symlink() for path in contents):
                return None
            actual = {path.relative_to(root).as_posix() for path in contents if path.is_file()}
            if actual != set(files):
                return None
            for name, expected in files.items():
                path = cls._archive_member_path(root, name)
                if _sha256(path) != expected:
                    return None
            return cls._archive_member_path(root, graph)
        except (OSError, ValueError, KeyError, TypeError, ModelError):
            return None


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()
