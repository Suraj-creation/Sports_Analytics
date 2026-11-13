"""Contract reproduction only: expected RED on preserved dacc05e production.

No production code is changed. Raw missing association remains missing; the
independent temporal window must retain bounded *reconstructed* provenance.
"""
import numpy as np
import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.contact import detect_contacts
from bai_badminton.events.rally_motion import trajectory_continuation_supported
from bai_badminton.perception.association import ShuttleObservationEvidence
from bai_badminton.perception.shuttle_post import Track, process
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.rules import MatchConfig
from bai_engine.store import EventStore


def frames(*, typed=True, missing_status="missing"):
    result = []
    for i in range(25):
        absent = 9 <= i <= 12
        raw = None if absent and missing_status != "ambiguous" else (100.0+i*10, 300.0)
        status = missing_status if absent else "observed"
        association = "rejected" if status in {"ambiguous", "invalid"} else "unknown" if absent else "tracked"
        support = .9 if raw else 0.0
        result.append(FramePerception(
            i, raw, support,
            shuttle_observation=ShuttleObservationEvidence(
                i, 0, status, association, raw, raw if status == "observed" else None, support,
            ) if typed else None,
        ))
    return result


def window(tmp_path, discipline, **kwargs):
    store = EventStore(tmp_path/"events.sqlite", "PROVENANCE")
    engine = BadmintonMatchEngine("PROVENANCE", EngineConfig(
        fps=30, frame_width=1280, frame_height=720, match=MatchConfig(discipline=discipline)), store)
    sequence = frames(**kwargs)
    engine.ingest(ChunkPerception(0, 24, sequence))
    return engine._window(0, 24), sequence


@pytest.mark.parametrize("discipline", ["singles", "doubles"])
def test_modern_raw_missing_keeps_independent_reconstructed_temporal_context(tmp_path, discipline):
    current, original = window(tmp_path, discipline)
    # This exact bounded gap has coherent moving observed brackets under the
    # existing unchanged postprocess/continuation contracts.
    t = Track.from_arrays(np.array([100.0+i*10 for i in range(25)]), np.full(25, 300.),
                          np.array([not 9 <= i <= 12 for i in range(25)]))
    assert process(t).interp[9:13].all()
    assert all(f.shuttle_observation.status == "missing" and f.shuttle_observation.selected_xy is None for f in original[9:13])
    assert current.shuttle.interp[9:13].all(), "Typed raw absence incorrectly erases independent reconstructed temporal provenance"
    assert current.shuttle.vis[9:13].all()
    assert trajectory_continuation_supported(current, 10)
    # Reconstruction is not an observed contact or synthesized raw detection.
    assert not (current.shuttle.vis & ~current.shuttle.interp)[9:13].any()
    assert not any(9 <= candidate.frame <= 12 for candidate in detect_contacts(current, enforce_alternation=False))


@pytest.mark.parametrize("discipline", ["singles", "doubles"])
def test_legacy_no_association_provenance_already_retains_reconstruction(tmp_path, discipline):
    current, _ = window(tmp_path, discipline, typed=False)
    assert current.shuttle.interp[9:13].all()
    assert trajectory_continuation_supported(current, 10)


@pytest.mark.parametrize("status", ["ambiguous", "invalid"])
def test_contradictory_or_invalid_raw_evidence_must_stay_excluded(tmp_path, status):
    current, _ = window(tmp_path, "singles", missing_status=status)
    assert not current.shuttle.vis[9:13].any()
    assert not current.shuttle.interp[9:13].any()
