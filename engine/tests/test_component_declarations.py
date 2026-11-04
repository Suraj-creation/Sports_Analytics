"""Provider evidence/device/lifecycle declarations are immutable cache inputs."""
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import pytest

from bai_engine.components import ComponentContract, ComponentRegistry


@runtime_checkable
class Port(Protocol):
    def run(self): ...


@dataclass
class Context:
    value: int = 1


class Instance:
    def run(self):
        return 1


def _contract(declaration):
    return ComponentContract(
        kind='sensor', implementation='declared', version='1', input_schema='pixels:v1', output_schema='signal:v1',
        interface=Port, context_type=Context, supported_formats=frozenset({'video'}), failure_policy='unknown',
        declaration=declaration,
    )


def test_declaration_is_a_detached_deeply_immutable_snapshot():
    source = {'devices': ['cpu'], 'evidence': {'required': ['pixels']}, 'state_restore': 'stateless'}
    contract = _contract(source)
    source['devices'].append('cuda')
    source['evidence']['required'].append('invented')
    assert contract.describe()['declaration'] == {
        'devices': ['cpu'], 'evidence': {'required': ['pixels']}, 'state_restore': 'stateless',
    }
    with pytest.raises(TypeError):
        contract.declaration['devices'] = ['changed']
    with pytest.raises(TypeError):
        contract.declaration['evidence']['required'][0] = 'changed'
    public = contract.describe()
    public['declaration']['devices'].append('mutated')
    assert contract.describe()['declaration']['devices'] == ['cpu']


@pytest.mark.parametrize('bad', [{'devices': float('nan')}, {'evidence': {1: 'invalid-key'}}, {'model': object()}])
def test_non_json_declarations_are_rejected_without_exposing_values(bad):
    with pytest.raises(ValueError, match='declaration'):
        _contract(bad)


def test_provider_declarations_participate_in_component_cache_identity():
    fingerprints = []
    for device in ('cpu', 'cuda'):
        registry = ComponentRegistry()
        registry.register(_contract({'devices': [device]}), lambda context, config: Instance())
        handle = registry.create('sensor', 'declared', context=Context(), configuration={}, match_format='video')
        fingerprints.append(handle.fingerprint)
    assert fingerprints[0] != fingerprints[1]


def test_legacy_contract_metadata_is_explicitly_undeclared_instead_of_baseline_claims():
    contract = ComponentContract(
        kind='legacy', implementation='custom', version='1', input_schema='x:v1', output_schema='y:v1',
        interface=Port, context_type=Context, supported_formats=frozenset({'video'}), failure_policy='unknown',
    )
    assert contract.describe()['declaration'] == {}


@pytest.mark.parametrize('failure', ['interface', 'lifecycle', 'cleanup'])
def test_rejected_factory_results_release_resources_without_masking_port_failure(failure):
    from dataclasses import replace

    closed = []

    class Invalid:
        def close(self):
            closed.append(True)
            if failure == 'cleanup':
                raise ValueError('secondary close failure')

    class MissingReset(Invalid):
        def run(self):
            return 1

    registry = ComponentRegistry()
    contract = replace(_contract({}), stateful=failure == 'lifecycle')
    registry.register(contract, lambda context, config: MissingReset() if failure == 'lifecycle' else Invalid())
    with pytest.raises(RuntimeError, match='interface|lifecycle'):
        registry.create('sensor', 'declared', context=Context(), configuration={}, match_format='video')
    assert closed == [True]


def test_versioning_a_declared_contract_preserves_its_frozen_metadata():
    from dataclasses import replace

    original = _contract({'devices': ['cpu'], 'evidence': {'required': ['pixels']}})
    updated = replace(original, version='2')
    assert updated.version == '2'
    assert updated.describe()['declaration'] == original.describe()['declaration']


def test_closing_handle_releases_its_own_reference_to_a_stateless_model():
    import weakref

    registry = ComponentRegistry()
    registry.register(_contract({}), lambda context, config: Instance())
    handle = registry.create('sensor', 'declared', context=Context(), configuration={}, match_format='video')
    reference = weakref.ref(handle.instance)
    handle.close()
    assert reference() is None
