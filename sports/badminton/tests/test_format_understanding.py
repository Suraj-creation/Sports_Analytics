"""Format inference uses sustained fresh target-court evidence, not a default.

These are component policy regressions. They establish no real-video accuracy.
"""

from dataclasses import replace
from importlib import import_module

import pytest


def _api():
    return import_module("bai_badminton.format_understanding")


def _model(*, configured=None, fps=30.0, **policy):
    api = _api()
    return api.SustainedCourtFormat(
        fps=fps,
        configured_format=configured,
        policy=api.FormatPolicy(min_observations=3, min_duration_s=1.0, max_gap_s=0.6, **policy),
    )


def _observation(frame, counts=(1, 1), *, full=True, epoch="target-a", **overrides):
    api = _api()
    persons = tuple(
        api.FormatPerson(
            episode_id=f"{side}-{index}",
            court_xy=(-1.0 + 2.0 * index, -3.0 if side == "near" else 3.0),
            detector_matched=True,
        )
        for side, count in zip(("near", "far"), counts, strict=True)
        for index in range(count)
    )
    values = dict(
        frame_idx=frame,
        persons=persons,
        detector_observed=True,
        main_view=True,
        geometry_valid=True,
        full_court_visible=full,
        epoch=epoch,
        cut=False,
    )
    values.update(overrides)
    return api.FormatObservation(**values)


def _sustain(model, *, counts=(1, 1), start=0, **kwargs):
    return [model.observe(_observation(frame, counts, **kwargs)) for frame in (start, start + 15, start + 30)]


def test_unconfigured_format_starts_unknown_and_never_defaults_to_singles():
    model = _model()
    assert model.decision.match_format == "unknown"
    assert model.decision.source == "unknown"
    assert model.decision.reason == "insufficient_evidence"


@pytest.mark.parametrize("counts,expected", [((1, 1), "singles"), ((2, 2), "doubles")])
def test_sustained_complete_target_court_evidence_infers_format(counts, expected):
    decisions = _sustain(_model(), counts=counts)
    assert [value.match_format for value in decisions] == ["unknown", "unknown", expected]
    assert decisions[-1].source == "inferred"
    assert decisions[-1].observed_frames == (0, 15, 30)
    assert decisions[-1].to_public()["method"] == "sustained_target_court_format_v1"
    assert "probability" not in decisions[-1].to_public()


def test_two_visible_people_without_full_court_observability_remain_unknown():
    model = _model()
    assert _sustain(model, full=False)[-1].match_format == "unknown"
    assert model.decision.reason == "incomplete_court_visibility"


def test_four_target_court_people_can_support_doubles_without_claiming_complete_visibility():
    assert _sustain(_model(), counts=(2, 2), full=False)[-1].match_format == "doubles"


@pytest.mark.parametrize("counts", [(0, 0), (1, 0), (2, 0), (2, 1), (3, 1), (3, 2), (2, 3)])
def test_incomplete_or_inconsistent_sides_do_not_force_a_format(counts):
    assert _sustain(_model(), counts=counts)[-1].match_format == "unknown"


@pytest.mark.parametrize(
    "overrides",
    [
        {"detector_observed": False},
        {"detector_observed": None},
        {"main_view": False},
        {"geometry_valid": False},
    ],
)
def test_skipped_unknown_non_main_and_unverified_frames_do_not_supply_evidence(overrides):
    model = _model()
    assert _sustain(model, counts=(2, 2), **overrides)[-1].match_format == "unknown"
    assert model.decision.observed_frames == ()


def test_carried_individuals_are_not_fresh_even_when_frame_detector_ran():
    model = _model()
    for frame in (0, 15, 30):
        observation = _observation(frame, (2, 2))
        observation = replace(
            observation, persons=tuple(replace(person, detector_matched=False) for person in observation.persons)
        )
        model.observe(observation)
    assert model.decision.match_format == "unknown"


def test_adjacent_court_people_are_excluded_before_format_counts():
    api = _api()
    model = _model()
    for frame in (0, 15, 30):
        observation = _observation(frame)
        extras = (
            api.FormatPerson("adjacent-near", (7.0, -3.0), True),
            api.FormatPerson("adjacent-far", (7.0, 3.0), True),
        )
        model.observe(replace(observation, persons=observation.persons + extras))
    assert model.decision.match_format == "singles"
    assert model.decision.side_counts == (1, 1)


def test_nonfinite_or_duplicate_episode_observations_do_not_support_a_format():
    api = _api()
    for persons in (
        (api.FormatPerson("same", (-1.0, -3.0), True), api.FormatPerson("same", (1.0, 3.0), True)),
        (api.FormatPerson("near", (float("nan"), -3.0), True), api.FormatPerson("far", (1.0, 3.0), True)),
    ):
        model = _model()
        for frame in (0, 15, 30):
            model.observe(replace(_observation(frame), persons=persons))
        assert model.decision.match_format == "unknown"


def test_observation_count_does_not_replace_sustained_video_time():
    model = _model()
    for frame in (0, 1, 2, 3, 4):
        model.observe(_observation(frame, (2, 2)))
    assert model.decision.match_format == "unknown"


def test_long_gap_breaks_unconfirmed_evidence_instead_of_counting_across_a_cut():
    model = _model()
    model.observe(_observation(0, (2, 2)))
    model.observe(_observation(15, (2, 2)))
    assert model.observe(_observation(60, (2, 2))).match_format == "unknown"
    assert model.decision.observed_frames == (60,)


