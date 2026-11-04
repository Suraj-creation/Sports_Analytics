"""The geometry repair stays explicit and follows effective contact selection."""

import pytest
import test_plugin_discipline as fixtures

from bai_engine.config import ModelChoice


def _profile(monkeypatch, *, legacy=None, selected=None):
    changes = {"contact": legacy}
    if selected is not None:
        changes["components"] = {"contact": selected}
    monkeypatch.setattr(fixtures, "PROFILE", fixtures.PROFILE.model_copy(update=changes))


def _choice(params):
    return ModelChoice(model="contact_fusion_v1", backend="opencv-cpu", params=params)


def test_participant_geometry_is_disabled_by_default(tmp_path, monkeypatch):
    _profile(monkeypatch)
    plugin = fixtures.make_session(tmp_path, "singles")
    try:
        assert plugin.engine.cfg.participant_geometry_policy is None
    finally:
        plugin.close()


def test_explicit_contact_geometry_configuration_reaches_engine(tmp_path, monkeypatch):
    _profile(monkeypatch, legacy=_choice({"participant_geometry": {}}))
    plugin = fixtures.make_session(tmp_path, "doubles")
    try:
        assert plugin.engine.cfg.participant_geometry_policy.max_span_s == 0.2
    finally:
        plugin.close()


def test_component_contact_override_controls_geometry_instead_of_legacy_choice(tmp_path, monkeypatch):
    _profile(
        monkeypatch,
        legacy=_choice({"participant_geometry": {"max_span_s": 0.2}}),
        selected=_choice({"participant_geometry": {"max_span_s": 0.1}}),
    )
    plugin = fixtures.make_session(tmp_path, "doubles")
    try:
        assert plugin.engine.cfg.participant_geometry_policy.max_span_s == 0.1
    finally:
        plugin.close()


@pytest.mark.parametrize("bad", [[], {"unexpected": 1}, {"max_span_s": "invalid"}])
def test_invalid_participant_geometry_configuration_fails_clearly(tmp_path, monkeypatch, bad):
    _profile(monkeypatch, selected=_choice({"participant_geometry": bad}))
    with pytest.raises(ValueError, match="participant_geometry"):
        fixtures.make_session(tmp_path, "doubles")
