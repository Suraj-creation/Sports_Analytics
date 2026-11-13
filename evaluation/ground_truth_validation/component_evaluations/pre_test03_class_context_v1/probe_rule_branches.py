"""Isolate unchanged heuristic branches using already serialized input fields."""

from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

from bai_badminton.events.stroke import RuleStrokeClassifier, StrokeContext

HERE = Path(__file__).resolve().parent
source = HERE / "causal_readout.json"
readout = json.loads(source.read_text())
results = []
for case in readout["class_flips"]:
    for arm in ["before", "after"]:
        payload = case[arm]
        context = StrokeContext(
            frame=case["frame"],
            player_id=None,
            is_serve=payload["is_serve"],
            hitter_court_xy=tuple(payload["hitter_court_xy"]),
            speed_after_px_s=payload["speed_px_s"],
            frame_height_px=720.0,
            flight_time_s=payload["flight_time_s"],
            vy_after_px_s=None,
            hitter_side=None,
            contact_above_head=None,
        )
        prediction = RuleStrokeClassifier().predict(context)
        label, support = prediction.top
        assert label == payload["stroke"]
        assert support == payload["probs"][label]
        results.append(
            {
                "frame": case["frame"],
                "arm": arm,
                "label": label,
                "support": support,
                "speed_frame_heights_per_second": payload["speed_px_s"] / 720.0,
                "depth_m": abs(payload["hitter_court_xy"][1]),
                "flight_s": payload["flight_time_s"],
                "ground_truth": None,
            }
        )
module = Path(inspect.getfile(RuleStrokeClassifier)).resolve()
output = {
    "scope": (
        "Four model-free rule-branch probes using serialized data, not new NN or physical stroke labels. "
        "Unneeded vertical/head/side features remain None; these branches do not consult them."
    ),
    "input_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "actual_rule_source": str(module),
    "actual_rule_source_sha256": hashlib.sha256(module.read_bytes()).hexdigest(),
    "results": results,
    "no_configuration_or_source_changes": True,
}
with (HERE / "rule_branch_probe.json").open("x") as stream:
    json.dump(output, stream, indent=2)
    stream.write("\n")
print(json.dumps(results))
