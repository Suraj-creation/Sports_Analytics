"""Actual typed rally providers: supporting evidence never becomes observation.

The temporal contract is actor-neutral and serves singles/four-player doubles;
these controlled cases do not claim unannotated doubles-video accuracy.
"""

import math
from dataclasses import asdict

import pytest

from bai_badminton.components import EvidenceRallySegmentation, RallySegmentation, _EvidenceRally, _Rally
from bai_badminton.events.rally_evidence import EvidenceRallyFSM, ObservationKind, RallyObservation
from bai_badminton.events.rally_fsm import RallyFSM, RallyParams, RallyState


def _observation(frame, *, kind=ObservationKind.OBSERVED, speed=12.0, motion=False, **kwargs):
    return RallyObservation(frame, kind, speed, player_motion=motion, **kwargs)


def _active(provider=EvidenceRallyFSM, **flags):
    fsm = provider(RallyParams(fps=30), **flags)
    assert fsm.on_contact(0).started == 0
    for frame in range(80):
        fsm.step_evidence(_observation(frame))
    assert fsm.state is RallyState.IN_PLAY
    return fsm


@pytest.mark.parametrize("provider", [EvidenceRallyFSM, _EvidenceRally])
def test_reconstructed_interior_gap_continues_but_does_not_fabricate_contacts(provider):
    fsm = provider(RallyParams(fps=30))
    for frame in range(100):
        fsm.step_evidence(_observation(frame, speed=None if frame == 0 else 12.0))
    assert fsm.start == 1
    for frame in range(100, 125):
        update = fsm.step_evidence(
            _observation(
                frame,
                kind=ObservationKind.RECONSTRUCTED,
                speed=None,
                shuttle_support=0.35,
                continuation_supported=True,
            )
        )
        assert update.started is None
        assert update.finalized is None
        assert fsm.state is RallyState.IN_PLAY
        assert fsm.serve is None
    for frame in range(125, 220):
        fsm.step_evidence(_observation(frame, speed=None if frame == 125 else 12.0))
    final = fsm.flush(219).finalized
    assert (final.start, final.end) == (1, 219)
    assert final.serve_frame is None


@pytest.mark.parametrize("kind", [ObservationKind.RECONSTRUCTED, ObservationKind.MISSING])
def test_player_motion_and_estimates_cannot_start_an_idle_exchange(kind):
    fsm = EvidenceRallyFSM(RallyParams(fps=30), motion_guard=True)
    for frame in range(80):
        update = fsm.step_evidence(
            _observation(
                frame,
                kind=kind,
                speed=None,
                motion=True,
                continuation_supported=kind is ObservationKind.RECONSTRUCTED,
            )
        )
        assert update.started is None
        assert update.finalized is None
    assert fsm.state is RallyState.IDLE
    assert fsm.serve is None


@pytest.mark.parametrize("motion_guard", [False, True])
@pytest.mark.parametrize("kind", [ObservationKind.MISSING, ObservationKind.RECONSTRUCTED])
def test_unsupported_missing_or_reconstructed_gap_still_ends_even_if_players_move(motion_guard, kind):
    fsm = _active(motion_guard=motion_guard)
    finalized = []
    for frame in range(80, 120):
        update = fsm.step_evidence(_observation(frame, kind=kind, speed=None, motion=True))
        if update.finalized:
            finalized.append(update.finalized)
    assert [(segment.start, segment.end, segment.reason) for segment in finalized] == [(0, 79, "gap")]
    assert fsm.state is RallyState.IDLE


@pytest.mark.parametrize(
    "observation",
    [
        _observation(80, kind=ObservationKind.INVALID, speed=None, motion=True),
        _observation(80, context_valid=False, motion=True),
        _observation(80, replay=True, motion=True),
    ],
)
def test_invalid_context_and_replay_are_cut_barriers(observation):
    fsm = _active(motion_guard=True)
    update = fsm.step_evidence(observation)
    assert update.finalized is not None
    assert (update.finalized.start, update.finalized.end, update.finalized.reason) == (0, 79, "cut")
    assert fsm.state is RallyState.IDLE
    for frame in range(81, 110):
        update = fsm.step_evidence(
            _observation(
                frame,
                kind=ObservationKind.RECONSTRUCTED,
                speed=None,
                motion=True,
                continuation_supported=True,
            )
        )
        assert update.started is None
        assert fsm.state is RallyState.IDLE


@pytest.mark.parametrize("motion_guard", [False, True])
def test_stationary_players_do_not_end_a_moving_observed_shuttle(motion_guard):
    fsm = _active(motion_guard=motion_guard)
    for frame in range(80, 180):
        update = fsm.step_evidence(_observation(frame, motion=False))
        assert update.finalized is None
        assert fsm.state is RallyState.IN_PLAY
    assert fsm.flush(179).finalized.end == 179


@pytest.mark.parametrize("motion_guard", [False, True])
def test_player_motion_guards_stationarity_only_when_explicitly_enabled(motion_guard):
    fsm = _active(motion_guard=motion_guard)
    for frame in range(80, 87):
        fsm.step_evidence(_observation(frame, speed=0.5, motion=True))
    assert fsm.state is (RallyState.IN_PLAY if motion_guard else RallyState.ENDING)


