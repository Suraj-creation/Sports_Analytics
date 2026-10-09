"""Video sources → content-addressed local media.

* :func:`store_upload` streams an uploaded file to disk while hashing it (size-capped), then
  moves it to ``media/<sha256>/source<ext>`` — user-supplied names never touch the filesystem.
* :class:`YouTubeSource` downloads a YouTube video with ``yt-dlp`` under strict limits.  YouTube's
  Terms of Service restrict downloading; the feature is disabled unless ``BAI_YOUTUBE_INGEST`` is
  true and the user has acknowledged they hold the rights to the content.

Live sources (RTSP/SRT/WebRTC through MediaMTX) plug in behind the same ``Session.source`` field
with a causal profile; they are outside the VOD ingest path implemented here.
"""

from __future__ import annotations

import hashlib
import ipaddress
import re
import shutil
import socket
import tempfile
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from bai_engine.media.ffmpeg import MediaError

ALLOWED_EXTS = {
    ".mp4",
    ".mov",
    ".m4v",
    ".mkv",
    ".webm",
    ".avi",
    ".ts",
    ".mts",
    ".m2ts",
    ".flv",
    ".wmv",
    ".mpg",
    ".mpeg",
}
YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "music.youtube.com"}
_VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


class SourceError(ValueError):
    pass


@dataclass(frozen=True)
class StoredMedia:
    sha256: str
    path: Path
    size: int
    original_name: str | None


def safe_ext(name: str | None) -> str:
    ext = Path(name or "").suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise SourceError(f"unsupported file type {ext or '(none)'}; allowed: {', '.join(sorted(ALLOWED_EXTS))}")
    return ext


def store_upload(chunks: Iterable[bytes], media_root: Path, original_name: str | None, max_bytes: int) -> StoredMedia:
    ext = safe_ext(original_name)
    media_root.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256()
    size = 0
    tmp = tempfile.NamedTemporaryFile(dir=media_root, prefix=".upload-", delete=False)  # noqa: SIM115
    try:
        with tmp:
            for chunk in chunks:
                size += len(chunk)
                if size > max_bytes:
                    raise SourceError(f"file exceeds the {max_bytes // 1024**2} MB limit")
                h.update(chunk)
                tmp.write(chunk)
        digest = h.hexdigest()
        dest_dir = media_root / digest
        dest_dir.mkdir(exist_ok=True)
        dest = dest_dir / f"source{ext}"
        if dest.exists():
            Path(tmp.name).unlink()
        else:
            Path(tmp.name).replace(dest)
        return StoredMedia(digest, dest, size, original_name)
    except BaseException:
        Path(tmp.name).unlink(missing_ok=True)
        raise


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


# ---------------------------------------------------------------------- YouTube
def parse_youtube_url(url: str) -> str:
    """Return the 11-character video id, rejecting anything that is not a plain YouTube watch URL."""
    if len(url) > 300:
        raise SourceError("URL too long")
    u = urlparse(url.strip())
    if u.scheme not in ("https", "http"):
        raise SourceError("only http(s) URLs are accepted")
    host = (u.hostname or "").lower()
    if host not in YOUTUBE_HOSTS:
        raise SourceError("only youtube.com / youtu.be URLs are accepted")
    if u.username or u.password or (u.port not in (None, 80, 443)):
        raise SourceError("credentials and custom ports are not allowed in URLs")
    vid = None
    if host == "youtu.be":
        vid = u.path.lstrip("/").split("/")[0]
    elif u.path == "/watch":
        vid = (parse_qs(u.query).get("v") or [None])[0]
    elif u.path.startswith(("/shorts/", "/live/", "/embed/")):
        vid = u.path.split("/")[2]
    if not vid or not _VIDEO_ID.match(vid):
        raise SourceError("could not find a YouTube video id in the URL")
    return vid


def _resolves_public(host: str) -> bool:
    """SSRF guard: every address the host resolves to must be public."""
    try:
        infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
    except OSError:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            return False
    return True


@dataclass
class YouTubeSource:
    video_id: str
    max_height: int = 1080
    max_bytes: int = 4 * 1024**3
    max_duration_s: int = 3 * 3600

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"

    def download(self, media_root: Path, on_progress: Callable[[float], None] | None = None) -> StoredMedia:
        try:
            import yt_dlp
        except ImportError as e:  # pragma: no cover - dependency of bai-api
            raise SourceError("yt-dlp is not installed") from e
        if not _resolves_public("www.youtube.com"):
            raise SourceError("YouTube host did not resolve to a public address")
        work = Path(tempfile.mkdtemp(dir=media_root, prefix=".yt-"))

        def hook(d: dict[str, object]) -> None:
            if d.get("status") == "downloading" and on_progress is not None:
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                done = d.get("downloaded_bytes") or 0
                if isinstance(total, (int, float)) and total > 0 and isinstance(done, (int, float)):
                    on_progress(min(0.999, float(done) / float(total)))

        opts = {
            "format": f"bv*[height<={self.max_height}][ext=mp4]+ba[ext=m4a]/b[height<={self.max_height}]/b",
            "merge_output_format": "mp4",
            "outtmpl": str(work / "video.%(ext)s"),
            "noplaylist": True,
            "max_filesize": self.max_bytes,
            "match_filter": yt_dlp.utils.match_filter_func(f"duration <= {self.max_duration_s} & !is_live"),
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "progress_hooks": [hook],
            "cachedir": False,
            "socket_timeout": 30,
            "retries": 3,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
        except Exception as e:
            shutil.rmtree(work, ignore_errors=True)
            raise MediaError(f"YouTube download failed: {e}") from e
        files = sorted(work.glob("video.*"), key=lambda p: p.stat().st_size, reverse=True)
        if not files:
            shutil.rmtree(work, ignore_errors=True)
            raise MediaError("YouTube download produced no file (video too long, live, or filtered?)")
        f = files[0]
        title = str((info or {}).get("title") or self.video_id)
        stored = store_upload(_read_chunks(f), media_root, f"youtube{f.suffix}", self.max_bytes)
        shutil.rmtree(work, ignore_errors=True)
        return StoredMedia(stored.sha256, stored.path, stored.size, title)


def _read_chunks(path: Path, size: int = 1 << 20) -> Iterable[bytes]:
    with path.open("rb") as f:
        yield from iter(lambda: f.read(size), b"")
