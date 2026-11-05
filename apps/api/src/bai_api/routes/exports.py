"""Exports: canonical JSONL, CSV v2, legacy 8-column CSV, PDF match report, frame-exact clips."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import FileResponse, Response, StreamingResponse

from bai_api.deps import Repo, SessionDep, SettingsDep
from bai_api.public import public_session
from bai_engine.media import Tools
from bai_engine.timeline import format_clock

router = APIRouter(prefix="/api/sessions", tags=["exports"])


def _fname(session: Any, suffix: str) -> str:
    base = "".join(c if c.isalnum() else "_" for c in session.title)[:60] or "match"
    return f"{base}_{suffix}"


@router.get("/{session_id}/exports/events.jsonl")
def events_jsonl(session: SessionDep, r: Repo, live: bool = True) -> StreamingResponse:
    with r.analysis_snapshot(session.session_id) as (session, store, _):
        evs = store.all_live() if live else store.since(0, limit=10**7)

    def gen():  # type: ignore[no-untyped-def]
        for e in evs:
            yield e.model_dump_json() + "\n"

    return StreamingResponse(
        gen(),
        media_type="application/x-ndjson",
        headers={"Content-Disposition": f'attachment; filename="{_fname(session, "events.jsonl")}"'},
    )


def _rally_rows(session: Any, r: Any) -> list[dict[str, Any]]:
    with r.analysis_snapshot(session.session_id) as (current, store, _):
        return _snapshot_rally_rows(current, store)


def _snapshot_rally_rows(session: Any, store: Any) -> list[dict[str, Any]]:
    from bai_badminton.analytics.rebuild import rally_records

    tl = session.media.timeline() if session.media else None
    names = {p.player_id: p.name or p.player_id for p in session.players}
    rows = []
    for rec in rally_records(store):
        if not rec.official:  # warm-up / replayed exchanges are not rallies of the match
            continue
        rows.append(
            {
                "match_id": session.session_id,
                "game_id": rec.game_no,
                "rally_id": rec.rally_no,
                "frame_start": rec.start,
                "frame_end": rec.end,
                "start_time": tl.format_frame(rec.start, millis=True) if tl else "",
                "end_time": tl.format_frame(rec.end, millis=True) if tl else "",
                "duration_s": rec.duration_s,
                "winner": names.get(rec.winner or "", rec.winner),
                "loser": names.get(rec.loser or "", rec.loser),
                "outcome": rec.outcome,
                "shots": " ".join(s.get("stroke") or "unknown" for s in rec.shots),
                "n_shots": rec.n_shots,
                "score_P1": rec.score_after.get("P1") if rec.score_available else None,
                "score_P2": rec.score_after.get("P2") if rec.score_available else None,
                "score_available": rec.score_available,
                "rally_event_id": rec.rally_id,
                "_last_stroke": (rec.shots[-1].get("stroke") if rec.shots else "unknown"),
                "_winner_id": rec.winner,
            }
        )
    return rows


# Stable public application CSV schema, including an empty/failed analysis.
# This is independent of the seven-column research benchmark export.
_RALLY_COLUMNS = [
    "match_id",
    "game_id",
    "rally_id",
    "frame_start",
    "frame_end",
    "start_time",
    "end_time",
    "duration_s",
    "winner",
    "loser",
    "outcome",
    "shots",
    "n_shots",
    "score_P1",
    "score_P2",
    "score_available",
    "rally_event_id",
]


@router.get("/{session_id}/exports/rallies.csv")
def rallies_csv(session: SessionDep, r: Repo) -> Response:
    rows = _rally_rows(session, r)
    buf = io.StringIO()
    cols = _RALLY_COLUMNS
    w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
    return Response(
        buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{_fname(session, "rallies.csv")}"'},
    )


_LEGACY_REASON = {
    "out": "opponent goes out of bounds",
    "net": "opponent hits the net",
    "winner": "wins by landing",
    "unknown": "unknown",
}
_LEGACY_LOSE = {"out": "goes out of bounds", "net": "hits the net", "winner": "fails to return", "unknown": "unknown"}


@router.get("/{session_id}/exports/legacy.csv")
def legacy_csv(session: SessionDep, r: Repo) -> Response:
    """The original 8-column contract consumed by ``legacy/streamlit`` (times as M:SS / H:MM:SS)."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(
        [
            "start_time",
            "end_time",
            "win_point_player",
            "win_reason",
            "ball_types",
            "lose_reason",
            "roundscore_A",
            "roundscore_B",
        ]
    )
    with r.analysis_snapshot(session.session_id) as (session, store, _):
        tl = session.media.timeline() if session.media else None
        rows = _snapshot_rally_rows(session, store)
    for row in rows:
        if not row["winner"] or tl is None:
            continue
        w.writerow(
            [
                format_clock(tl.frame_to_pts_us(row["frame_start"])),
                format_clock(tl.frame_to_pts_us(row["frame_end"])),
                row["winner"],
                _LEGACY_REASON.get(row["outcome"], "unknown"),
                ", ".join(dict.fromkeys(row["shots"].split())).replace("_", " "),
                _LEGACY_LOSE.get(row["outcome"], "unknown"),
                row["score_P1"],
                row["score_P2"],
            ]
        )
    return Response(
        buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{_fname(session, "legacy.csv")}"'},
    )


