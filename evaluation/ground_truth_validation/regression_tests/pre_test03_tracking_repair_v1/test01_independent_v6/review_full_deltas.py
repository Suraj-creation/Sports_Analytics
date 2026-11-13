"""Additional full timeline deltas after native completion, with no inference."""

import importlib.util
import json
from collections import Counter
from hashlib import file_digest
from pathlib import Path

import msgpack

OUT = Path(__file__).resolve().parent
CFG = json.loads((OUT / "review_config.json").read_text())
ART = Path(CFG["artifact_root"])
MAIN = Path(CFG["main_root"])


def sha(p):
    with Path(p).open("rb") as f:
        return file_digest(f, "sha256").hexdigest()


def save(name, data):
    with (OUT / name).open("x") as f:
        json.dump(data, f, indent=2, allow_nan=False)
        f.write("\n")


def read(p):
    return json.loads(Path(p).read_text())


def packed(x):
    return msgpack.packb(x, use_bin_type=True)


def packets(root):
    catalogue = read(root / "run/perception_completion_catalog.json")
    result = []
    for item in catalogue["files"]:
        p = root / "run" / item["path"]
        assert sha(p) == item["sha256"]
        result.extend(msgpack.unpackb(p.read_bytes(), raw=False)["frames"])
    assert [f["f"] for f in result] == list(range(CFG["frame_count"]))
    return result


