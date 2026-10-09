"""PDF match report (ReportLab) built from canonical analytics — every number traceable to events."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

INK = colors.HexColor("#14211D")
MAT = colors.HexColor("#103129")
P1 = colors.HexColor("#2D7FD3")
P2 = colors.HexColor("#E0702A")


def build_report(path: Path, session: Any, analytics: Any, rallies: list[dict[str, Any]]) -> None:
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], textColor=MAT, fontSize=20, leading=24, alignment=0)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], textColor=MAT, spaceBefore=10)
    body = ParagraphStyle("b", parent=ss["BodyText"], textColor=INK, fontSize=9.5, leading=13)
    names = {p.player_id: p.name or p.player_id for p in session.players}
    pub = analytics.to_public()
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=session.title,
    )
    story: list[Any] = [
        Paragraph(session.title, h1),
        Paragraph(f"{names['P1']} vs {names['P2']} · {pub['rallies']} rallies analysed", body),
        Spacer(1, 6 * mm),
    ]

    story.append(Paragraph("Players", h2))
    keys = [
        ("points_won", "Points won"),
        ("winners", "Winners"),
        ("errors_out", "Errors (out)"),
        ("errors_net", "Errors (net)"),
        ("smashes", "Smashes"),
        ("jump_smashes", "Jump smashes"),
        ("smash_points", "Points from smashes"),
        ("serve_points_won", "Points won on serve"),
        ("points_won_under_pressure", "Points won under pressure"),
        ("distance_m", "Distance covered (m)"),
    ]
    pl = pub["players"]
    data = [["", names["P1"], names["P2"]]] + [
        [label, str(pl.get("P1", {}).get(k, "–")), str(pl.get("P2", {}).get(k, "–"))] for k, label in keys
    ]
    t = Table(data, colWidths=[70 * mm, 45 * mm, 45 * mm])
    t.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
                ("TEXTCOLOR", (1, 0), (1, 0), P1),
                ("TEXTCOLOR", (2, 0), (2, 0), P2),
                ("LINEBELOW", (0, 0), (-1, 0), 0.6, MAT),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6F4")]),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    story += [t, Spacer(1, 4 * mm)]

    hl = analytics.highlights(k=8)
    if hl:
        story.append(Paragraph("Highlights", h2))
        rows = [["#", "Rally", "Score", "Why it stands out"]]
        for i, h in enumerate(hl, 1):
            why = ", ".join(c.replace("_", " ") for c in h.categories) or ", ".join(h.reasons)
            rows.append([str(i), str(h.rally_no), f"{h.score:.1f}", why])
        ht = Table(rows, colWidths=[10 * mm, 18 * mm, 18 * mm, 114 * mm])
        ht.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
                    ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.6, MAT),
                ]
            )
        )
        story += [ht, Spacer(1, 4 * mm)]

    story.append(Paragraph("Rallies", h2))
    rrows = [["Rally", "Game", "Time", "Winner", "Outcome", "Shots", "Score"]]
    for r in rallies:
        rrows.append(
            [
                str(r["rally_id"]),
                str(r["game_id"]),
                r["start_time"],
                str(r["winner"] or "–"),
                r["outcome"],
                str(r["n_shots"]),
                f"{r['score_P1']}–{r['score_P2']}",
            ]
        )
    rt = Table(rrows, repeatRows=1, colWidths=[14 * mm, 14 * mm, 24 * mm, 40 * mm, 22 * mm, 16 * mm, 20 * mm])
    rt.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), "Helvetica", 8.5),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8.5),
                ("LINEBELOW", (0, 0), (-1, 0), 0.6, MAT),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6F4")]),
            ]
        )
    )
    story.append(rt)
    story += [
        Spacer(1, 6 * mm),
        Paragraph(
            "Figures are computed from the session's event log. Labels marked probable or uncertain in the app are "
            "model estimates; human-verified events take precedence.",
            body,
        ),
    ]
    doc.build(story)
