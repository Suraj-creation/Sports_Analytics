"""Profiler interpretation and latency arithmetic do not require a GPU."""

import math

import pytest

from research.production_runtime_probe import placement_summary, summarize_latencies_ms


def kernel(name="conv", provider="CUDAExecutionProvider", duration=100, op="Conv", index=1, **extra):
    return {
        "cat": "Node",
        "ph": "X",
        "name": name + "_kernel_time",
        "dur": duration,
        "args": {"provider": provider, "op_name": op, "node_index": index, **extra},
    }


def test_counts_executed_kernels_once_and_keeps_cpu_shape_work_explicit():
    events = [
        kernel(),
        kernel(duration=80),
        kernel("shape", "CPUExecutionProvider", 4, "Shape", 2),
        {
            "cat": "Node",
            "ph": "X",
            "name": "conv_fence_before",
            "dur": 5,
            "args": {"provider": "CUDAExecutionProvider"},
        },
        {"cat": "Session", "ph": "X", "name": "model_run", "dur": 200, "args": {}},
    ]
    result = placement_summary(events)
    assert result["kernel_events"] == 3
    assert result["providers"]["CUDAExecutionProvider"]["unique_nodes"] == 1
    assert result["providers"]["CUDAExecutionProvider"]["kernel_events"] == 2
    assert result["providers"]["CUDAExecutionProvider"]["summed_kernel_duration_us"] == 180
    assert result["providers"]["CPUExecutionProvider"]["op_event_counts"] == {"Shape": 1}
    assert "wall_time_fraction" not in result["providers"]["CUDAExecutionProvider"]


def test_transfers_remain_distinct_from_compute_and_dtype_is_observed_metadata():
    result = placement_summary(
        [
            kernel("copy", duration=3, op="MemcpyFromHost", index=1),
            kernel(
                "conv",
                duration=11,
                index=2,
                input_type_shape=[{"float": [1, 3, 8, 8]}],
                output_type_shape=[{"float": [1, 4, 8, 8]}],
            ),
        ]
    )
    cuda = result["providers"]["CUDAExecutionProvider"]
    assert cuda["transfer_events"] == 1
    assert cuda["compute_events"] == 1
    assert result["observed_tensor_types"] == ["float"]


def test_unknown_provider_is_not_silently_called_cpu_or_cuda():
    result = placement_summary([kernel(provider="FutureExecutionProvider")])
    assert set(result["providers"]) == {"FutureExecutionProvider"}
    assert result["actual_cuda_kernel_events"] == 0


def test_missing_provider_is_counted_without_inventing_placement():
    event = kernel()
    del event["args"]["provider"]
    result = placement_summary([event])
    assert result["kernel_events_without_provider"] == 1
    assert not result["providers"]


def test_same_node_can_report_multiple_actual_providers():
    result = placement_summary([kernel(), kernel(provider="CPUExecutionProvider")])
    assert result["nodes_with_multiple_providers"] == ["1:conv_kernel_time:Conv"]


@pytest.mark.parametrize("duration", [-1, math.nan, math.inf, True])
def test_invalid_kernel_duration_fails_closed(duration):
    with pytest.raises(ValueError, match="duration"):
        placement_summary([kernel(duration=duration)])


def test_profile_without_kernel_execution_does_not_prove_gpu_usage():
    with pytest.raises(ValueError, match="kernel"):
        placement_summary([{"cat": "Session", "name": "model_run", "dur": 100}])


def test_dtype_metadata_may_be_string_encoded_without_becoming_a_precision_claim():
    result = placement_summary([kernel(input_type_shape='[{"float16": [1, 3, 8, 8]}]')])
    assert result["observed_tensor_types"] == ["float16"]
    assert (
        result["precision_limit"] == "Tensor metadata does not prove accumulator precision or hardware execution units."
    )


def test_empty_latency_samples_stay_unmeasured():
    assert summarize_latencies_ms([]) == {
        "count": 0,
        "mean": None,
        "median": None,
        "minimum": None,
        "maximum": None,
        "p95": None,
    }


def test_latency_statistics_keep_small_sample_p95_and_units_explicit():
    result = summarize_latencies_ms([10, 30, 20, 40, 50])
    assert result == {"count": 5, "mean": 30.0, "median": 30.0, "minimum": 10.0, "maximum": 50.0, "p95": 48.0}


@pytest.mark.parametrize("values", [[-1], [math.nan], [math.inf], [False]])
def test_invalid_latency_samples_are_rejected(values):
    with pytest.raises(ValueError, match="latency"):
        summarize_latencies_ms(values)
