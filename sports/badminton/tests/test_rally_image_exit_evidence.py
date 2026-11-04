"""Supported out-of-image flight may continue evidence, never invent a contact/start.

The image/trajectory helper is tested separately. These cases exercise the real
typed segmenter with its explicit support bit, independent of player movement.
"""

import pytest

from bai_badminton.components import _EvidenceRally
from bai_badminton.events.rally_evidence import EvidenceRallyFSM, ObservationKind, RallyObservation
from bai_badminton.events.rally_fsm import RallyParams, RallyState


def _observed(frame, speed=12.0):
    return RallyObservation(frame, ObservationKind.OBSERVED, speed, player_motion=False)


def _loss(frame, *, supported=True, motion=False, kind=ObservationKind.MISSING, **kwargs):
    return RallyObservation(
        frame,
        kind,
        player_motion=motion,
        exit_return_supported=supported,
        **kwargs,
    )


def _moving(provider=EvidenceRallyFSM, **options):
    fsm = provider(RallyParams(fps=30), **options)
    for frame in range(100):
        fsm.step_evidence(_observed(frame, None if frame == 0 else 12.0))
    assert fsm.state is RallyState.IN_PLAY
    assert fsm.start == 1
    assert fsm.serve is None
    return fsm


@pytest.mark.parametrize("gap_frames", [40, 53])
@pytest.mark.parametrize("motion", [False, True])
@pytest.mark.parametrize("provider", [EvidenceRallyFSM, _EvidenceRally])
def test_supported_exit_return_retains_one_exchange_without_observed_positions_or_contacts(
    gap_frames, motion, provider
):
    fsm = _moving(provider, use_exit_recovery=True, use_reconstruction=False, motion_guard=False)
    for frame in range(100, 100 + gap_frames):
        evidence = _loss(frame, motion=motion)
        update = fsm.step_evidence(evidence)
        assert evidence.kind is ObservationKind.MISSING
        assert evidence.speed is None
        assert update.started is None
        assert update.finalized is None
        assert fsm.state is RallyState.IN_PLAY
        assert fsm.serve is None
    for frame in range(100 + gap_frames, 230):
        fsm.step_evidence(_observed(frame, None if frame == 100 + gap_frames else 12.0))
    final = fsm.flush(229).finalized
    assert (final.start, final.end) == (1, 229)
    assert final.serve_frame is None


@pytest.mark.parametrize("mode", ["default_disabled", "explicit_disabled", "unsupported"])
def test_missing_without_qualifying_enabled_return_evidence_still_terminates(mode):
    options = {} if mode == "default_disabled" else {"use_exit_recovery": mode == "unsupported"}
    fsm = _moving(**options)
    finalized = []
    for frame in range(100, 150):
        update = fsm.step_evidence(_loss(frame, supported=mode != "unsupported", motion=True))
        if update.finalized:
            finalized.append(update.finalized)
    assert [(s.start, s.end, s.reason) for s in finalized] == [(1, 99, "gap")]
    assert fsm.state is RallyState.IDLE


@pytest.mark.parametrize("kind", [ObservationKind.MISSING, ObservationKind.RECONSTRUCTED])
def test_exit_cue_cannot_start_an_idle_exchange_or_claim_a_contact(kind):
    fsm = EvidenceRallyFSM(RallyParams(fps=30), use_exit_recovery=True)
    for frame in range(80):
        update = fsm.step_evidence(_loss(frame, kind=kind, motion=True))
        assert update.started is None
        assert update.finalized is None
        assert fsm.state is RallyState.IDLE
        assert fsm.serve is None


def test_supported_loss_can_cancel_a_retained_gap_end_candidate():
    fsm = _moving(use_exit_recovery=True)
    for frame in range(100, 110):
        fsm.step_evidence(_loss(frame, supported=False))
    assert fsm.state is RallyState.ENDING
    assert fsm.end_reason == "gap"
    update = fsm.step_evidence(_loss(110))
    assert update.started is None
    assert update.finalized is None
    assert fsm.state is RallyState.IN_PLAY
    assert fsm.start == 1