def test_cut_breaks_candidate_but_does_not_erase_confirmed_doubles():
    model = _model()
    model.observe(_observation(0, (2, 2)))
    model.observe(_observation(15, (2, 2)))
    assert model.observe(_observation(30, (2, 2), cut=True)).match_format == "unknown"
    assert _sustain(model, counts=(2, 2), start=45)[-1].match_format == "doubles"
    assert model.observe(_observation(90, (1, 1), cut=True)).match_format == "doubles"


def test_confirmed_doubles_survives_occlusion_and_never_downgrades_to_singles():
    model = _model()
    _sustain(model, counts=(2, 2))
    for frame, counts in ((45, (1, 1)), (60, (0, 1)), (75, (1, 1)), (90, (1, 1)), (105, (1, 1))):
        assert model.observe(_observation(frame, counts)).match_format == "doubles"


def test_inferred_singles_can_upgrade_on_sustained_four_person_evidence():
    model = _model()
    _sustain(model)
    upgraded = _sustain(model, counts=(2, 2), start=45)[-1]
    assert upgraded.match_format == "doubles"
    assert upgraded.revision == 2


@pytest.mark.parametrize("configured,counts", [("singles", (2, 2)), ("doubles", (1, 1))])
def test_explicit_format_is_authoritative_and_exposes_conflicting_observation(configured, counts):
    model = _model(configured=configured)
    assert model.decision.match_format == configured and model.decision.source == "configured"
    decision = _sustain(model, counts=counts)[-1]
    assert decision.match_format == configured
    assert decision.source == "configured"
    assert decision.reason == "configured_format_conflict"


def test_epoch_change_resets_inferred_format_but_not_an_explicit_override():
    inferred, configured = _model(), _model(configured="doubles")
    _sustain(inferred, counts=(2, 2))
    assert inferred.observe(_observation(45, epoch="target-b", full=False)).match_format == "unknown"
    assert configured.observe(_observation(0, epoch="target-b", full=False)).match_format == "doubles"


def test_reset_clears_observations_and_restores_configured_or_unknown_state():
    for configured in (None, "singles", "doubles"):
        model = _model(configured=configured)
        _sustain(model, counts=(2, 2))
        model.reset()
        assert model.decision.match_format == (configured or "unknown")
        assert model.decision.observed_frames == ()
        model.observe(_observation(0))


def test_decision_json_and_cache_identity_are_detached_and_bind_policy_fps_and_format():
    model = _model()
    initial = model.cache_identity
    _sustain(model, counts=(2, 2))
    public = model.decision.to_public()
    public["observed_frames"].append(999)
    assert model.decision.observed_frames == (0, 15, 30)
    assert initial != model.cache_identity
    assert _model(fps=25.0).cache_identity != _model(fps=30.0).cache_identity
    assert _model(configured="singles").cache_identity != _model(configured="doubles").cache_identity


@pytest.mark.parametrize("fps", [0.0, -1.0, float("nan"), float("inf")])
def test_invalid_timeline_is_rejected(fps):
    with pytest.raises(ValueError, match="fps"):
        _model(fps=fps)


@pytest.mark.parametrize("configured", ["auto", "mixed", "", "unknown"])
def test_invalid_configured_format_is_rejected(configured):
    with pytest.raises(ValueError, match="configured"):
        _model(configured=configured)


def test_repeated_or_backward_frames_do_not_count_as_new_evidence():
    model = _model()
    model.observe(_observation(15, (2, 2)))
    for frame in (15, 14):
        with pytest.raises(ValueError, match="frame"):
            model.observe(_observation(frame, (2, 2)))


def test_close_is_idempotent_and_prevents_observation_or_reset():
    model = _model()
    model.close()
    model.close()
    with pytest.raises(RuntimeError, match="closed"):
        model.observe(_observation(0))
    with pytest.raises(RuntimeError, match="closed"):
        model.reset()


def test_format_understanding_is_a_registered_replaceable_component():
    from bai_engine.components import ComponentContract, ComponentRegistry

    api = _api()
    registry = ComponentRegistry()
    api.register_format_components(registry)
    context = api.FormatContext(fps=30.0, configured_format=None)
    handle = registry.create("format", "sustained-court-v1", context=context, configuration={}, match_format="unknown")
    assert isinstance(handle.instance, api.FormatUnderstanding)
    assert handle.instance.decision.match_format == "unknown"

    class Fixed:
        decision = api.FormatDecision(match_format="doubles", source="configured", reason="test", revision=0)

        def observe(self, observation):
            return self.decision

        def reset(self):
            pass

        def close(self):
            pass

    registry.register(
        ComponentContract(
            kind="format",
            implementation="controlled",
            version="1",
            input_schema="format-observation:v1",
            output_schema="format-decision:v1",
            interface=api.FormatUnderstanding,
            context_type=api.FormatContext,
            supported_formats=frozenset({"singles", "doubles", "unknown"}),
            failure_policy="unknown",
            stateful=True,
        ),
        lambda context, config: Fixed(),
    )
    alternative = registry.create("format", "controlled", context=context, configuration={}, match_format="unknown")
    assert alternative.instance.observe(_observation(0)).match_format == "doubles"
