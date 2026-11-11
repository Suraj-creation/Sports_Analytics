"""Appearance availability must retain the actual loader failure across formats."""

from types import SimpleNamespace

import pytest

from bai_engine.config import ModelChoice


@pytest.mark.parametrize("match_format", ["singles", "doubles", "unknown"])
@pytest.mark.parametrize("reason", ["pinned checkpoint is not downloaded", "CUDA initialization failed"])
def test_loader_failure_is_not_replaced_by_current_format(tmp_path, match_format, reason):
    from test_plugin_discipline import make_session

    value = make_session(tmp_path, "singles")
    value.perception.match_format = match_format
    value.perception.profile = value.perception.profile.model_copy(
        update={"player_reid": ModelChoice(model="osnet_ain_x0_25", backend="torch-cuda")}
    )
    value.perception.effective_choices["player_reid"] = value.perception.profile.player_reid
    value.perception.degraded = [SimpleNamespace(stage="player_identity", reason=reason)]
    capability = value.capabilities()["player_identity"]
    assert capability["status"] == "unavailable"
    assert capability["reason"] == reason
    assert capability["active_model"] is None


def test_explicit_singles_provider_failure_keeps_its_reason(tmp_path):
    from test_plugin_discipline import make_session

    value = make_session(tmp_path, "singles")
    value.perception.profile = value.perception.profile.model_copy(deep=True)
    value.perception.profile.components["player_reid"] = ModelChoice(
        model="osnet_ain_x0_25", backend="torch-cpu", implementation="osnet-appearance-v1"
    )
    value.perception.effective_choices["player_reid"] = value.perception.profile.components["player_reid"]
    value.perception.degraded = [SimpleNamespace(stage="player_identity", reason="checkpoint not cached")]
    capability = value.capabilities()["player_identity"]
    assert capability["status"] == "unavailable"
    assert capability["requested_model"] == "osnet_ain_x0_25"
    assert capability["reason"] == "checkpoint not cached"


def test_disabled_identity_does_not_claim_a_missing_model_or_format_limitation(tmp_path):
    from test_plugin_discipline import make_session

    value = make_session(tmp_path, "singles")
    capability = value.capabilities()["player_identity"]
    assert capability["status"] == "disabled"
    assert capability["reason"] == ""


def test_loaded_appearance_does_not_assert_named_identity(tmp_path):
    from test_plugin_discipline import make_session

    value = make_session(tmp_path, "singles")
    value.perception.models["player_reid"] = "osnet_ain_x0_25@1"
    assert value.capabilities()["player_identity"]["status"] == "loaded"
    assert value.capabilities()["named_identity"]["status"] == "review_required"