def test_supported_exit_return_reopens_only_a_retained_closed_gap():
    fsm = _moving(use_exit_recovery=True)
    for frame in range(100, 115):
        fsm.step_evidence(_loss(frame, supported=False))
    assert fsm.state is RallyState.CLOSED
    assert fsm.closed.reason == "gap"
    update = fsm.step_evidence(_loss(115))
    assert update.started is None
    assert update.finalized is None
    assert fsm.state is RallyState.IN_PLAY
    assert fsm.start == 1
    assert fsm.serve is None
    for frame in range(116, 145):
        fsm.step_evidence(_loss(frame))
    assert fsm.flush(144).finalized.start == 1


def test_exit_cue_does_not_reopen_a_closed_stationary_exchange():
    fsm = _moving(use_exit_recovery=True)
    for frame in range(100, 113):
        fsm.step_evidence(_observed(frame, 0.5))
    assert fsm.state is RallyState.CLOSED
    assert fsm.closed.reason == "stationary"
    finalized = []
    for frame in range(113, 145):
        update = fsm.step_evidence(_loss(frame))
        assert update.started is None
        assert fsm.state is not RallyState.IN_PLAY
        if update.finalized:
            finalized.append(update.finalized)
    assert len(finalized) == 1
    assert finalized[0].reason == "stationary"


def test_finalized_gap_cannot_be_reopened_by_a_late_exit_cue():
    fsm = _moving(use_exit_recovery=True)
    for frame in range(100, 130):
        fsm.step_evidence(_loss(frame, supported=False))
    assert fsm.state is RallyState.IDLE
    for frame in range(130, 170):
        update = fsm.step_evidence(_loss(frame))
        assert update.started is None
        assert update.finalized is None
        assert fsm.state is RallyState.IDLE


@pytest.mark.parametrize("barrier", ["context_invalid", "replay", "cut"])
def test_context_and_cut_barriers_override_supported_exit_return(barrier):
    fsm = _moving(use_exit_recovery=True)
    for frame in range(100, 110):
        fsm.step_evidence(_loss(frame))
    if barrier == "cut":
        update = fsm.on_discontinuity(110)
    else:
        update = fsm.step_evidence(_loss(110, context_valid=barrier != "context_invalid", replay=barrier == "replay"))
    assert update.finalized is not None
    assert update.finalized.reason == "cut"
    assert update.finalized.end < 110
    assert fsm.state is RallyState.IDLE
    for frame in range(111, 150):
        update = fsm.step_evidence(_loss(frame))
        assert update.started is None
        assert fsm.state is RallyState.IDLE


@pytest.mark.parametrize("enabled", [False, True])
def test_exit_option_and_evidence_survive_provider_checkpoint_and_reset(enabled):
    fsm = _moving(_EvidenceRally, use_exit_recovery=enabled, use_reconstruction=False, motion_guard=False)
    fsm.step_evidence(_loss(100))
    checkpoint = fsm.checkpoint()
    fsm.on_discontinuity(101)
    assert fsm.state is RallyState.IDLE
    fsm.restore(checkpoint)
    assert fsm.state is RallyState.IN_PLAY
    assert fsm.last_evidence.exit_return_supported is True
    assert fsm.use_exit_recovery is enabled
    fsm.reset()
    assert fsm.use_exit_recovery is enabled
    assert fsm.use_reconstruction is False
    assert fsm.motion_guard is False
    assert fsm.state is RallyState.IDLE
    assert fsm.last_evidence is None


@pytest.mark.parametrize("kind", [ObservationKind.OBSERVED, ObservationKind.INVALID])
def test_exit_return_support_is_rejected_on_nonmissing_observed_or_invalid_input(kind):
    with pytest.raises(ValueError):
        RallyObservation(0, kind, exit_return_supported=True)


@pytest.mark.parametrize("kind", [ObservationKind.MISSING, ObservationKind.RECONSTRUCTED])
def test_exit_return_support_is_allowed_only_as_explicit_missing_evidence(kind):
    observation = RallyObservation(0, kind, exit_return_supported=True)
    assert observation.exit_return_supported is True
    assert observation.speed is None


@pytest.mark.parametrize("value", [0, 1, None, "true"])
def test_exit_support_requires_a_strict_boolean(value):
    with pytest.raises(ValueError):
        RallyObservation(0, ObservationKind.MISSING, exit_return_supported=value)


@pytest.mark.parametrize("value", [0, 1, None, "true"])
def test_exit_recovery_option_requires_a_strict_boolean(value):
    with pytest.raises(ValueError):
        EvidenceRallyFSM(RallyParams(fps=30), use_exit_recovery=value)
