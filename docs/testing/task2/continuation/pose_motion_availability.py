import collections
import hashlib
import importlib.util
import json
import pathlib
import sys

import msgpack
import numpy as np

from bai_badminton.events.contact import _wrist_speed
from bai_badminton.observations import PlayerSeries

root = pathlib.Path(sys.argv[1]).resolve()
old_path = root / "baseline-source/sports/badminton/src/bai_badminton/events/contact.py"
spec = importlib.util.spec_from_file_location("task2_contact_baseline", old_path)
old = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = old
spec.loader.exec_module(old)
frames = []
digest = hashlib.sha256()
for p in sorted((root / "real-after/data/sessions/01M5MBR3087FH07N5B1XR5VGHW/perception").glob("*.msgpack")):
    b = p.read_bytes()
    digest.update(b)
    frames.extend(msgpack.unpackb(b, raw=False)["frames"])
n = len(frames)
series = {}
schedule = np.zeros(n, dtype=np.int64)
for f in frames:
    i = f["f"]
    if f["cs"] != "VALID" or f["v"] != "main":
        continue
    schedule[i] = f["ps"] if f["ps"] is not None else -1
    for person in f["p"]:
        t = person["t"]
        if t not in series:
            series[t] = PlayerSeries.empty(n)
        s = series[t]
        s.bbox[i] = person["b"]
        if person["k"] is not None:
            s.kps[i] = person["k"]
c = collections.Counter()
for f in frames:
    i = f["f"]
    if schedule[i] <= 0:
        continue
    for person in f["p"]:
        s = series[person["t"]]
        lo = max(0, i - 4)
        hi = min(n, i + 4)
        w = PlayerSeries(s.bbox[lo:hi], s.kps[lo:hi], s.court_xy[lo:hi])
        j = i - lo
        a = old._wrist_speed(w, j)
        b = _wrist_speed(w, j, frame0=lo, pose_stride=schedule[lo:hi])
        c["tested_track_frame_windows"] += 1
        c["before_motion_available"] += a is not None and np.isfinite(a)
        c["after_motion_available"] += b is not None and np.isfinite(b)
        c["newly_available"] += a is None and b is not None
r = {
    "kind": "identical_observation_component_diagnostic",
    "input_cache_sha256": digest.hexdigest(),
    "counts": {k: int(v) for k, v in c.items()},
    "accuracy_claim": False,
    "limitations": (
        "Temporary-track local windows only; presence of a finite motion cue is not contact correctness "
        "or durable identity. "
        "Both methods consume identical new-run pose/box observations."
    ),
}
(root / "pose-motion-availability.json").write_text(json.dumps(r, indent=2) + "\n")
print(json.dumps(r, indent=2))
