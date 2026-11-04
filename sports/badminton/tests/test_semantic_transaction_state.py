"""Custom stateful semantic providers must participate in scoring rollback."""
from threading import RLock

import pytest
from test_plugin_domain_composition import _session


class StatefulContact:
    def __init__(self):
        self.lock = RLock()
        self.count = 0
        self.closed = 0

    def __deepcopy__(self, memo):
        raise AssertionError('a model/runtime provider must not be deepcopied')

    def detect(self, window, **kwargs):
        self.count += 1
        return []

    def reset(self):
        self.count = 0

    def close(self):
        self.closed += 1


class TransactionalContact(StatefulContact):
    def checkpoint(self):
        return self.count

    def restore(self, checkpoint):
        self.count = checkpoint


def test_stateful_semantic_provider_without_restore_is_rejected_before_processing(tmp_path):
    provider = StatefulContact()
    with pytest.raises(ValueError, match='checkpoint.*restore'):
        _session(tmp_path, 'contact', provider, stateful=True)
    assert provider.closed == 1


def test_failed_score_transaction_restores_custom_semantic_state_without_copying_models(tmp_path):
    provider = TransactionalContact()
    plugin, store = _session(tmp_path, 'contact', provider, stateful=True)
    try:
        with pytest.raises(ValueError, match='controlled'):
            with plugin.engine._score_transaction():
                provider.count = 9
                raise ValueError('controlled score write failure')
        assert provider.count == 0
    finally:
        plugin.close()
        store.close()