def test_stationary_evidence_ends_after_aligned_motion_support_expires():
    fsm = _active(motion_guard=True)
    for frame in range(80, 110):
        fsm.step_evidence(_observation(frame, speed=0.5, motion=True))
        assert fsm.state is RallyState.IN_PLAY
    first_candidate = None
    for frame in range(110, 125):
        fsm.step_evidence(_observation(frame, speed=0.5, motion=False))
        if fsm.state is RallyState.ENDING:
            first_candidate = frame
            break
    assert first_candidate == 119
    assert fsm.end_reason == "stationary"


@pytest.mark.parametrize("motion", [False, None])
def test_fresh_observed_rest_is_not_disabled_by_absent_motion_support(motion):
    fsm = _active(motion_guard=True)
    for frame in range(80, 87):
        fsm.step_evidence(_observation(frame, speed=0.5, motion=motion))
    assert fsm.state is RallyState.ENDING
    assert fsm.end_reason == "stationary"


def test_disabled_support_flags_match_the_corrected_legacy_fsm_step_for_step():
    legacy = RallyFSM(RallyParams(fps=30))
    rich = EvidenceRallyFSM(RallyParams(fps=30), use_reconstruction=False, motion_guard=False)
    for frame in range(260):
        if frame in [0, 170]:
            assert asdict(legacy.on_contact(frame)) == asdict(rich.on_contact(frame))
        if frame == 220:
            assert asdict(legacy.on_discontinuity(frame)) == asdict(rich.on_discontinuity(frame))
        kind = ObservationKind.RECONSTRUCTED if 100 <= frame < 125 else ObservationKind.OBSERVED
        speed = 0.5 if 180 <= frame < 215 else 12.0
        observation = _observation(
            frame,
            kind=kind,
            speed=speed if kind is ObservationKind.OBSERVED else None,
            motion=True,
            continuation_supported=kind is ObservationKind.RECONSTRUCTED,
        )
        expected = legacy.step(
            frame, kind is ObservationKind.OBSERVED, observation.speed if observation.speed is not None else math.nan
        )
        actual = rich.step_evidence(observation)
        assert asdict(actual) == asdict(expected)
        assert (rich.state, rich.start, rich.tentative_end) == (legacy.state, legacy.start, legacy.tentative_end)
    assert asdict(rich.flush(259)) == asdict(legacy.flush(259))


@pytest.mark.parametrize(
    "use_reconstruction,motion_guard", [(True, False), (False, True), (True, True), (False, False)]
)
def test_actual_provider_checkpoint_reset_and_optional_flags(use_reconstruction, motion_guard):
    fsm = _active(_EvidenceRally, use_reconstruction=use_reconstruction, motion_guard=motion_guard)
    assert isinstance(fsm, EvidenceRallySegmentation)
    assert isinstance(fsm, RallySegmentation)
    checkpoint = fsm.checkpoint()
    fsm.step_evidence(_observation(80, kind=ObservationKind.INVALID, speed=None))
    assert fsm.state is RallyState.IDLE
    fsm.restore(checkpoint)
    assert fsm.state is RallyState.IN_PLAY
    assert fsm.last_evidence.frame == 79
    fsm.reset()
    assert fsm.use_reconstruction is use_reconstruction
    assert fsm.motion_guard is motion_guard
    assert fsm.state is RallyState.IDLE
    assert fsm.last_evidence is None
    assert not isinstance(_Rally(RallyParams(fps=30)), EvidenceRallySegmentation)


@pytest.mark.parametrize("speed", [-1.0, math.nan, math.inf, -math.inf, True, "fast"])
def test_invalid_observed_speed_is_rejected(speed):
    with pytest.raises(ValueError):
        RallyObservation(0, ObservationKind.OBSERVED, speed)


@pytest.mark.parametrize("speed", [0, 1, 1.5, None])
def test_finite_nonnegative_or_unavailable_speed_is_preserved(speed):
    observation = RallyObservation(0, ObservationKind.OBSERVED, speed)
    assert observation.speed == speed


@pytest.mark.parametrize("kind", ["observed", "missing", None, 1])
def test_observation_kind_must_be_the_declared_enum(kind):
    with pytest.raises(ValueError):
        RallyObservation(0, kind)


@pytest.mark.parametrize("kind", [ObservationKind.RECONSTRUCTED, ObservationKind.MISSING, ObservationKind.INVALID])
def test_nonobserved_evidence_cannot_claim_measured_speed(kind):
    with pytest.raises(ValueError):
        RallyObservation(0, kind, 12.0)


@pytest.mark.parametrize("frame", [-1, 0.5, True])
def test_invalid_canonical_frame_is_rejected(frame):
    with pytest.raises(ValueError):
        RallyObservation(frame, ObservationKind.OBSERVED)


@pytest.mark.parametrize("support", [math.nan, math.inf])
def test_nonfinite_shuttle_support_is_rejected(support):
    with pytest.raises(ValueError):
        RallyObservation(0, ObservationKind.OBSERVED, shuttle_support=support)


@pytest.mark.parametrize("kind", [ObservationKind.OBSERVED, ObservationKind.MISSING, ObservationKind.INVALID])
def test_only_reconstructed_samples_can_claim_continuation_support(kind):
    with pytest.raises(ValueError):
        RallyObservation(0, kind, continuation_supported=True)


@pytest.mark.parametrize("support", [0, 1, None, "true"])
def test_continuation_support_must_be_an_explicit_boolean(support):
    with pytest.raises(ValueError):
        RallyObservation(0, ObservationKind.RECONSTRUCTED, continuation_supported=support)


def test_reconstruction_is_not_continuation_support_by_default():
    observation = RallyObservation(0, ObservationKind.RECONSTRUCTED)
    assert observation.continuation_supported is False
