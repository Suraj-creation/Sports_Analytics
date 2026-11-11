from types import SimpleNamespace

import pytest

from research.pipeline_repair_performance import observe_perception_rates, summarize_stage_samples


def test_quantiles_are_per_invocation_and_stage_scopes_are_separate():
    result = summarize_stage_samples(
        {"ocr": [{"seconds": 1.0, "frames": 60}, {"seconds": 3.0, "frames": 60}], "empty": []}
    )
    assert result["ocr"]["calls"] == 2
    assert result["ocr"]["seconds"] == 4
    assert result["ocr"]["p50_ms"] == 2000
    assert result["ocr"]["p95_ms"] == pytest.approx(2900)
    assert result["ocr"]["frame_population_sum"] == 120
    assert "empty" not in result


def test_observation_preserves_original_call_population_and_timing():
    stats = SimpleNamespace(seconds={})
    calls = []

    def original(stage, n, began):
        calls.append((stage, n, began))
        stats.seconds[stage] = stats.seconds.get(stage, 0.0) + began

    perception = SimpleNamespace(stats=stats, _rate=original)
    samples = {}
    observe_perception_rates(perception, samples)
    perception._rate("court", 16, 0.5)
    perception._rate("court", 60, 1.5)
    assert calls == [("court", 16, 0.5), ("court", 60, 1.5)]
    assert stats.seconds == {"court": 2.0}
    assert samples["court"] == [{"seconds": 0.5, "frames": 16}, {"seconds": 1.5, "frames": 60}]


@pytest.mark.parametrize("seconds", [-1, float("inf"), float("nan")])
def test_invalid_time_is_not_reported_as_performance(seconds):
    with pytest.raises(ValueError, match="wall seconds"):
        summarize_stage_samples({"bad": [{"seconds": seconds, "frames": 1}]})
