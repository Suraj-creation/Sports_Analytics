"""Restore one explicitly requested public Drive asset with exact-byte binding."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode, urlparse

import requests


class Forms(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        row = dict(attrs)
        if tag == "form":
            self.current = {"action": row.get("action", ""), "fields": {}}
            self.forms.append(self.current)
        elif tag == "input" and self.current is not None and row.get("name"):
            self.current["fields"][row["name"]] = row.get("value", "")

    def handle_endtag(self, tag):
        if tag == "form":
            self.current = None


def save(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file-id", required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--expected-bytes", type=int, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]{10,128}", args.file_id):
        raise ValueError("Invalid file identifier")
    if not re.fullmatch(r"[a-f0-9]{64}", args.expected_sha256) or args.expected_bytes <= 0:
        raise ValueError("Exact original byte identity is required")
    if Path(args.filename).name != args.filename or not args.filename.endswith(".mp4"):
        raise ValueError("Require a plain mp4 basename")
    out = args.output_dir.absolute()
    if out.exists() or out.is_symlink():
        raise FileExistsError("Use a NEW owned download directory; preserve existing attempts")
    out.mkdir(parents=True)
    partial = out / (args.filename + ".part")
    target = out / args.filename
    started = time.time()
    request = {
        "file_id": args.file_id,
        "expected_sha256": args.expected_sha256,
        "expected_bytes": args.expected_bytes,
        "started_utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "source_url": f"https://drive.google.com/file/d/{args.file_id}/view",
        "output_file": str(target),
        "original_annotations_modified": False,
    }
    save(out / "request.json", request)
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0"
    url = "https://drive.usercontent.google.com/download?" + urlencode(
        {"id": args.file_id, "export": "download", "confirm": "t"}
    )
    try:
        for attempt in range(3):
            response = session.get(url, stream=True, timeout=(30, 120))
            response.raise_for_status()
            kind = response.headers.get("Content-Type", "")
            if "text/html" not in kind:
                break
            data = bytearray()
            for chunk in response.iter_content(65536):
                data.extend(chunk)
                if len(data) > 2 * 1024**2:
                    raise ValueError("Unexpected oversized confirmation page")
            response.close()
            (out / f"confirmation_{attempt}.html").write_bytes(data)
            forms = Forms()
            forms.feed(data.decode("utf-8", errors="replace"))
            chosen = None
            for form in forms.forms:
                action = urlparse(form["action"])
                if (
                    action.scheme == "https"
                    and action.netloc in {"drive.usercontent.google.com", "drive.google.com"}
                    and form["fields"].get("id") == args.file_id
                ):
                    chosen = form
                    break
            if chosen is None:
                raise ValueError("No public download form: access/quota/confirmation page preserved")
            url = chosen["action"] + "?" + urlencode(chosen["fields"])
        else:
            raise ValueError("Public download confirmation did not resolve")
        count = 0
        digest = hashlib.sha256()
        last_report = 0.0
        with partial.open("xb") as stream:
            for chunk in response.iter_content(8 * 1024**2):
                if not chunk:
                    continue
                stream.write(chunk)
                digest.update(chunk)
                count += len(chunk)
                if count > args.expected_bytes:
                    raise ValueError("Downloaded bytes exceed exact original identity")
                now = time.time()
                if now - last_report >= 20:
                    print(
                        json.dumps(
                            {
                                "status": "downloading",
                                "bytes": count,
                                "expected_bytes": args.expected_bytes,
                                "percent": round(100 * count / args.expected_bytes, 1),
                            }
                        ),
                        flush=True,
                    )
                    last_report = now
        response.close()
        actual = digest.hexdigest()
        if count != args.expected_bytes or actual != args.expected_sha256:
            raise ValueError(f"Original byte identity mismatch: bytes={count}, sha256={actual}; partial preserved")
        os.link(partial, target)
        partial.unlink()
        save(
            out / "completion.json",
            {
                **request,
                "status": "completed_exact_original_restoration",
                "bytes": count,
                "sha256": actual,
                "elapsed_seconds": time.time() - started,
                "large_video_files_downloaded": 1,
                "original_data_modified": False,
            },
        )
        print(
            json.dumps({"status": "completed_exact_original_restoration", "bytes": count, "sha256": actual}), flush=True
        )
    except BaseException as error:
        save(
            out / "failure.json",
            {
                **request,
                "status": "failed_partial_preserved",
                "error_type": type(error).__name__,
                "error": str(error),
                "elapsed_seconds": time.time() - started,
            },
        )
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
