"""Offline packaging must bind a decision trace to its own complete observations."""

import importlib
import json
from pathlib import Path

import msgpack
import pytest

from scripts.benchmarking.evaluate_rallies import read_csv, save_evaluation, write_predictions
from scripts.benchmarking.production_inference import digest


@pytest.fixture
def packager():
    # Import through sys.modules so the preserved pre-fix source can run these
    # same black-box regressions in the separately recorded red evidence run.
    return importlib.import_module("research.build_failure_cases")


@pytest.fixture
def fixture_run(tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    cache = run / "runtime/sessions/Synthetic/perception"
    cache.mkdir(parents=True)
    cache_path = cache / "000000_000059.msgpack"
    cache_path.write_bytes(msgpack.packb({"frames": [{"f": i, "s": None, "c": 0} for i in range(60)]}))
    labels = tmp_path / "labels.csv"
    write_predictions(labels, [(20, 40)], 30)
    metadata = {
        "video_fps": 30,
        "frame_count": 60,
        "ground_truth_path": str(labels),
        "ground_truth_sha256": digest(labels),
        "source_video_sha256": "1" * 64,
    }
    (run / "benchmark_metadata.json").write_text(json.dumps(metadata))
    (run / "events.jsonl").write_text("")
    (run / "execution.log").write_text("Synthetic software-contract fixture; no sporting-accuracy label.\n")
    replay = run / "replay"
    replay.mkdir()
    trace = replay / "fsm_trace.jsonl"

    def configure(predictions=((20, 40, "gap"),), finalizations=None):
        for filename in ("predicted_rallies.csv", "rally_comparison.csv", "metrics.json", "metrics.md"):
            (run / filename).unlink(missing_ok=True)
        write_predictions(run / "predicted_rallies.csv", [(start, end) for start, end, _ in predictions], 30)
        save_evaluation(run, read_csv(labels, 30), read_csv(run / "predicted_rallies.csv", 30), 30)
        (run / "inference.json").write_text(
            json.dumps(
                {
                    "rally_events": [
                        {"start": start, "end": end, "end_reason": reason} for start, end, reason in predictions
                    ],
                    "media": {"width": 1280, "height": 720, "source_width": 1920, "source_height": 1080},
                }
            )
        )
        rows = predictions if finalizations is None else finalizations
        trace.write_text(
            "".join(
                json.dumps({"frame": 50, "update": {"finalized": {"start": start, "end": end, "reason": reason}}})
                + "\n"
                for start, end, reason in rows
            )
        )
        (replay / "replay_metadata.json").write_text(
            json.dumps(
                {
                    "video_sha256": metadata["source_video_sha256"],
                    "cache_sha256": {path.name: digest(path) for path in cache.glob("*.msgpack")},
                    "trace_sha256": digest(trace),
                }
            )
        )

    configure()
    return {"run": run, "cache": cache, "cache_path": cache_path, "trace": trace, "configure": configure}


def package(packager, fixture_run, tmp_path, **kwargs):
    output = tmp_path / "package"
    packager.build(output, fixture_run["trace"], run=fixture_run["run"], **kwargs)
    return output


def test_new_run_packages_own_trace_and_complete_cache(packager, fixture_run, tmp_path):
    output = package(packager, fixture_run, tmp_path)
    index = json.loads((output / "index.json").read_text())
    assert index["case_count"] == 1
    provenance = index["evidence_provenance"]
    assert provenance["cache_trace_hash_binding_verified"] is True
    assert provenance["end_reason_and_multiplicity_verified"] is True
    assert provenance["trace_finalization_count"] == provenance["prediction_count"] == 1
    assert provenance["observation_cache_file_count"] == 1
    snapshot = output / "executed_build_failure_cases.py"
    assert snapshot.read_bytes() == Path(packager.__file__).read_bytes()
    assert provenance["packager_source_sha256"] == digest(snapshot)
    assert provenance["packager_source_snapshot"] == str(snapshot)


def test_same_ranges_from_another_cache_are_rejected(packager, fixture_run, tmp_path):
    other = tmp_path / "other/perception"
    other.mkdir(parents=True)
    data = msgpack.unpackb(fixture_run["cache_path"].read_bytes(), raw=False)
    data["frames"][25]["s"] = [123, 456]
    (other / fixture_run["cache_path"].name).write_bytes(msgpack.packb(data))
    with pytest.raises(ValueError, match="cache SHA256"):
        package(packager, fixture_run, tmp_path, cache_source=other)
    assert not (tmp_path / "package").exists()


def test_extra_unused_cache_file_cannot_hide_behind_full_frame_coverage(packager, fixture_run, tmp_path):
    (fixture_run["cache"] / "empty_extra.msgpack").write_bytes(msgpack.packb({"frames": []}))
    with pytest.raises(ValueError, match="cache SHA256"):
        package(packager, fixture_run, tmp_path)


def test_trace_with_same_final_intervals_but_different_bytes_is_rejected(packager, fixture_run, tmp_path):
    with fixture_run["trace"].open("a") as stream:
        stream.write('{"frame":51,"update":{}}\n')
    with pytest.raises(ValueError, match="trace SHA256"):
        package(packager, fixture_run, tmp_path)


def test_duplicate_finalization_is_not_silently_deduplicated(packager, fixture_run, tmp_path):
    fixture_run["configure"](finalizations=[(20, 40, "gap"), (20, 40, "gap")])
    with pytest.raises(ValueError, match="multiplicity"):
        package(packager, fixture_run, tmp_path)


def test_exact_duplicate_lists_preserve_multiplicity_in_evidence(packager, fixture_run, tmp_path):
    fixture_run["configure"](predictions=[(20, 40, "gap"), (20, 40, "gap")])
    output = package(packager, fixture_run, tmp_path)
    evidence = json.loads((output / "index.json").read_text())["evidence_provenance"]
    assert evidence["trace_finalization_count"] == evidence["prediction_count"] == 2


def test_changed_end_reason_cannot_pass_same_range_parity(packager, fixture_run, tmp_path):
    fixture_run["configure"](finalizations=[(20, 40, "stationary")])
    with pytest.raises(ValueError, match="end-reason"):
        package(packager, fixture_run, tmp_path)


def test_nonbaseline_requires_replay_metadata(packager, fixture_run, tmp_path):
    fixture_run["trace"].with_name("replay_metadata.json").unlink()
    with pytest.raises(ValueError, match=r"replay_metadata\.json"):
        package(packager, fixture_run, tmp_path)


def test_wrong_video_binding_is_rejected_even_when_cache_and_intervals_match(packager, fixture_run, tmp_path):
    path = fixture_run["trace"].with_name("replay_metadata.json")
    value = json.loads(path.read_text())
    value["video_sha256"] = "2" * 64
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="different source video"):
        package(packager, fixture_run, tmp_path)


