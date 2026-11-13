# ruff: noqa: E501
"""Independently bind every gallery membership to strict fresh source geometry."""

from __future__ import annotations

import json

import numpy as np
from measure_features import ART, BASE2, HERE, PREFIX, geometry, load


def main():
    results = json.loads((HERE / "results.json").read_text())
    features = {r["feature_id"]: r for r in (json.loads(s) for s in (HERE / "raw_features.jsonl").open())}
    first = load(ART / "run")
    second = load(BASE2 / "run", [(5505, 6510)])
    metadata = {1: first, 2: second}
    prefix = json.loads((PREFIX / "test2_05505_06510.json").read_text())
    member_ids = {fid for q in results["queries"] for fid in q["reference_bank"]}
    member_ids.update(fid for q in results["queries"] for ids in q["other_banks"].values() for fid in ids)
    checks = []
    for fid in sorted(member_ids):
        feature = features[fid]
        test = feature["test"]
        frame = feature["frame"]
        _info, raw, calibration_h, _ = metadata[test]
        row = raw[frame]
        regions = row["fg"] if test == 1 else prefix["variants"]["foreground"][frame - 5505]["foreground_regions"]
        region = next(r for r in regions if r["key"] == feature["key"])
        assert region["bbox"] == feature["bbox"]
        assert region["detector_observed"] is True and region["detector_matched"] is True
        roi = geometry(row, calibration_h)
        assert roi is not None and roi.contains_feet(np.asarray(feature["bbox"]), allow_runoff=False)
        x1, _, x2, y2 = feature["bbox"]
        point = roi.homography.image_to_court(np.array([[(x1 + x2) / 2, y2]]))[0]
        checks.append(
            {
                "feature_id": fid,
                "strict_geometry_supported": True,
                "raw_box_fresh_matched": True,
                "floor_projection_m": point.tolist(),
                "physical_identity_GT": None,
            }
        )
    for q in results["queries"]:
        assert len(q["reference_bank"]) <= 32
        assert all(features[fid]["frame"] < q["frame"] for fid in q["reference_bank"])
        for ids in q["other_banks"].values():
            assert len(ids) <= 32 and all(features[fid]["frame"] < q["frame"] for fid in ids)
    for _test, source in metadata.items():
        model = source[0]["models"]["artifacts"]["rfdetr_small"]
        assert model["status"] == "verified_copy"
        assert model["sha256"] == model["expected_sha256"] == results["model_sha256"]
    with (HERE / "gallery_memberships.json").open("x") as stream:
        json.dump(
            {
                "status": "all_selected_reference_memberships_fresh_strict_geometry_and_past_only",
                "memberships": checks,
                "query_bank_limit": 32,
                "future_samples_used": False,
                "outside_updates": False,
                "descriptor_role_note": "raw_features first-use role may be competitor; this separate geometry/freshness verification defines every reference-bank membership.",
                "actual_model_metadata_equal_and_verified": True,
                "role_is_target_hypothesis_not_named_identity": True,
            },
            stream,
            indent=2,
        )
        stream.write("\n")
    print(
        json.dumps(
            {
                "gallery_memberships": len(checks),
                "all_strict_fresh": True,
                "future_samples": 0,
                "outside_updates": 0,
                "NN": False,
            }
        )
    )


if __name__ == "__main__":
    main()
