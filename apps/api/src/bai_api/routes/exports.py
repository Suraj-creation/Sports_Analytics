"""Exports: canonical JSONL, CSV v2, legacy 8-column CSV, PDF match report, frame-exact clips."""

from __future__ import annotations

import csv
import io
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import FileResponse, Response, StreamingResponse

from bai_api.deps import Repo, SessionDep, SettingsDep
from bai_engine.media import Tools
from bai_engine.timeline import format_clock

router = APIRouter(prefix="/api/sessions", tags=["exports"])


def _fname(session: Any, suffix: str) -> str:
    base = "".join(c if c.isalnum() else "_" for c in session.title)[:60] or "match"
    return f"{base}_{suffix}"


@router.get("/{session_id}/exports/events.jsonl")
def events_jsonl(session: SessionDep, r: Repo, live: bool = True) -> StreamingResponse:
    store = r.events(session.session_id)
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
    from bai_badminton.analytics.rebuild import rally_records

    store = r.events(session.session_id)
    tl = session.media.timeline() if session.media else None
    names = {p.player_id: p.name or p.player_id for p in session.players}
    rows = []
    for rec in rally_records(store):
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
                "score_P1": rec.score_after.get("P1"),
                "score_P2": rec.score_after.get("P2"),
                "rally_event_id": rec.rally_id,
                "_last_stroke": (rec.shots[-1].get("stroke") if rec.shots else "unknown"),
                "_winner_id": rec.winner,
            }
        )
    return rows


@router.get("/{session_id}/exports/rallies.csv")
def rallies_csv(session: SessionDep, r: Repo) -> Response:
    rows = _rally_rows(session, r)
    buf = io.StringIO()
    cols = [k for k in (rows[0] if rows else {"match_id": ""}) if not k.startswith("_")]
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
    tl = session.media.timeline() if session.media else None
    for row in _rally_rows(session, r):
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
    if not src.exists():
        raise HTTPException(status.HTTP_409_CONFLICT, "The proxy is not finished yet")
    out_dir = r.paths(session.session_id).exports
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"clip_{a}_{b}.mp4"
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
            str(out),
        ]
        res = subprocess.run(cmd, capture_output=True, timeout=300, check=False)  # noqa: S603
        if res.returncode != 0:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "clip encoding failed")
    return FileResponse(out, media_type="video/mp4", filename=_fname(session, f"clip_{a}-{b}.mp4"))


@router.get("/{session_id}/exports/report.pdf")
def report_pdf(session: SessionDep, r: Repo, request: Request) -> FileResponse:
    from bai_api.report import build_report

    a = request.app.state.analytics.get(session.session_id)
    rows = _rally_rows(session, r)
    out_dir = r.paths(session.session_id).exports
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=out_dir, suffix=".pdf", delete=False) as tmp:
        path = Path(tmp.name)
    build_report(path, session, a, rows)
    return FileResponse(path, media_type="application/pdf", filename=_fname(session, "report.pdf"))


@router.get("/{session_id}/exports/summary.json")
def summary_json(session: SessionDep, request: Request) -> Response:
    a = request.app.state.analytics.get(session.session_id)
    body = {
        "session": session.model_dump(mode="json"),
        "analytics": a.to_public(),
        "highlights": [h.to_public() for h in a.highlights(k=10)],
    }
    return Response(json.dumps(body, indent=2), media_type="application/json")
