"""Leases fence duplicate executors and fail closed on unavailable process evidence."""

from pathlib import Path
from unittest.mock import patch

import pytest

from research.production_resource_guard import compute_pids, gpu_lease, gpu_uuid

UUID = "GPU-1234abcd-5678-abcd-1234-abcd56781234"


def test_process_evidence_filters_by_physical_uuid_and_deduplicates():
    rows = f"{UUID},42\nGPU-other,17\n{UUID},42\n{UUID},18\n"
    assert compute_pids(rows, UUID) == [18, 42]
    assert compute_pids("", UUID) == []


@pytest.mark.parametrize("rows", ["unknown", f"{UUID},N/A", f"{UUID},true"])
def test_unknown_process_evidence_is_not_an_idle_gpu(rows):
    with pytest.raises(ValueError):
        compute_pids(rows, UUID)


def test_second_executor_is_rejected_and_exception_releases_lease(tmp_path):
    with patch("research.production_resource_guard.subprocess.check_output", return_value=""):
        with gpu_lease(tmp_path, UUID), pytest.raises(RuntimeError, match="lease"), gpu_lease(tmp_path, UUID):
            pytest.fail("duplicate executor entered")
        with pytest.raises(ValueError), gpu_lease(tmp_path, UUID):
            raise ValueError("interrupted job")
        with gpu_lease(tmp_path, UUID):
            pass


def test_existing_compute_job_is_preserved_and_blocks_new_executor(tmp_path):
    with (
        patch("research.production_resource_guard.subprocess.check_output", return_value=f"{UUID},777\n"),
        pytest.raises(RuntimeError, match="777"),
        gpu_lease(tmp_path, UUID),
    ):
        pytest.fail("job started on occupied GPU")
    with (
        patch("research.production_resource_guard.subprocess.check_output", return_value=""),
        gpu_lease(tmp_path, UUID),
    ):
        pass


def test_unknown_uuid_does_not_create_lock_path(tmp_path):
    with pytest.raises(ValueError), gpu_lease(tmp_path, "GPU-../../bad"):
        pass
    assert not list(Path(tmp_path).iterdir())


def test_physical_index_is_resolved_to_single_verified_uuid():
    with patch("research.production_resource_guard.subprocess.check_output", return_value=UUID + "\n"):
        assert gpu_uuid(1) == UUID
    with (
        patch("research.production_resource_guard.subprocess.check_output", return_value="N/A"),
        pytest.raises(RuntimeError),
    ):
        gpu_uuid(1)
