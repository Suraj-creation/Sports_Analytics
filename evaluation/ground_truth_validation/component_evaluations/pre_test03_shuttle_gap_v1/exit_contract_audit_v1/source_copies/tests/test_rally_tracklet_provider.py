import numpy as np
import pytest

from bai_badminton.components import _EvidenceRally, _TrackletEvidenceRally
from bai_badminton.events.rally_evidence import ObservationKind, RallyObservation
from bai_badminton.events.rally_fsm import RallyParams, RallyState
from bai_badminton.events.rally_motion import image_exit_return_supported
from bai_badminton.observations import WindowObs
from bai_badminton.perception.shuttle_post import Track


def window(*, singleton=True):
    x, y = np.full(35, np.nan), np.full(35, np.nan)
    visible = np.zeros(35, bool)
    for frame in range(5):
        x[frame], y[frame], visible[frame] = 500 + frame, 60 - frame * 8, True
    for frame in range(25, 30):
        x[frame], y[frame], visible[frame] = 530 + frame - 25, 28 + (frame - 25) * 8, True
    if singleton:
        x[15], y[15], visible[15] = 740, 450, True
    return WindowObs(0, 30, Track.from_arrays(x, y, visible), {})


def proof(provider, w, index=10):
    return provider.exit_return_support(w, index, frame_height=720, raw_xy=lambda frame, xy: xy)


@pytest.mark.parametrize("start,qualified", [(0, True), (45, True), (46, False), (100, False), (None, False)])
def test_new_association_qualifies_at_loss_not_later_decision(start, qualified):
    w = window()
    w.frame0 = 100
    provider = _TrackletEvidenceRally(RallyParams(fps=30))
    provider.start = start
    provider.state = RallyState.IN_PLAY if start is not None else RallyState.IDLE
    for index in (10, 20, 24):
        value = proof(provider, w, index)
        assert value.supported is qualified
        assert value.gap_start == 105
        assert provider.last_exit_support_frame == 100 + index


def test_original_v2_cue_can_still_support_provisional_event():
    w = window(singleton=False)
    w.frame0 = 100
    provider = _TrackletEvidenceRally(RallyParams(fps=30))
    provider.start, provider.state = 103, RallyState.IN_PLAY
    assert proof(provider, w).supported
    assert image_exit_return_supported(w, 10, frame_height=720)


def test_new_association_does_not_create_idle_start_or_fabricated_observation():
    w = window()
    w.frame0 = 100
    provider = _TrackletEvidenceRally(RallyParams(fps=30), use_reconstruction=False, use_exit_recovery=True)
    support = proof(provider, w)
    assert not support.supported
    event = RallyObservation(110, ObservationKind.MISSING, exit_return_supported=support.supported)
    assert provider.step_evidence(event).started is None
    assert event.speed is None and provider.state is RallyState.IDLE
    assert w.shuttle.vis[15]


def test_support_and_options_survive_checkpoint_and_reset_without_private_window_state():
    w = window()
    w.frame0 = 100
    provider = _TrackletEvidenceRally(RallyParams(fps=30), use_reconstruction=False, use_exit_recovery=True)
    provider.start, provider.state = 1, RallyState.IN_PLAY
    value = proof(provider, w)
    saved = provider.checkpoint()
    provider.reset()
    assert provider.last_exit_support is None
    provider.restore(saved)
    assert provider.last_exit_support == value
    assert provider.use_exit_recovery and not provider.use_reconstruction
    provider.close()
    assert provider.last_exit_support is None


def test_legacy_evidence_provider_has_no_new_association_capability():
    from bai_badminton.components import AssociatedExitRallySegmentation

    assert not isinstance(_EvidenceRally(RallyParams(fps=30)), AssociatedExitRallySegmentation)
    assert isinstance(_TrackletEvidenceRally(RallyParams(fps=30)), AssociatedExitRallySegmentation)


@pytest.mark.parametrize("enabled", [True, False])
def test_curve_choice_is_explicit_and_survives_provider_lifecycle(enabled):
    provider = _TrackletEvidenceRally(
        RallyParams(fps=25),
        use_curve_exit=enabled,
        use_reconstruction=False,
        use_exit_recovery=True,
    )
    checkpoint = provider.checkpoint()
    provider.reset()
    assert provider.use_curve_exit is enabled
    provider.restore(checkpoint)
    assert provider.use_curve_exit is enabled
    provider.close()


def test_selected_contact_and_independent_attribution_have_distinct_provenance(tmp_path, monkeypatch):
    import bai_badminton.engine as module
    from bai_badminton.events.contact import CONTACT_MODEL, CONTACT_RELIABILITY_MODEL, ContactCandidate
    from bai_badminton.testing.synth import make_rally
    from bai_engine.store import EventStore

    observed = make_rally(n_shots=3).obs
    with EventStore(tmp_path / "events.sqlite", "test") as store:
        engine = module.BadmintonMatchEngine(
            "test", module.EngineConfig(fps=30, frame_width=1280, frame_height=720), store
        )
        engine._participant_frames = [{}] * observed.n
        monkeypatch.setattr(
            module, "participant_contact_evidence", lambda *args, **kwargs: {"components": {"redirect": 1}}
        )
        candidate = ContactCandidate(10, None, 0.6, model=CONTACT_RELIABILITY_MODEL)
        engine._on_contact(candidate, observed)
        event = store.query(types=["contact"])[0]
        assert event.payload["contact_method"] == CONTACT_RELIABILITY_MODEL
        assert event.payload["participant_hypothesis"]["components_model"] == CONTACT_MODEL
        engine.close()
