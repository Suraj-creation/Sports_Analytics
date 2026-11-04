"""Rally state uses observed motion and cannot merge evidence across a cut."""

from bai_badminton.events.rally_fsm import RallyFSM, RallyParams, RallyState


def _playing() -> RallyFSM:
    fsm = RallyFSM(RallyParams(fps=30))
    assert fsm.on_contact(0).started == 0
    for frame in range(70):
        assert fsm.step(frame, True, 12.0).finalized is None
    assert fsm.state is RallyState.IN_PLAY
    return fsm


def test_cut_finalizes_previous_exchange_before_a_new_contact() -> None:
    fsm = _playing()
    update = fsm.on_discontinuity(70)
    assert update.finalized is not None
    assert (update.finalized.start, update.finalized.end, update.finalized.reason) == (0, 69, "cut")
    assert fsm.state is RallyState.IDLE
    assert fsm.on_contact(70).started == 70
    assert fsm.start == 70  # a nearby contact cannot merge back across the cut


def test_cut_does_not_extend_an_already_tentative_end() -> None:
    fsm = _playing()
    for frame in range(70, 77):
        fsm.step(frame, True, 0.0)
    assert fsm.state is RallyState.ENDING
    tentative_end = fsm.tentative_end
    update = fsm.on_discontinuity(77)
    assert update.finalized is not None
    assert update.finalized.end == tentative_end
    assert update.finalized.end < 77
    assert update.finalized.reason == "cut"


def test_cut_finalizes_closed_exchange_instead_of_reopening_it() -> None:
    fsm = _playing()
    for frame in range(70, 85):
        fsm.step(frame, False, 0.0)
    assert fsm.state is RallyState.CLOSED
    update = fsm.on_discontinuity(85)
    assert update.finalized is not None
    assert (update.finalized.start, update.finalized.end, update.finalized.reason) == (0, 69, "gap")
    assert fsm.on_contact(85).started == 85
    assert fsm.start == 85


def test_cut_discards_previous_scenes_stationary_history() -> None:
    fsm = _playing()
    for frame in range(70, 76):
        fsm.step(frame, True, 0.0)
    assert fsm.state is RallyState.IN_PLAY
    fsm.on_discontinuity(76)
    assert fsm.on_contact(76).started == 76
    fsm.step(76, True, 0.0)
    assert fsm.state is RallyState.IN_PLAY
    assert fsm.tentative_end is None


def test_repeated_replay_frames_cannot_supply_stationary_history() -> None:
    fsm = _playing()
    first = fsm.step(70, True, 0.0, replay=True)
    assert first.finalized is not None
    assert (first.finalized.end, first.finalized.reason) == (69, "cut")
    for frame in range(71, 85):
        assert fsm.step(frame, True, 0.0, replay=True).finalized is None
    assert fsm.on_contact(85).started == 85
    fsm.step(85, True, 0.0)
    assert fsm.state is RallyState.IN_PLAY
    assert fsm.tentative_end is None


def test_short_observation_gap_keeps_existing_exchange() -> None:
    fsm = _playing()
    for frame in range(70, 75):
        assert fsm.step(frame, False, 0.0).finalized is None
    for frame in range(75, 91):
        assert fsm.step(frame, True, 12.0).finalized is None
    assert fsm.state is RallyState.IN_PLAY
    assert fsm.start == 0


def test_unobserved_positions_with_motion_cannot_keep_exchange_alive() -> None:
    fsm = _playing()
    finalized = []
    # The caller may have reconstructed locations, but must pass visible=False
    # when no independent shuttle observation exists.
    for frame in range(70, 120):
        update = fsm.step(frame, False, 12.0)
        if update.finalized is not None:
            finalized.append(update.finalized)
    assert [(segment.start, segment.end, segment.reason) for segment in finalized] == [(0, 69, "gap")]
    assert fsm.state is RallyState.IDLE


def test_unobserved_motion_cannot_start_an_exchange() -> None:
    fsm = RallyFSM(RallyParams(fps=30))
    for frame in range(60):
        assert fsm.step(frame, False, 12.0).started is None
    assert fsm.state is RallyState.IDLE
