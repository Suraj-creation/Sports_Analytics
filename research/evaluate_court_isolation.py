"""Reproducible real-video isolation checks; writes metrics and annotated samples."""

import fcntl
import json
import sqlite3
import time
from pathlib import Path

import cv2
import numpy as np

from bai_badminton.court import COURT_LINES
from bai_badminton.perception.court_lines import choose_main, detect_court
from bai_badminton.plugin import BadmintonSession, _corner_shift
from bai_engine.config import load_profile
from bai_engine.decode import DecodedChunk
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import Session
from bai_engine.store import EventStore

SID = "01M5EXGZNEVGYAJ3AR6CJS5ZG9"
root = Path("data/court-evaluation")
lock = (root / "evaluation.lock").open("w")
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
c = sqlite3.connect("data/sessions.sqlite")
session = Session.model_validate_json(c.execute("select body from sessions where session_id=?", (SID,)).fetchone()[0])
video = Path(session.source.uri).with_name("proxy.mp4")
cap = cv2.VideoCapture(str(video))


def at(i):
    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    ok, img = cap.read()
    if not ok:
        raise RuntimeError(f"cannot decode {i}")
    return img


indices = np.linspace(0, session.media.n_frames - 61, 24, dtype=int)
keys = [at(int(i)) for i in indices]
fits = [detect_court(f) for f in keys]
main = choose_main([f for f in fits if f is not None and f.ok])
print(
    "CALIBRATION",
    [
        (
            int(i),
            None if f is None else round(f.precision, 3),
            None if f is None else round(_corner_shift(f.H, main.H), 2),
        )
        for i, f in zip(indices, fits, strict=True)
    ],
    flush=True,
)
profile = load_profile("gpu-rtx4000")
store = EventStore(root / f"evaluation-{time.time_ns()}.sqlite", session.session_id)
s = BadmintonSession(session, store, profile, ModelRegistry(Path("models")), lambda e: None)
s.seed(keys)
print("CALIBRATION RECORD", store.query(types=["calibration"])[-1].payload, flush=True)
metrics = {"windows": [], "degraded": [d.__dict__ for d in s.perception.degraded]}
for start in (0, 900, 3600, 7200, 12000, 18000, 22000):
    cap.set(cv2.CAP_PROP_POS_FRAMES, start)
    imgs = []
    for _ in range(60):
        ok, img = cap.read()
        if ok:
            imgs.append(img)
    t = time.time()
    p = s.perceive(DecodedChunk(start=start, frames=imgs))
    row = {
        "start": start,
        "frames": len(imgs),
        "main": sum(f.view == "main" for f in p.frames),
        "players": sum(len(f.persons) for f in p.frames),
        "shuttle": sum(f.shuttle_xy is not None for f in p.frames),
        "seconds": round(time.time() - t, 2),
    }
    metrics["windows"].append(row)
    print("WINDOW", row, flush=True)
    for j in (0, 30):
        fp = p.frames[j]
        img = imgs[j].copy()
        hm = s.calibration.H if fp.cam is None else fp.cam @ s.calibration.H
        for a, b in COURT_LINES:
            xy = cv2.perspectiveTransform(np.array([[a, b]], float), hm)[0].astype(int)
            cv2.line(img, tuple(xy[0]), tuple(xy[1]), (0, 255, 255), 2)
        for person in fp.persons:
            b = person.bbox.astype(int)
            cv2.rectangle(img, tuple(b[:2]), tuple(b[2:]), (255, 100, 0), 2)
        if fp.shuttle_xy is not None:
            cv2.circle(img, tuple(np.array(fp.shuttle_xy).astype(int)), 7, (0, 0, 255), 2)
        cv2.imwrite(str(root / f"checked-{start + j}.jpg"), img)
metrics["note"] = "Sampled perception only. Event accuracy requires continuous full-video analysis."
(root / "metrics.json").write_text(json.dumps(metrics, indent=2))
print(json.dumps(metrics), flush=True)
