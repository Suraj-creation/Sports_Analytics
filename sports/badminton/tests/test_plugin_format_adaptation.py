"""Format decisions apply at their canonical boundary, never to earlier frames."""

import numpy as np
import pytest
import test_plugin_discipline as fixtures

from bai_badminton.court import fit_homography
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs, ScoreReading
from bai_engine.config import ModelChoice


def _plugin(tmp_path, monkeypatch, configured=None):
    profile = fixtures.PROFILE.model_copy(
        update={
            "components": {
                "format": ModelChoice(
                    model="none",
                    backend="none",
                    implementation="sustained-court-v1",
                    params={"min_observations": 3, "min_duration_s": 1.0, "max_gap_s": 0.6},
                )
            }
        }
    )
    monkeypatch.setattr(fixtures, "PROFILE", profile)
    plugin = fixtures.make_session(tmp_path, configured)
    plugin._apply_calibration(fit_homography(fixtures.CLICKS), emit=False, mode="static")
    return plugin


def _chunk(plugin, start, stop, counts=(2, 2), *, shot_id=0, full=True):
    h = plugin.calibration
    frames = []
    for frame in range(start, stop + 1):
        fresh = frame % 15 == 0
        people = []
        for side, count in enumerate(counts):
            for index in range(count):
                x, y = h.court_to_image(np.array([[-1 + 2 * index, -3 if side == 0 else 3]], dtype=float))[0]
                people.append(
                    PersonObs(
                        track_id=side * 10 + index,
                        bbox=np.array([x - 10, y - 80, x + 10, y]),
                        conf=0.95,
                        detector_matched=fresh,
                    )
                )
        frames.append(
            FramePerception(
                frame,
                None,
                0.0,
                persons=people,
                detector_observed=fresh,
                view="main" if full else "none",
                shot_id=shot_id,
                calibration_state=CalibrationState.VALID,
            )
        )
    return ChunkPerception(start, stop, frames)


@pytest.mark.parametrize("counts,expected", [((2, 2), "doubles"), ((1, 1), "singles")])
def test_inferred_format_starts_at_decision_frame_and_preserves_four_person_acquisition(
    tmp_path,
    monkeypatch,
    counts,
    expected,
):
    plugin = _plugin(tmp_path, monkeypatch)
    actual_set = plugin.engine.set_match_format
    actual_ingest = plugin.engine.ingest
    boundaries, segments = [], []

    def set_format(match_format, frame, provenance, **kwargs):
        boundaries.append((match_format, frame))
        return actual_set(match_format, frame, provenance, **kwargs)

    def ingest(perception):
        segments.append(
            (
                perception.start,
                perception.end,
                plugin.engine.cfg.match_format_known,
                [reading.frame_idx for reading in perception.ocr],
            )
        )
        actual_ingest(perception)

    monkeypatch.setattr(plugin.engine, "set_match_format", set_format)
    monkeypatch.setattr(plugin.engine, "ingest", ingest)
    chunk = _chunk(plugin, 0, 60, counts)
    chunk.ocr = [ScoreReading(40, (("ALICE", 1), ("BOB", 0)), conf=0.95)]
    try:
        plugin.ingest(chunk)
        assert boundaries == [(expected, 30)]
        assert segments == [(0, 29, False, []), (30, 60, True, [40])]
        assert plugin.perception.match_format == expected
        assert plugin.perception.players.max_players == 4
        assert plugin.engine.match_cfg.discipline == expected
        assert plugin.public_state()["format"]["source"] == "inferred"
    finally:
        plugin.close()


def test_target_epoch_change_revokes_inference_and_requires_fresh_observations(tmp_path, monkeypatch):
    plugin = _plugin(tmp_path, monkeypatch)
    try:
        plugin.ingest(_chunk(plugin, 0, 60))
        assert plugin.engine.cfg.match_format_known
        plugin._apply_calibration(fit_homography(fixtures.CLICKS), emit=False, mode="static")
        plugin.ingest(_chunk(plugin, 61, 61, full=False))
        assert plugin.format_understanding.decision.match_format == "unknown"
        assert plugin.perception.match_format == "unknown"
        assert not plugin.engine.cfg.match_format_known
    finally:
        plugin.close()


def test_camera_cut_or_occlusion_does_not_downgrade_confirmed_doubles(tmp_path, monkeypatch):
    plugin = _plugin(tmp_path, monkeypatch)
    try:
        plugin.ingest(_chunk(plugin, 0, 60))
        plugin.ingest(_chunk(plugin, 61, 100, counts=(1, 1), shot_id=1))
        assert plugin.format_understanding.decision.match_format == "doubles"
        assert plugin.engine.cfg.match_format_known
    finally:
        plugin.close()