def test_duplicate_source_frame_cannot_be_overwritten_in_cache_fold(packager, fixture_run, tmp_path):
    data = msgpack.unpackb(fixture_run["cache_path"].read_bytes(), raw=False)
    data["frames"].append(data["frames"][25])
    fixture_run["cache_path"].write_bytes(msgpack.packb(data))
    fixture_run["configure"]()
    with pytest.raises(ValueError, match="duplicate source frame"):
        package(packager, fixture_run, tmp_path)


def test_half_open_touching_neighbors_are_not_tagged_as_fragments(packager, fixture_run, tmp_path):
    fixture_run["configure"](predictions=[(10, 20, "gap"), (20, 40, "gap"), (40, 50, "gap")])
    output = package(packager, fixture_run, tmp_path)
    case = json.loads((output / "gt_01/case.json").read_text())
    assert "multiple_segments" not in case["tags"]


def test_positive_overlap_fragments_still_receive_tag(packager, fixture_run, tmp_path):
    fixture_run["configure"](predictions=[(20, 28, "gap"), (32, 40, "gap")])
    output = package(packager, fixture_run, tmp_path)
    case = json.loads((output / "gt_01/case.json").read_text())
    assert "multiple_segments" in case["tags"]


def test_historical_baseline_fallback_is_explicit_and_not_claimed_as_hash_proof(
    packager, fixture_run, tmp_path, monkeypatch
):
    fixture_run["trace"].with_name("replay_metadata.json").unlink()
    monkeypatch.setattr(packager, "BASELINE", fixture_run["run"])
    # Historical outputs are still forbidden below the baseline root.
    output = package(packager, fixture_run, tmp_path)
    evidence = json.loads((output / "index.json").read_text())["evidence_provenance"]
    assert evidence["trace_binding_policy"] == "historical_frozen_baseline_interval_only_compatibility"
    assert evidence["cache_trace_hash_binding_verified"] is False
    assert evidence["end_reason_and_multiplicity_verified"] is False


def test_nonbaseline_never_silently_selects_baseline_trace(packager, fixture_run):
    with pytest.raises(ValueError, match="--trace is required"):
        packager.resolve_inputs(fixture_run["run"])
