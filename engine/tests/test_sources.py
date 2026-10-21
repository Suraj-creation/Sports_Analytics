from pathlib import Path

import pytest

from bai_engine.sources import SourceError, parse_youtube_url, safe_ext, store_upload


@pytest.mark.parametrize(
    ("url", "vid"),
    [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ?t=42", "dQw4w9WgXcQ"),
        ("https://m.youtube.com/watch?v=dQw4w9WgXcQ&list=x", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ],
)
def test_youtube_urls(url: str, vid: str) -> None:
    assert parse_youtube_url(url) == vid


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "https://evil.example.com/watch?v=dQw4w9WgXcQ",
        "https://youtube.com.evil.com/watch?v=dQw4w9WgXcQ",
        "https://user:pw@www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com:8443/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=short",
        "https://www.youtube.com/playlist?list=PL123",
        "http://169.254.169.254/latest/meta-data",
    ],
)
def test_youtube_rejects(url: str) -> None:
    with pytest.raises(SourceError):
        parse_youtube_url(url)


def test_store_upload_content_addressed(tmp_path: Path) -> None:
    a = store_upload([b"abc", b"def"], tmp_path, "../../evil name.MP4", max_bytes=100)
    assert a.path.name == "source.mp4" and a.path.parent.name == a.sha256
    assert a.path.read_bytes() == b"abcdef"
    b = store_upload([b"abcdef"], tmp_path, "other.mp4", max_bytes=100)
    assert b.sha256 == a.sha256 and b.path == a.path  # dedup
    assert not list(tmp_path.glob(".upload-*"))


def test_store_upload_limits(tmp_path: Path) -> None:
    with pytest.raises(SourceError):
        store_upload([b"x" * 60, b"x" * 60], tmp_path, "a.mp4", max_bytes=100)
    assert not list(tmp_path.glob(".upload-*"))  # temp file cleaned
    with pytest.raises(SourceError):
        safe_ext("payload.exe")
