"""Read-only independent audit of closed acquisition prefix evidence; no inference."""
import hashlib
import json
from pathlib import Path

import av
import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
PREFIX = HERE.parent / "prefix_v2"


def sha(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def save(name, value):
    with (HERE / name).open("x") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")


def main():
    summary = json.loads((PREFIX / "summary.json").read_text())
    inputs = summary["input_sha256"]
    details = [json.loads((PREFIX / f"test{c['test']}_{c['range'][0]:05d}_{c['range'][1]:05d}.json").read_text()) for c in summary["cases"]]
    current = {a: set() for a in ("original", "c7", "foreground")}
    stale = []
    banks = set()
    decisions = []
    decoded_counts = {}
    pixels = []
    for detail in details:
        test = detail["test"]
        start, end = detail["range"]
        bank = {x["frame"]: x for x in detail["detector_inputs"]}
        banks.update((test, frame) for frame in bank)
        for arm, rows in detail["variants"].items():
            for row in rows:
                dg = row["tracking_diagnostic"] or {}
                valid = dg.get("frame_idx") == row["frame"] and dg.get("detector_executed") is True
                if valid:
                    current[arm].add((test, row["frame"]))
                    assert row["frame"] in bank
                if row["detector_observed"] and not valid:
                    stale.append({"test": test, "arm": arm, "frame": row["frame"], "diagnostic": row["tracking_diagnostic"], "persons": len(row["persons"])})
                decision = row["decision"]
                if arm == "foreground" and decision:
                    assert decision["detector_image_sha256"] == row["source_pixels_sha256"]
                    assert decision["detector_frame"] == row["frame"]
                    origin = np.array(dg["crop_origin"] * 2)
                    proposals = np.asarray(bank[row["frame"]]["boxes_crop"], float).reshape(-1, 4) + origin
                    assert np.allclose(proposals, decision["detector_boxes"], rtol=0, atol=1e-9)
                    assert np.allclose(bank[row["frame"]]["scores"], decision["detector_scores"], rtol=0, atol=1e-12)
                    decisions.append({"test": test, "frame": row["frame"], "barrier": row["barrier"], "decision": decision, "raw_status": row["raw_content"]["status"], "raw_hypothesis": row["raw_content"]["hypothesis"]})
        proxy = next(Path(p) for p in inputs if p.endswith("/proxy.mp4") and detail["source_sha256"] in p)
        assert sha(proxy) == detail["proxy_sha256"] == inputs[str(proxy)]
        count = 0
        with av.open(str(proxy)) as container:
            stream = container.streams.video[0]
            stream.thread_count = 1
            container.seek(int(start / 30 / stream.time_base), stream=stream, backward=True)
            for decoded in container.decode(video=0):
                frame = round(float(decoded.pts * decoded.time_base) * 30)
                if frame < start:
                    continue
                if frame > end:
                    break
                rows = {a: rows[frame - start] for a, rows in detail["variants"].items()}
                assert all(row["frame"] == frame for row in rows.values())
                assert all(row["source_pts"] == decoded.pts and row["source_time_base"] == str(decoded.time_base) for row in rows.values())
                image = decoded.to_ndarray(format="bgr24")
                digest = hashlib.sha256(image.tobytes()).hexdigest()
                assert all(row["source_pixels_sha256"] == digest for row in rows.values())
                pixels.append({"test": test, "frame": frame, "pts": decoded.pts, "time_base": str(decoded.time_base), "pixels_sha256": digest})
                count += 1
                if test == 2 and frame in (6150, 6151):
                    panels = []
                    for arm, row in rows.items():
                        panel = image.copy()
                        for person in row["persons"]:
                            box = np.asarray(person["bbox"]).astype(int)
                            cv2.rectangle(panel, tuple(box[:2]), tuple(box[2:]), (0, 230, 0) if person["detector_matched"] else (0, 150, 250), 2)
                        for region in row["foreground_regions"]:
                            box = np.asarray(region["bbox"]).astype(int)
                            cv2.rectangle(panel, tuple(box[:2]), tuple(box[2:]), (255, 170, 0), 1)
                        cv2.putText(panel, f"{arm} f{frame} barrier={row['barrier']} diagnostic, no physical GT", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, .6, (255, 255, 255), 2)
                        panels.append(panel)
                    assert cv2.imwrite(str(HERE / f"test2_frame_{frame:05d}.png"), np.concatenate(panels, axis=1))
        assert count == end - start + 1
        decoded_counts[f"test{test}_{start}_{end}"] = count
    calls = set.union(*current.values())
    save("cadence_audit.json", {
        "schema": "independent-prefix-cadence-audit:v1", "executed_commit": summary["candidate_commit"],
        "predicate": "tracking_diagnostic.frame_idx == row.frame AND detector_executed is True",
        "current_frame_diagnostic_execution_counts": {a: len(v) for a, v in current.items()},
        "stale_observed_property_records": stale,
        "additional_foreground_execution_frames_vs_original": sorted(current["foreground"] - current["original"]),
        "lost_foreground_execution_frames_vs_original": sorted(current["original"] - current["foreground"]),
        "proposal_bank_unique_frames": len(banks), "unused_retained_bank_frames": sorted(banks - calls),
        "fresh_neural_forwards": sum(c["fresh_neural_detector_calls"] for c in summary["cases"]),
        "caveat": "detector_observed is a sticky property during off-main skips; it is not a per-row execution receipt. Shared/seed proposal consumption is not a fresh neural forward."
    })
    save("source_pixels_audit.json", {"schema": "independent-source-pixel-audit:v1", "decoded_frames": len(pixels), "case_counts": decoded_counts, "pixels": pixels, "physical_ground_truth": None})
    save("decision_binding_audit.json", {"schema": "independent-raw-proposal-decision-binding:v1", "decisions": decisions, "exact_bank_plus_crop_origin_comparisons": len(decisions), "physical_ground_truth": None})
    print(json.dumps({"frames": len(pixels), "decisions": len(decisions), "counts": {a: len(v) for a, v in current.items()}, "stale_records": len(stale)}))


if __name__ == "__main__":
    main()
