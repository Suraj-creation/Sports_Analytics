"""Named hypotheses, participant episodes and team trackers share an explicit provider."""
from test_plugin_domain_composition import _run, _session

from bai_badminton.identity import IdentityResolver
from bai_badminton.participation import ParticipantTracker
from bai_badminton.teams import DoublesTeamTracker
from bai_engine.schema import Provenance


class ControlledIdentity:
    def __init__(self):
        self.named_calls = self.participant_calls = self.team_calls = 0

    def named_resolver(self):
        self.named_calls += 1
        return IdentityResolver(frame_height=720., rebind_gap_frames=60)

    def participant_tracker(self, instance_id):
        self.participant_calls += 1
        return ParticipantTracker(720., fps=30., instance_id=instance_id)

    def team_tracker(self):
        self.team_calls += 1
        return DoublesTeamTracker(30.)


def test_selected_identity_provider_constructs_actual_engine_state(tmp_path):
    provider = ControlledIdentity()
    plugin, store = _session(tmp_path, 'identity', provider)
    try:
        _run(plugin)
        assert provider.named_calls == provider.team_calls == 1
        assert provider.participant_calls >= 1
        assert plugin.capabilities()['identity']['active_implementation'] == 'controlled'
        assert plugin._isolation_id()['domain_components']['identity']['contract']['implementation'] == 'controlled'
    finally:
        plugin.close()
        store.close()


def test_format_boundary_recreates_identity_through_the_same_selected_provider(tmp_path):
    provider = ControlledIdentity()
    plugin, store = _session(tmp_path, 'identity', provider)
    try:
        plugin.engine.set_match_format('doubles', 0, Provenance(model='test-format'))
        assert provider.named_calls == provider.team_calls == 2
        assert plugin.engine._multi_person_identity_ambiguous
    finally:
        plugin.close()
        store.close()
