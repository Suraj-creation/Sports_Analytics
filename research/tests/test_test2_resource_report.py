import pytest

from research.test2_resource_report import worker_gpu_memory


def test_gpu_memory_excludes_other_gpu_and_other_pid():
    rows = "GPU-a, 1, 100\nGPU-a, 2, 200\nGPU-b, 1, 300\n"
    assert worker_gpu_memory(rows, "GPU-a", 1) == 100
    assert worker_gpu_memory(rows, "GPU-b", 1) == 300
    assert worker_gpu_memory(rows, "GPU-a", 9) is None


def test_unavailable_gpu_measurement_stays_unknown():
    assert worker_gpu_memory("GPU-a, 1, N/A\n", "GPU-a", 1) is None


def test_unknown_gpu_sample_format_fails():
    with pytest.raises(ValueError):
        worker_gpu_memory("GPU-a, 1\n", "GPU-a", 1)
