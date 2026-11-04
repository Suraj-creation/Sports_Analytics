"""Read-only contact/event audit and controlled production-code probes.

The constructed probes test code semantics, not contact accuracy on footage.
No pipeline, source video, annotation, or frozen result is changed.
"""

from __future__ import annotations

import argparse
import collections
import copy
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bai_badminton.events.contact import score_frame  # noqa: E402
from bai_badminton.events.rally_fsm import RallyFSM, RallyParams  # noqa: E402
from bai_badminton.observations import PlayerSeries, WindowObs  # noqa: E402
from bai_badminton.perception.shuttle_post import Track  # noqa: E402


def live_events(events):
    superseded = {e["supersedes"] for e in events if e.get("supersedes")}
    return [e for e in events if e["event_id"] not in superseded and e["status"] != "retracted"]


def component_scores(event):
    return next((e["scores"] for e in event["evidence"] if e["kind"] == "component_scores"), {})


def history_probe():
    fsm = RallyFSM(RallyParams(fps=30))
    fsm.on_contact(0)
    for frame in range(10):
        fsm.step(frame, True, 0.0)
    assert fsm.state.value == "ending"
    control = copy.deepcopy(fsm)
    baseline_contact = fsm.on_contact(10)
    assert fsm.state.value == "in_play"
    before = {"state": fsm.state.value, "recent": list(fsm._recent)}
    fsm.step(10, True, 10.0)
    control.on_contact(10)
    control._recent.clear()  # explicit research-only intervention, not production
    control.step(10, True, 10.0)
    assert fsm.state.value == "ending"
    assert control.state.value == "in_play"
    return {
        "name": "precontact_stationary_history_reends_same_frame",
        "before_step": before,
        "accepted_contact_frame": 10,
        "current_observed_speed": 10.0,
        "baseline_after": {"state": fsm.state.value, "tentative_end": fsm.tentative_end},
        "counterfactual_clear_recent_after": {"state": control.state.value, "tentative_end": control.tentative_end},
        "baseline_contact_started": baseline_contact.started,
        "interpretation": (
            "Accepted contact changes state but precontact low-motion history immediately reverses it, "
            "despite current motion >resume speed."
        ),
    }


def jitter_probe():
    n = 9
    x = np.array([0.02 * i if i <= 4 else 0.08 - 0.6 * (i - 4) for i in range(n)])
    y = np.zeros(n)
    player = PlayerSeries.empty(n)
    player.bbox[:] = [-10, -15, 10, 85]
    window = WindowObs(0, 30, Track.from_arrays(x, y, np.ones(n, dtype=bool)), {"P1": player})
    candidate = score_frame(window, 4)
    assert candidate is not None
    assert candidate.scores["redirect"] == candidate.scores["impulse"] == 1.0
    assert candidate.p > 0.9
    return {
        "name": "small_displacement_ratio_saturation",
        "image_window_span_px": float(np.ptp(x)),
        "player_body_height_px": 100,
        "heuristic_support": candidate.p,
        "scores": candidate.components,
        "racket_observation_present": False,
        "pose_present": False,
        "interpretation": (
            "Tiny pre-turn speed makes relative impulse saturate; this is heuristic sensitivity, "
            "not a labeled false contact."
        ),
    }


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    baseline = ROOT / "outputs/benchmarking/test1"
    raw = [json.loads(line) for line in (baseline / "raw_events.jsonl").open()]
    live = live_events(raw)
    contacts = [e for e in live if e["type"] == "contact"]
    traces = [
        json.loads(line)
        for line in (ROOT / "artifacts/benchmarking/investigation/baseline_semantic_replay/fsm_trace.jsonl").open()
    ]
    steps = {r["frame"]: r for r in traces if r["call"] == "step"}
    calls = [r for r in traces if r["call"] == "contact"]
    immediate = [
        r
        for r in calls
        if steps[r["frame"]]["after"]["state"] == "ending" and steps[r["frame"]]["after"]["end_reason"] == "stationary"
    ]
    unique_live_frames = {e["frame_start"] for e in contacts}
    assert unique_live_frames <= {r["frame"] for r in calls}
    actor_count = collections.Counter(str(e["actors"].get("player_id")) for e in contacts)
    score_rows = [component_scores(e) for e in contacts]
    current_starts = {e["frame_start"] for e in live if e["type"] == "rally_start"}
    summary = {
        "mode": "recorded-evidence audit and synthetic code-semantic probes; no fresh inference",
        "raw_contact_event_entries": sum(e["type"] == "contact" for e in raw),
        "raw_contact_status_counts": dict(collections.Counter(e["status"] for e in raw if e["type"] == "contact")),
        "accepted_fsm_contact_calls": len(calls),
        "current_live_contacts": len(contacts),
        "cancelled_or_withdrawn_contact_calls": len(calls) - len(contacts),
        "named_actor_counts": dict(actor_count),
        "attribution_reason_counts": dict(
            collections.Counter(e["payload"].get("attribution_reason") for e in contacts)
        ),
        "participant_status_counts": dict(
            collections.Counter(
                e["payload"].get("participant_hypothesis", {}).get("status", "absent") for e in contacts
            )
        ),
        "participant_reason_counts": dict(
            collections.Counter(
                e["payload"].get("participant_hypothesis", {}).get("reason", "absent") for e in contacts
            )
        ),
        "physical_racket_contact_observed_count": sum(
            e["payload"].get("racket_contact_observed", False) for e in contacts
        ),
        "racket_overlap_observed_count": sum(e["payload"].get("racket_overlap_observed", False) for e in contacts),
        "racket_geometry_available_count": sum(
            e["payload"].get("racket_evidence_method") is not None for e in contacts
        ),
        "positive_swing_support_count": sum(s["swing"] > 0 for s in score_rows),
        "same_frame_stationary_reentry_after_contact_count": len(immediate),
        "same_frame_stationary_reentry_frames": [r["frame"] for r in immediate],
        "contact_state_before_counts": dict(collections.Counter(r["before"]["state"] for r in calls)),
        "contact_closed_actions": dict(
            collections.Counter(
                "new_start" if r["update"]["started"] is not None else "reopen"
                for r in calls
                if r["before"]["state"] == "closed"
            )
        ),
        "contact_started_provisional_count": sum(r["update"]["started"] is not None for r in calls),
        "live_rally_starts_from_contact": sum(
            r["update"]["started"] is not None and r["frame"] in current_starts for r in calls
        ),
        "score_quantiles": {
            key: dict(
                zip(
                    ["min", "p25", "median", "p75", "max"],
                    np.quantile([s[key] for s in score_rows], [0, 0.25, 0.5, 0.75, 1]).tolist(),
                    strict=True,
                )
            )
            for key in ["redirect", "impulse", "proximity", "swing", "speed_before", "speed_after"]
        },
        "controlled_probes": [history_probe(), jitter_probe()],
        "contact_accuracy": "unavailable: no independent physical contact timestamp/player labels supplied",
    }
    special = []
    for frame in [264, 2210, 2217, 12748, 12771]:
        special.append(
            {
                "frame": frame,
                "events": [e for e in raw if e["type"] == "contact" and e["frame_start"] == frame],
                "trace_contact": [r for r in calls if r["frame"] == frame],
                "trace_step": steps[frame],
            }
        )
    (output / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    (output / "boundary_contact_evidence.json").write_text(json.dumps(special, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {key: value for key, value in summary.items() if key not in {"score_quantiles", "controlled_probes"}},
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    main(args.output.resolve())
