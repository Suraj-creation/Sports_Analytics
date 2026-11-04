"""Pure safety-boundary tests; these do not open Redis or launch a process."""

import pytest

from research import validate_redis_runtime as harness
from research.validate_redis_runtime import Report, ValidationRuntimeError, fresh_output, validate_redis_url


def test_redis_harness_requires_explicit_private_service_confirmation():
    with pytest.raises(ValidationRuntimeError, match="confirm-private"):
        validate_redis_url("redis://127.0.0.1:16379/0", confirmed_private=False)


@pytest.mark.parametrize("url", [
    "redis://127.0.0.1/0", "redis://127.0.0.1:6379/0", "redis://remote.example:16379/0",
    "https://127.0.0.1:16379/0", "redis://127.0.0.1:16379/0?socket_timeout=0",
    "redis://127.0.0.1:16379/not-a-database", "redis://127.0.0.1:0/0",
])
def test_redis_harness_rejects_ambiguous_or_shared_endpoints(url):
    with pytest.raises(ValidationRuntimeError):
        validate_redis_url(url, confirmed_private=True)


def test_redis_harness_endpoint_metadata_does_not_expose_credentials():
    metadata = validate_redis_url("redis://fixture-user:fixture-password@127.0.0.1:16379/4", confirmed_private=True)
    assert metadata == {"scheme": "redis", "host": "127.0.0.1", "port": 16379, "database": 4}


def test_redis_harness_default_port_override_still_requires_private_confirmation():
    with pytest.raises(ValidationRuntimeError, match="confirm-private"):
        validate_redis_url("redis://127.0.0.1:6379/0", confirmed_private=False, allow_default_port=True)
    metadata = validate_redis_url("redis://127.0.0.1:6379/0", confirmed_private=True, allow_default_port=True)
    assert metadata["port"] == 6379


def test_redis_harness_preserves_existing_output(tmp_path):
    output = tmp_path / "existing"
    output.mkdir()
    evidence = output / "report.json"
    evidence.write_text("existing evidence", encoding="utf-8")
    with pytest.raises(ValidationRuntimeError, match="must be new"):
        fresh_output(output)
    assert evidence.read_text(encoding="utf-8") == "existing evidence"


def test_redis_harness_creates_only_the_requested_new_directory(tmp_path):
    output = tmp_path / "new"
    assert fresh_output(output) == output.resolve()
    assert list(output.iterdir()) == []


@pytest.mark.parametrize("protected", ["models", "data"])
def test_redis_harness_does_not_create_outputs_inside_application_assets(tmp_path, monkeypatch, protected):
    monkeypatch.setattr(harness, "REPO", tmp_path)
    output = tmp_path / protected / "new"
    with pytest.raises(ValidationRuntimeError, match="must not be inside"):
        fresh_output(output)
    assert not output.exists()


def test_redis_harness_error_report_redacts_endpoint_password(tmp_path):
    url = "redis://fixture-user:fixture-password@127.0.0.1:16379/0"
    report = Report(tmp_path, {"host": "127.0.0.1", "port": 16379}, 30, url)
    with pytest.raises(RuntimeError), report.stage("controlled_failure"):
        raise RuntimeError(f"Connection {url} failed with fixture-password")
    saved = (tmp_path / "report.json").read_text(encoding="utf-8")
    assert "fixture-password" not in saved
    assert "redacted" in saved