def _proxy_revision(path: Path) -> tuple[int, int, int, int]:
    try:
        stat = path.stat()
    except FileNotFoundError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, "The proxy is not finished yet") from exc
    return stat.st_dev, stat.st_ino, stat.st_mtime_ns, stat.st_size


@router.get("/{session_id}/exports/clip.mp4")
def clip(
    session: SessionDep,
    r: Repo,
    s: SettingsDep,
    frame_from: Annotated[int, Query(alias="from", ge=0)],
    frame_to: Annotated[int, Query(alias="to", ge=0)],
    pad_s: Annotated[float, Query(ge=0, le=10)] = 1.0,
) -> FileResponse:
    """Frame-exact clip cut from the canonical proxy (re-encoded so cuts need not be on keyframes)."""
    if session.media is None or not session.source.sha256:
        raise HTTPException(status.HTTP_409_CONFLICT, "The video is still being prepared")
    if frame_to <= frame_from or frame_to - frame_from > session.media.fps * 600:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "invalid clip range (max 10 min)")
    tl = session.media.timeline()
    pad = int(pad_s * float(session.media.fps))
    a, b = max(0, frame_from - pad), min(session.media.n_frames - 1, frame_to + pad)
    src = r.media_paths(session.source.sha256).proxy
    proxy_revision = _proxy_revision(src)
    out_dir = r.paths(session.session_id).exports
    out_dir.mkdir(parents=True, exist_ok=True)
    # Legacy files may have been written directly and left partial on failure.
    # Only the new publication contract can make a cache entry reusable.
    contract = {
        "encoding": "proxy-clip-h264-veryfast-crf20-aac-faststart-v2",
        "source_sha256": session.source.sha256,
        "proxy_revision": proxy_revision,
        "fps": [session.media.fps_num, session.media.fps_den],
        "frames": [a, b],
    }
    key = hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest()
    out = out_dir / f"clip_v2_{a}_{b}_{key}.mp4"
    if not out.exists():
        tools = Tools.resolve(s.ffmpeg, s.ffprobe)
        t0, t1 = tl.frame_to_seconds(a), tl.frame_to_seconds(b + 1)
        cmd = [
            tools.ffmpeg,
            "-hide_banner",
            "-nostdin",
            "-y",
            "-loglevel",
            "error",
            "-ss",
            f"{t0:.6f}",
            "-i",
            str(src),
            "-t",
            f"{t1 - t0:.6f}",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
        ]
        # Concurrent requests may each encode, but readers only ever see a
        # complete file. Failed/timed-out private output is discarded on exit.
        with tempfile.TemporaryDirectory(prefix=".clip-", dir=out_dir) as temporary:
            staged = Path(temporary) / "clip.mp4"
            try:
                res = subprocess.run(  # noqa: S603
                    [*cmd, str(staged)], capture_output=True, timeout=300, check=False
                )
            except subprocess.TimeoutExpired as exc:
                raise HTTPException(status.HTTP_504_GATEWAY_TIMEOUT, "clip encoding timed out") from exc
            if res.returncode != 0 or not staged.is_file() or staged.stat().st_size == 0:
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "clip encoding failed")
            if _proxy_revision(src) != proxy_revision:
                raise HTTPException(
                    status.HTTP_409_CONFLICT, "The proxy changed during clip encoding; retry the request"
                )
            staged.replace(out)
    return FileResponse(out, media_type="video/mp4", filename=_fname(session, f"clip_{a}-{b}.mp4"))


@router.get("/{session_id}/exports/report.pdf")
def report_pdf(session: SessionDep, r: Repo, request: Request) -> FileResponse:
    from bai_api.report import build_report

    with r.analysis_snapshot(session.session_id) as (session, store, _):
        a = request.app.state.analytics.get(session.session_id)
        rows = _snapshot_rally_rows(session, store)
    out_dir = r.paths(session.session_id).exports
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=out_dir, suffix=".pdf", delete=False) as tmp:
        path = Path(tmp.name)
    build_report(path, session, a, rows)
    return FileResponse(path, media_type="application/pdf", filename=_fname(session, "report.pdf"))


@router.get("/{session_id}/exports/summary.json")
def summary_json(session: SessionDep, r: Repo, request: Request) -> Response:
    with r.analysis_snapshot(session.session_id) as (session, _, _):
        a = request.app.state.analytics.get(session.session_id)
    body = {
        "session": public_session(session).model_dump(mode="json"),
        "analytics": a.to_public(),
        "highlights": [h.to_public() for h in a.highlights(k=10)],
    }
    return Response(json.dumps(body, indent=2), media_type="application/json")
