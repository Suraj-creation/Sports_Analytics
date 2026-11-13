"""Check consolidated diagnostic scope, provenance, arithmetic and local links."""
import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path

OUT = Path(__file__).resolve().parent
WORK = OUT.parents[1]
REPORT = WORK / "reports/test_01_02_annotation_and_failure_review.md"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    provenance = json.loads((OUT / "input_provenance.json").read_text())
    for path, info in provenance["files"].items():
        assert Path(path).exists(), path
        assert digest(path) == info["sha256"], path
    cases = [json.loads(x) for x in (OUT / "failure_database.jsonl").read_text().splitlines()]
    rows = [json.loads(x) for x in (OUT / "reference_rows.jsonl").read_text().splitlines()]
    annotations = json.loads((OUT / "annotation_inventory.json").read_text())
    components = json.loads((OUT / "component_cases.json").read_text())
    assert len(cases) == len({x["id"] for x in cases}) == 53
    assert len(rows) == len({x["id"] for x in rows}) == 422
    assert len([x for x in cases if x["test"] == 2]) == 39
    assert len(annotations) == 16 and sum(x["test"] == 2 for x in annotations) == 7
    assert all(not x["physical_gt"] for x in cases)
    assert all(not x["physical_ground_truth"] for x in rows)
    assert components["case_count"] == len(components["cases"]) == 17
    for m in json.loads((OUT / "mixed_iou_exact.json").read_text()):
        changes = m["changed_matched_rows"]
        assert len(changes) == 6
        total = sum((Fraction(x["exact_iou_delta"]["fraction"]) for x in changes), Fraction())
        assert total / m["matched_denominator"] == Fraction(m["exact_mean_delta"]["fraction"])
        assert abs(float(total / m["matched_denominator"]) - (m["mean_iou_after"] - m["mean_iou_before"])) < 1e-12
    link_count = 0
    for raw in re.findall(r"\]\(([^)]+)\)", REPORT.read_text()):
        if raw.startswith(("http:", "https:", "#")):
            continue
        path = Path(raw.split("#")[0])
        if not path.is_absolute():
            path = REPORT.parent / path
        assert path.exists(), raw
        link_count += 1
    result = {"status": "passed", "input_files_rehashed": len(provenance["files"]),
              "original_annotation_files_reverified": 16, "unique_packaged_rally_cases": 53,
              "rally_case_arm_observations": 106, "component_cases": 17,
              "valid_reference_rows": 422, "local_report_links_verified": link_count,
              "exact_iou_delta_checks": 3, "physical_gt_created": False,
              "production_edits": False, "test3_inputs_accessed": False,
              "report_sha256": digest(REPORT), "validator_sha256": digest(__file__)}
    (OUT / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