def main():
    assert read(OUT / "summary.json")["candidate_commit"] == CFG["expected_commit"]
    current = packets(ART)
    raw_summary = {}
    for name, root in [
        ("original", Path(CFG["baseline_root"])),
        ("previous_5ae", Path(CFG["previous_candidate_root"])),
    ]:
        before = packets(root)
        fields = {k: [] for k in ["s", "c", "do", "ps", "p", "fg", "sa", "aq", "g", "v", "cs", "ce", "sh", "r"]}
        rows = []
        for a, b in zip(before, current, strict=True):
            changed = [k for k in fields if packed(a.get(k)) != packed(b.get(k))]
            for key in changed:
                fields[key].append(b["f"])
            if changed:
                rows.append(
                    {
                        "frame": b["f"],
                        "changed_fields": changed,
                        "before": {k: a.get(k) for k in changed if k not in {"p", "fg"}},
                        "fresh": {k: b.get(k) for k in changed if k not in {"p", "fg"}},
                        "before_people": [{k: p.get(k) for k in ["t", "b", "dm", "pf", "rf"]} for p in a["p"]],
                        "fresh_people": [{k: p.get(k) for k in ["t", "b", "dm", "pf", "rf"]} for p in b["p"]],
                        "payload_scope": (
                            "Full pose/racket/foreground values retained in hash-bound immutable source cache; "
                            "this row indexes actual differences."
                        ),
                    }
                )
        with (OUT / f"all_raw_changed_rows_{name}.jsonl").open("x") as f:
            for row in rows:
                f.write(json.dumps(row, allow_nan=False) + "\n")
        old_det = {r["f"] for r in before if r["do"] is True}
        new_det = {r["f"] for r in current if r["do"] is True}
        raw_summary[name] = {
            "frames": len(current),
            "differing_frame_counts": {k: len(v) for k, v in fields.items()},
            "differing_frame_ids": fields,
            "extra_detector_frames": sorted(new_det - old_det),
            "lost_detector_frames": sorted(old_det - new_det),
            "lower_person_count_frames": [
                b["f"] for a, b in zip(before, current, strict=True) if len(b["p"]) < len(a["p"])
            ],
            "raw_shuttle_xy_and_support_identical": not fields["s"] and not fields["c"],
            "full_raw_values_remain_in_original_hash_bound_caches": True,
        }
    save("full_raw_timeline_differences.json", raw_summary)

    point_detail = {}
    fresh_rows = [
        json.loads(line) for line in (ART / "bound_reference_diagnostics/frame_point_candidates.jsonl").open()
    ]
    for name, root in [
        ("original", Path(CFG["baseline_root"])),
        ("previous_5ae", Path(CFG["previous_candidate_root"])),
    ]:
        old_rows = [
            json.loads(line) for line in (root / "bound_reference_diagnostics/frame_point_candidates.jsonl").open()
        ]

        def pairs(rows, key):
            return {
                (r["frame"], p["reference_slot"]): {
                    "distance": p["distance_px"],
                    "current": r["current_players"][p["current_index"]],
                }
                for r in rows
                for p in r.get(key, [])
            }

        scopes = {}
        for key in ["all_current_rows_assignments", "fresh_detector_rows_assignments"]:
            a, b = pairs(old_rows, key), pairs(fresh_rows, key)
            common = a.keys() & b.keys()
            changed = [
                {
                    "frame": f,
                    "reference_slot": slot,
                    "before": a[(f, slot)],
                    "fresh": b[(f, slot)],
                    "distance_delta": b[(f, slot)]["distance"] - a[(f, slot)]["distance"],
                }
                for f, slot in sorted(common)
                if a[(f, slot)]["distance"] != b[(f, slot)]["distance"]
            ]
            save(f"all_changed_point_pairs_{name}_{key}.json", changed)
            scopes[key] = {
                "common": len(common),
                "equal_errors": len(common) - len(changed),
                "worse": sum(r["distance_delta"] > 0 for r in changed),
                "better": sum(r["distance_delta"] < 0 for r in changed),
                "maximum_increase": max([r["distance_delta"] for r in changed], default=0),
                "new_only": len(b.keys() - a.keys()),
                "old_only": len(a.keys() - b.keys()),
                "largest_increases": sorted(changed, key=lambda r: r["distance_delta"], reverse=True)[:5],
            }
        point_detail[name] = scopes
    save("point_change_detail.json", point_detail)
    helper_path = MAIN / "evaluation/ground_truth_validation/test_02/fixes/review_semantic_effects.py"
    spec = importlib.util.spec_from_file_location("retained_event_comparison", helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    old = helper.live(Path(CFG["previous_candidate_root"]) / "run/events.jsonl")
    fresh = helper.live(ART / "run/events.jsonl")
    events = {
        "scope": "Previous5ae completed freshNN versus current3eb6 completed freshNN; no physical GT",
        "before_counts": dict(Counter(r["type"] for r in old)),
        "fresh_counts": dict(Counter(r["type"] for r in fresh)),
    }
    for kind in ["contact", "stroke"]:
        try:
            events[kind] = helper.compare_kind(old, fresh, kind)
        except ValueError as error:
            a = {row["frame_start"]: helper.compact_event(row) for row in old if row["type"] == kind}
            b = {row["frame_start"]: helper.compact_event(row) for row in fresh if row["type"] == kind}
            if len(a) != sum(row["type"] == kind for row in old) or len(b) != sum(row["type"] == kind for row in fresh):
                raise ValueError("Duplicate event anchors require explicit review, not dictionary collapse") from error
            events[kind] = {
                "nearby_anchor_association_status": "unavailable_rally_context_changed",
                "reason": str(error),
                "scope": "Exact-anchor changes only; no inferred shifted-event pairing",
                "before_count": len(a),
                "after_count": len(b),
                "candidate_temporal_shifts": [],
                "unpaired_removed": [a[f] for f in sorted(a.keys() - b.keys())],
                "unpaired_added": [b[f] for f in sorted(b.keys() - a.keys())],
                "same_anchor_changes": [
                    {
                        "frame": f,
                        "before": a[f],
                        "after": b[f],
                        "changes": {
                            key: {"before": a[f][key], "after": b[f][key]} for key in a[f] if a[f][key] != b[f][key]
                        },
                    }
                    for f in sorted(a.keys() & b.keys())
                    if a[f] != b[f]
                ],
            }
    save("event_differences_previous_5ae.json", events)
    all_event_changes = []

    def indexed(data):
        seen, result = Counter(), {}
        for event in data:
            basis = (event["type"], event["frame_start"], event["frame_end"])
            ordinal = seen[basis]
            seen[basis] += 1
            result[(*basis, ordinal)] = event
        return result

    a, b = indexed(old), indexed(fresh)
    for key in sorted(a.keys() | b.keys()):
        # Keep every live event type and payload. Native IDs/versions remain
        # visible; exact time/ordinal association is diagnostic, not identity GT.
        if a.get(key) != b.get(key):
            all_event_changes.append({"key": key, "before": a.get(key), "current": b.get(key)})
    save("all_event_type_exact_anchor_changes_previous_5ae.json", all_event_changes)
    a = read(Path(CFG["previous_candidate_root"]) / "bound_reference_diagnostics/component_reference_metrics.json")
    b = read(ART / "bound_reference_diagnostics/component_reference_metrics.json")
    interval = {}
    for key, value in a["interval_reference_comparisons"].items():
        current_ref = b["interval_reference_comparisons"][key]
        interval[key] = {
            "metrics_exactly_equal": value["metrics"] == current_ref["metrics"],
            "comparison_rows_exactly_equal": value["comparison"] == current_ref["comparison"],
            "before_metrics": value["metrics"],
            "fresh_metrics": current_ref["metrics"],
        }
    save("interval_secondary_2418_comparison.json", interval)
    preflight = read(ART / "preflight.json")
    for p, h in preflight["protected_input_sha256"].items():
        assert sha(p) == h, p
    annotations = [p for p in preflight["protected_input_sha256"] if Path(p).is_relative_to(MAIN / "Part2")]
    copies = [
        p for p in preflight["protected_input_sha256"] if Path(p).is_relative_to(Path(CFG["native_root"]) / "Part2")
    ]
    assert len(annotations) == 62 and len(copies) == 9
    assert len(preflight["protected_input_sha256"]) == 94
    for copy in copies:
        original = MAIN / "Part2" / Path(copy).relative_to(Path(CFG["native_root"]) / "Part2")
        assert str(original) in preflight["protected_input_sha256"]
        assert sha(copy) == sha(original)
    save(
        "protected_inputs_review.json",
        {
            "status": "all_protected_inputs_unchanged",
            "preflight_sha256": sha(ART / "preflight.json"),
            "protected_count": len(preflight["protected_input_sha256"]),
            "original_MAIN_Part2_files_verified": 62,
            "candidate_Test1_annotation_copies_verified": 9,
            "copies_equal_originals": True,
            "protected_paths_sha256": preflight["protected_input_sha256"],
            "no_other_test_annotation_contents_inspected": True,
        },
    )
    print(
        json.dumps(
            {
                "raw": {
                    k: {x: v[x] for x in ["differing_frame_counts", "raw_shuttle_xy_and_support_identical"]}
                    for k, v in raw_summary.items()
                },
                "secondary_reference_metrics_equal": all(v["metrics_exactly_equal"] for v in interval.values()),
                "previous_event_counts": events["before_counts"],
                "fresh_event_counts": events["fresh_counts"],
            }
        )
    )


if __name__ == "__main__":
    main()
