"""Raw association absence and independent temporal reconstruction stay distinct."""

from dataclasses import replace

import numpy as np
import pytest

from bai_badminton.components import _EvidenceRally
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.contact import detect_contacts
from bai_badminton.events.rally_fsm import RallyParams
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
        raw = None if absent and missing_status != "ambiguous" else (100.0 + i * 10, 300.0)
        status = missing_status if absent else "observed"
        association = "rejected" if status in {"ambiguous", "invalid"} else "unknown" if absent else "tracked"
        support = 0.9 if raw else 0.0
        result.append(
            FramePerception(
                i,
                raw,
                support,
                shuttle_observation=ShuttleObservationEvidence(
                    i,
                    0,
                    status,
                    association,
                    raw,
                    raw if status == "observed" else None,
                    support,
                )
                if typed
                else None,
            )
        )
    return result


def window(tmp_path, discipline, **kwargs):
    store = EventStore(tmp_path / "events.sqlite", "PROVENANCE")
    engine = BadmintonMatchEngine(
        "PROVENANCE",
        EngineConfig(fps=30, frame_width=1280, frame_height=720, match=MatchConfig(discipline=discipline)),
        store,
    )
    sequence = frames(**kwargs)
    engine.ingest(ChunkPerception(0, 24, sequence))
    return engine._window(0, 24), sequence


@pytest.mark.parametrize("discipline", ["singles", "doubles"])
def test_modern_raw_missing_keeps_independent_reconstructed_temporal_context(tmp_path, discipline):
    current, original = window(tmp_path, discipline)
    # This exact bounded gap has coherent moving observed brackets under the
    # existing unchanged postprocess/continuation contracts.
    t = Track.from_arrays(
        np.array([100.0 + i * 10 for i in range(25)]),
        np.full(25, 300.0),
        np.array([not 9 <= i <= 12 for i in range(25)]),
    )
    assert process(t).interp[9:13].all()
    assert all(
        f.shuttle_observation.status == "missing" and f.shuttle_observation.selected_xy is None for f in original[9:13]
    )
    assert current.shuttle.interp[9:13].all(), (
        "Typed raw absence incorrectly erases independent reconstructed temporal provenance"
    )
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


@pytest.mark.parametrize("status", ["ambiguous", "invalid", "rejected"])
def test_missing_neighbors_cannot_be_filled_through_incompatible_evidence(tmp_path, status):
    sequence = frames()
    raw = (210.0, 300.0) if status == "ambiguous" else None
    sequence[11].shuttle_xy = raw
    sequence[11].shuttle_conf = 0.9 if raw else 0.0
    sequence[11].shuttle_observation = ShuttleObservationEvidence(
        11, 0, "missing" if status == "rejected" else status, "rejected", raw, None, 0.9 if raw else 0.0
    )
    store = EventStore(tmp_path / "barrier.sqlite", "BARRIER")
    engine = BadmintonMatchEngine("BARRIER", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    engine.ingest(ChunkPerception(0, 24, sequence))
    current = engine._window(0, 24)
    assert not current.shuttle.vis[9:13].any()
    assert not current.shuttle.interp[9:13].any()
    # An interpolation prohibition is not a fabricated camera cut/FSM reset.
    assert not current.break_before.any()


@pytest.mark.parametrize("boundary", ["shot", "epoch", "replay", "invalid_view"])
def test_missing_reconstruction_does_not_cross_source_context_boundary(tmp_path, boundary):
    sequence = frames()
    for i, frame in enumerate(sequence):
        if boundary == "shot" and i >= 11:
            frame.shot_id = 1
        elif boundary == "epoch" and i >= 11:
            frame.content_epoch = 1
        elif boundary == "replay" and i >= 11:
            frame.replay = True
        elif boundary == "invalid_view" and i == 11:
            frame.view = "none"
        # Maintain exact provenance when the canonical source context changes.
        evidence = frame.shuttle_observation
        frame.shuttle_observation = replace(evidence, epoch=(frame.shot_id << 32) | frame.content_epoch)
    store = EventStore(tmp_path / "context.sqlite", "CONTEXT")
    engine = BadmintonMatchEngine("CONTEXT", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    engine.ingest(ChunkPerception(0, 24, sequence))
    current = engine._window(0, 24)
    assert not current.shuttle.interp[9:13].any()


@pytest.mark.parametrize("discipline", ["singles", "doubles"])
@pytest.mark.parametrize("enabled,expected", [(True, 1), (False, 2)])
def test_explicit_reconstruction_option_reaches_real_engine_rally_outputs(tmp_path, discipline, enabled, expected):
    store = EventStore(tmp_path / "continuation.sqlite", "CONTINUATION")
    engine = BadmintonMatchEngine(
        "CONTINUATION",
        EngineConfig(fps=30, frame_width=1280, frame_height=720, match=MatchConfig(discipline=discipline)),
        store,
        rally_segmenter=_EvidenceRally(RallyParams(fps=30), use_reconstruction=enabled),
    )
    sequence = []
    for i in range(165):
        raw = None if 70 <= i <= 93 else (100.0 + i * 5, 300.0)
        support = 0.9 if raw else 0.0
        sequence.append(
            FramePerception(
                i,
                raw,
                support,
                shuttle_observation=ShuttleObservationEvidence(
                    i, 0, "observed" if raw else "missing", "tracked" if raw else "unknown", raw, raw, support
                ),
            )
        )
    for lo in range(0, len(sequence), 15):
        engine.ingest(ChunkPerception(lo, min(lo + 14, 164), sequence[lo : lo + 15]))
    engine.flush()
    rallies = store.query(types=["rally_end"])
    assert len(rallies) == expected
    if enabled:
        assert (rallies[0].frame_start, rallies[0].frame_end) == (1, 164)
    assert not store.query(types=["contact", "stroke", "point"])
    assert all(f.shuttle_observation.selected_xy is None for f in sequence[70:94])
