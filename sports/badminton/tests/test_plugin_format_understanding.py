"""Unknown format retains four-person acquisition and truthful capabilities."""

from test_plugin_discipline import make_session

import pytest


@pytest.mark.parametrize("configured,capacity,known", [(None, 4, False), ("singles", 2, True), ("doubles", 4, True)])
def test_plugin_uses_an_explicit_unknown_state_without_forcing_a_singles_roster(tmp_path, configured, capacity, known):
    plugin = make_session(tmp_path, configured)
    try:
        assert plugin.perception.match_format == (configured or "unknown")
        assert plugin.perception.players.max_players == capacity
        assert plugin.engine.cfg.match_format_known is known
        decision = plugin.format_understanding.decision
        assert decision.match_format == (configured or "unknown")
        assert decision.source == ("configured" if configured else "unknown")
        public = plugin.public_state()
        assert public["format"]["match_format"] == (configured or "unknown")
        assert plugin.capabilities()["format"]["status"] == ("configured" if configured else "unknown")
    finally:
        plugin.close()


def test_cache_binds_selected_component_contracts_and_format_policy(tmp_path):
    plugin = make_session(tmp_path, "doubles")
    try:
        identity = plugin._isolation_id()
        assert identity["components"] == plugin.perception.component_metadata
        assert identity["format_understanding"]["method"] == "sustained_target_court_format_v1"
        assert identity["format_understanding"]["configured_format"] == "doubles"
    finally:
        plugin.close()
