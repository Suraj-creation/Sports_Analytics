"""The explicit session format controls court geometry on engine creation."""

from pathlib import Path

import numpy as np
import pytest

from bai_badminton.court import fit_homography
from bai_badminton.plugin import BadmintonSession
from bai_engine.config import Profile
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import MediaInfo, Session, Source, SourceKind
from bai_engine.schema.session import ParticipantRoster
from bai_engine.store import EventStore

PROFILE = Profile.model_validate(
    {
        "name": "cpu-test",
        "shuttle": {"model": "none", "backend": "none"},
        "player_detector": {"model": "none", "backend": "none"},
        "pose": {"model": "none", "backend": "none"},
        "stroke": {"model": "none", "backend": "none"},
    }
)
CLICKS = {
    "far_left": (420.0, 120.0),
    "far_right": (860.0, 120.0),
    "near_right": (1130.0, 712.0),
    "near_left": (150.0, 712.0),
}


def make_session(tmp_path: Path, match_format: str | None) -> BadmintonSession:
    session = Session(
        title="match",
        source=Source(kind=SourceKind.UPLOAD, uri="test.mp4"),
        media=MediaInfo(fps_num=30, fps_den=1, n_frames=300, width=1280, height=720, duration_us=10000000),
        roster=ParticipantRoster(match_format=match_format) if match_format else None,
    )
    return BadmintonSession(
        session,
        EventStore(tmp_path / "events.sqlite", session.session_id),
        PROFILE,
        ModelRegistry(Path(__file__).resolve().parents[3] / "models"),
        lambda _: None,
    )


@pytest.mark.parametrize("match_format,expected", [(None, "singles"), ("singles", "singles"), ("doubles", "doubles")])
def test_roster_format_selects_engine_court_discipline(tmp_path: Path, match_format: str | None, expected: str) -> None:
    plugin = make_session(tmp_path, match_format)
    assert plugin.engine.match_cfg.discipline == expected
    h = fit_homography(CLICKS)
    plugin.engine.set_calibration(0, h, emit=False)
    xy = h.court_to_image(np.array([[2.8, 1.0]], dtype=float))[0]
    inside = plugin.engine.calibration[0].geometry.signed_dist(*xy) > 0
    assert inside is (expected == "doubles")


def test_session_format_is_captured_for_an_analysis_not_mutated_midrun(tmp_path: Path) -> None:
    first = make_session(tmp_path, None)
    changed = first.session.model_copy(update={"roster": ParticipantRoster(match_format="doubles")})
    assert first.engine.match_cfg.discipline == "singles"
    reopened = BadmintonSession(
        changed, first.store, PROFILE, ModelRegistry(Path(__file__).resolve().parents[3] / "models"), lambda _: None
    )
    assert reopened.engine.match_cfg.discipline == "doubles"
