"""Exercise existing recovery, not a new algorithm or physical-GT evaluator.

Counterfactual fixtures retain actual G69 coordinates but explicitly change
availability of selected lower observations. Those fixtures are synthetic;
the unmodified six-point case is the actual recorded provider input.
"""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from bai_badminton.components import AssociatedExitRallySegmentation, _TrackletEvidenceRally
from bai_badminton.events.rally_fsm import RallyParams, RallyState
from bai_badminton.events.rally_motion import image_exit_return_supported, image_exit_return_tracklet_support
from bai_badminton.observations import WindowObs
from bai_badminton.perception.shuttle_post import Track

SOURCE = Path(__file__).resolve().parent.parent / "attempt_v1/cache_window.json"
START = 27312


def window(lower_count=6):
    rows = json.loads(SOURCE.read_text())
    x, y, visible, confidence = np.full(64, np.nan), np.full(64, np.nan), np.zeros(64, bool), np.zeros(64)
    for row in rows:
        index = row["f"] - START
        if row["s"] is not None:
            x[index], y[index], visible[index], confidence[index] = *row["s"], True, row["c"]
    if lower_count != 6:
        # Synthetic availability counterfactual only. The original preserved
        # cache, raw coordinates/support and source annotations never change.
        visible[27348 + lower_count - START : 27354 - START] = False
    return WindowObs(START, 30, Track.from_arrays(x, y, visible, confidence), {})


def provider(start=26654):
    value = _TrackletEvidenceRally(
        RallyParams(fps=30), use_reconstruction=False, use_exit_recovery=True, use_curve_exit=False
    )
    value.start, value.state = start, RallyState.IN_PLAY if start is not None else RallyState.IDLE
    assert isinstance(value, AssociatedExitRallySegmentation)
    return value


def proof(value, observed, frame=27335):
    return value.exit_return_support(observed, frame - START, frame_height=720, raw_xy=lambda _frame, xy: xy)


def shortened(observed, stop):
    length = stop - START
    track = observed.shuttle
    return replace(
        observed,
        shuttle=Track(
            track.x[:length], track.y[:length], track.vis[:length], track.conf[:length], track.interp[:length]
        ),
        replay=np.zeros(length, bool),
        break_before=np.zeros(length, bool),
        pose_stride=None,
    )


def test_recorded_six_contiguous_lower_samples_intentionally_do_not_become_singleton():
    observed = window()
    original = [a.copy() for a in (observed.shuttle.x, observed.shuttle.y, observed.shuttle.vis, observed.shuttle.conf)]
    assert not image_exit_return_supported(observed, 27335 - START, frame_height=720)
    value = proof(provider(), observed)
    assert not value.supported and value.reason == "exactly_one_isolated_alternative_required"
    assert value.ignored_frame is None
    for actual, expected in zip(
        (observed.shuttle.x, observed.shuttle.y, observed.shuttle.vis, observed.shuttle.conf), original, strict=True
    ):
        np.testing.assert_equal(actual, expected)


def test_existing_selected_provider_already_recovers_one_isolated_lower_hypothesis():
    observed = window(lower_count=1)
    assert not image_exit_return_supported(observed, 27335 - START, frame_height=720)
    value = proof(provider(), observed)
    assert value.supported and value.basis == "single_unassociated_observation"
    assert (value.gap_start, value.gap_end, value.ignored_frame) == (27326, 27354, 27348)
    assert value.before_frames == tuple(range(27321, 27326))
    assert value.after_frames == tuple(range(27354, 27359))
    # Internal alternative association is not deletion/relabeling of the input.
    assert observed.shuttle.vis[27348 - START]
    np.testing.assert_allclose(observed.shuttle.x[27348 - START], 784.9683248617133, atol=0.0)


def test_missing_future_is_recomputed_without_sticky_negative_cache():
    observed = window(lower_count=1)
    selected = provider()
    first = proof(selected, shortened(observed, 27354))
    assert not first.supported
    later = proof(selected, observed)
    assert later.supported
    assert selected.last_exit_support == later
    assert selected.last_exit_support_frame == 27335


def test_current_lower_observation_is_never_marked_missing_by_exit_proof():
    observed = window(lower_count=1)
    value = proof(provider(), observed, frame=27348)
    assert not value.supported and value.reason == "current_sample_is_observed_or_invalid"
    assert observed.shuttle.vis[27348 - START]


@pytest.mark.parametrize("lower_count", [2, 3, 6])
def test_multiple_contiguous_lower_observations_are_not_silently_discarded(lower_count):
    value = proof(provider(), window(lower_count))
    assert not value.supported and value.ignored_frame is None


@pytest.mark.parametrize("start", [None, 27300])
def test_missingness_cannot_earn_idle_or_late_event_qualification(start):
    value = proof(provider(start), window(lower_count=1))
    assert not value.supported and value.reason == "event_not_qualified_before_loss"


@pytest.mark.parametrize("alteration", ["cut", "replay", "no_upper", "estimated_upper", "wrong_exit_direction"])
def test_existing_source_temporal_and_observed_bracket_controls_remain_negative(alteration):
    observed = window(lower_count=1)
    if alteration == "cut":
        observed.break_before[27340 - START] = True
    elif alteration == "replay":
        observed.replay[27335 - START] = True
    elif alteration == "no_upper":
        observed.shuttle.vis[27354 - START :] = False
    elif alteration == "estimated_upper":
        observed.shuttle.interp[27354 - START :] = True
    else:
        observed.shuttle.y[27321 - START : 27326 - START] = [28, 38, 48, 58, 68]
    assert not proof(provider(), observed).supported


def test_pure_tracklet_contract_matches_selected_provider_for_qualified_case():
    observed = window(lower_count=1)
    expected = image_exit_return_tracklet_support(observed, 27335 - START, frame_height=720)
    assert proof(provider(), observed) == expected
