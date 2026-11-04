"""A domain-neutral host resolves typed, versioned, format-aware components."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import pytest

from bai_engine.config import ModelChoice, Profile


@runtime_checkable
class Counter(Protocol):
    def predict(self, values: list[int]) -> int: ...


@dataclass
class Context:
    offset: int = 0


class SumCounter:
    def __init__(self, offset=0):
        self.offset = offset
        self.resets = 0
        self.closes = 0

    def predict(self, values):
        return sum(values) + self.offset

    def reset(self):
        self.resets += 1

    def close(self):
        self.closes += 1


def _registry(factory=None, *, formats=frozenset({'one', 'many'}), version='1', stateful=True):
    from bai_engine.components import ComponentContract, ComponentRegistry

    registry = ComponentRegistry()
    contract = ComponentContract(
        kind='counter', implementation='sum', version=version,
        input_schema='integer-sequence:v1', output_schema='integer-count:v1',
        interface=Counter, context_type=Context, supported_formats=formats,
        failure_policy='unavailable', stateful=stateful,
    )
    registry.register(contract, factory or (lambda context, config: SumCounter(context.offset + config['offset'])))
    return registry, contract


def _create(registry, *, match_format='one', config=None, identity=None):
    return registry.create('counter', 'sum', context=Context(2),
                           configuration={'offset': 3} if config is None else config,
                           match_format=match_format, context_identity=identity or {'input': 'a' * 64})


def test_component_factory_is_replaceable_without_importing_a_sport():
    registry, contract = _registry()
    first = _create(registry)
    assert first.instance.predict([1, 2]) == 8
    assert first.contract == contract
    alternative, _ = _registry(lambda context, config: SumCounter(-10))
    assert _create(alternative).instance.predict([1, 2]) == -7


def test_stateful_instances_are_session_scoped_and_lifecycle_is_explicit():
    registry, _ = _registry()
    first, second = _create(registry), _create(registry)
    assert first.instance is not second.instance
    instance = first.instance
    first.reset()
    first.close()
    first.close()
    assert (instance.resets, instance.closes) == (1, 1)
    assert second.instance.closes == 0
    with pytest.raises(RuntimeError, match='closed'):
        first.reset()


def test_duplicate_registration_is_not_a_silent_replacement():
    registry, contract = _registry()
    with pytest.raises(ValueError, match='registered'):
        registry.register(contract, lambda context, config: SumCounter())


@pytest.mark.parametrize('match_format', ['one', 'many'])
def test_declared_formats_resolve_without_assuming_two_players(match_format):
    registry, _ = _registry()
    assert _create(registry, match_format=match_format).instance.predict([4]) == 9


def test_unknown_format_does_not_silently_select_a_single_format_component():
    registry, _ = _registry(formats=frozenset({'one'}))
    with pytest.raises(RuntimeError, match='format'):
        _create(registry, match_format='unknown')


def test_unknown_provider_does_not_fall_back_to_an_unrelated_model():
    registry, _ = _registry()
    with pytest.raises(RuntimeError, match='missing'):
        registry.create('counter', 'missing', context=Context(), configuration={}, match_format='one')


def test_factory_result_and_context_must_follow_the_declared_port():
    registry, _ = _registry(lambda context, config: object())
    with pytest.raises(RuntimeError, match='interface'):
        _create(registry)
    registry, _ = _registry()
    with pytest.raises(RuntimeError, match='context'):
        registry.create('counter', 'sum', context=object(), configuration={}, match_format='one')


def test_stateful_provider_must_supply_reset_and_close():
    class MissingLifecycle:
        def predict(self, values):
            return sum(values)

    registry, _ = _registry(lambda context, config: MissingLifecycle())
    with pytest.raises(RuntimeError, match='lifecycle'):
        _create(registry)


def test_fingerprint_records_component_config_format_and_input_identity():
    registry, _ = _registry()
    base = _create(registry).fingerprint
    assert base == _create(registry).fingerprint
    changed, _ = _registry(version='2')
    assert len({base, _create(changed).fingerprint,
                _create(registry, config={'offset': 4}).fingerprint,
                _create(registry, match_format='many').fingerprint,
                _create(registry, identity={'input': 'b' * 64}).fingerprint}) == 5


def test_configuration_is_snapshotted_and_nonfinite_values_are_rejected_before_build():
    def build(context, config):
        value = config['offset']
        config['offset'] = 999
        return SumCounter(value)

    registry, _ = _registry(build)
    config = {'offset': 3}
    assert _create(registry, config=config).instance.predict([1]) == 4
    assert config == {'offset': 3}
    with pytest.raises(ValueError, match='finite|JSON'):
        _create(registry, config={'offset': float('nan')})


@pytest.mark.parametrize('source', ['configuration', 'context_identity'])
@pytest.mark.parametrize('invalid', [float('inf'), {3: 'not-a-string-key'}, object()])
def test_nested_non_json_inputs_are_rejected_before_constructing_a_component(source, invalid):
    built = []

    def build(context, config):
        instance = SumCounter()
        built.append(instance)
        return instance

    registry, _ = _registry(build)
    arguments = {'configuration': {'offset': 3}, 'context_identity': {'input': 'a' * 64}}
    arguments[source] = {'nested': [invalid]}
    with pytest.raises(ValueError, match='finite|JSON'):
        registry.create('counter', 'sum', context=Context(), match_format='one', **arguments)
    assert built == []


def test_registration_metadata_cannot_change_capabilities_or_cache_identity():
    formats = {'one'}
    registry, contract = _registry(formats=formats)
    fingerprint = _create(registry).fingerprint
    formats.add('many')
    with pytest.raises(AttributeError):
        contract.version = 'changed-by-caller'
    with pytest.raises(RuntimeError, match='format'):
        _create(registry, match_format='many')
    assert _create(registry).fingerprint == fingerprint


def test_registry_description_is_data_not_a_factory_or_mutable_registration():
    registry, _ = _registry()
    descriptions = registry.describe()
    assert descriptions[0]['input_schema'] == 'integer-sequence:v1'
    assert descriptions[0]['output_schema'] == 'integer-count:v1'
    descriptions[0]['version'] = 'changed-by-caller'
    assert registry.describe()[0]['version'] == '1'


def test_another_analytics_profile_does_not_require_badminton_model_configuration():
    profile = Profile(name='integer-analytics', components={
        'counter': ModelChoice(model='sum', backend='none'),
    })
    assert profile.components['counter'].model == 'sum'
    assert profile.shuttle.model == profile.player_detector.model == profile.pose.model == profile.stroke.model == 'none'


def test_model_artifact_and_component_implementation_have_separate_configuration():
    choice = ModelChoice(model='weights_v2', backend='torch-cpu', implementation='counter_impl')
    assert choice.model == 'weights_v2'
    assert choice.implementation == 'counter_impl'
    assert ModelChoice(model='weights_v2', backend='torch-cpu').implementation is None
