"""Scheduled source-board observations do not depend on inferred rally activity.

The real reader cadence, parser and pipeline run with controlled OCR text in
place of the neural recognizer. These are acquisition contract regressions,
not accuracy measurements or accepted-point evidence.
"""

from types import SimpleNamespace

import numpy as np
import pytest

from bai_badminton.perception.pipeline import BadmintonPerception, _Scene
from bai_badminton.perception.scoreboard import ScoreboardReader
from bai_engine.config import ModelChoice, Profile
from bai_engine.decode import DecodedChunk
from bai_engine.runtime.registry import ModelRegistry


def _recognized_board(crop):
    return SimpleNamespace(
        boxes=[[[2, 2], [48, 2], [48, 8], [2, 8]], [[2, 12], [48, 12], [48, 18], [2, 18]]],
        txts=["ALPHA 9", "BETA 8"],
        scores=[0.95, 0.95],
    )


def _perception(tmp_path, monkeypatch, match_format, *, enabled=True, views=None, scene_policy=None, replay_status=None):
    disabled = ModelChoice(model="none", backend="none")
    profile = Profile(
        name="scoreboard-acquisition-contract",
        shuttle=disabled,
        player_detector=disabled,
        pose=disabled,
        stroke=disabled,
        ocr=ModelChoice(model="rapidocr_v4", backend="onnx-cpu", params={"scene_policy": scene_policy} if scene_policy else {}) if enabled else None,
        ocr_every_s=0.1,  # Three canonical frames at the configured 30 fps.
    )
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    (model_dir / "manifest.yaml").write_text(
        "models:\n  rapidocr_v4:\n    task: ocr\n    format: package\n    source: {package: rapidocr}\n",
        encoding="utf-8",
    )
    # Keep loader interval propagation, reader state, parser and pipeline real.
    # The recognizer is the only model operation replaced in these tests.
    monkeypatch.setattr(
        ScoreboardReader,
        "load",
        classmethod(lambda cls, every, *, backend: cls(_recognized_board, every)),
    )
    perception = BadmintonPerception(
        profile,
        ModelRegistry(model_dir),
        30.0,
        model_dir,
        (160, 80),
        match_format=match_format,
    )

    def scene(chunk, cuts):
        observed_views = ["main"] * len(chunk.frames) if views is None else views
        extra = {"broadcast_replay_status": replay_status} if replay_status is not None else {}
        return _Scene(
            observed_views,
            [0] * len(chunk.frames),
            [1.0] * len(chunk.frames),
            None,
            [None] * len(chunk.frames),
            **extra,
        )

    monkeypatch.setattr(perception, "_scene", scene)
    return perception


def _chunk(start, count):
    return DecodedChunk(start, [np.full((80, 160, 3), 255, np.uint8) for _ in range(count)])


@pytest.mark.parametrize("match_format", ["singles", "doubles"])
@pytest.mark.parametrize("in_play", [False, True])
def test_scheduled_main_view_board_reads_survive_in_play(tmp_path, monkeypatch, match_format, in_play):
    perception = _perception(tmp_path, monkeypatch, match_format)
    readings = perception._read_scoreboard(_chunk(100, 10), [False] * 10, in_play)

    assert [reading.frame_idx for reading in readings] == [100, 103, 106, 109]
    assert all(reading.rows == (("ALPHA", 9), ("BETA", 8)) for reading in readings)
    assert perception.stats.ocr_calls == 4
    assert perception.stats.ocr_readings == 4


@pytest.mark.parametrize("match_format", ["singles", "doubles"])
def test_process_publishes_scheduled_board_observations_when_chunk_begins_in_play(
    tmp_path, monkeypatch, match_format
):
    perception = _perception(tmp_path, monkeypatch, match_format)
    result = perception.process(_chunk(100, 10), in_play=True)

    assert [reading.frame_idx for reading in result.ocr] == [100, 103, 106, 109]
    assert len(result.frames) == 10
    assert perception.stats.ocr_calls == 4
    assert perception.stats.ocr_readings == 4


@pytest.mark.parametrize("match_format", ["singles", "doubles"])
@pytest.mark.parametrize("in_play", [False, True])
def test_replay_and_absent_court_frames_do_not_read_or_consume_main_view_cadence(
    tmp_path, monkeypatch, match_format, in_play
):
    views = ["alt", "main", "main", "main", "none", "main", "main", "main", "main", "main"]
    perception = _perception(tmp_path, monkeypatch, match_format, views=views)
    result = perception.process(_chunk(100, 10), in_play=in_play)

    assert [reading.frame_idx for reading in result.ocr] == [101, 105, 108]
    assert result.frames[0].replay is True
    assert result.frames[4].replay is True
    assert perception.stats.ocr_calls == 3
    assert perception.stats.ocr_readings == 3


@pytest.mark.parametrize("match_format", ["singles", "doubles"])
def test_configured_ocr_interval_survives_activity_changes_and_chunk_boundaries(
    tmp_path, monkeypatch, match_format
):
    perception = _perception(tmp_path, monkeypatch, match_format)
    idle_before = perception.process(_chunk(100, 2), in_play=False)
    playing = perception.process(_chunk(102, 3), in_play=True)
    idle_after = perception.process(_chunk(105, 4), in_play=False)

    assert [reading.frame_idx for reading in idle_before.ocr] == [100]
    assert [reading.frame_idx for reading in playing.ocr] == [103]
    assert [reading.frame_idx for reading in idle_after.ocr] == [106]
    assert perception.stats.ocr_calls == 3
    assert perception.stats.ocr_readings == 3


@pytest.mark.parametrize("match_format", ["singles", "doubles"])
@pytest.mark.parametrize("in_play", [False, True])
def test_disabled_ocr_emits_no_board_observations_or_calls(tmp_path, monkeypatch, match_format, in_play):
    perception = _perception(tmp_path, monkeypatch, match_format, enabled=False)
    result = perception.process(_chunk(100, 10), in_play=in_play)

    assert result.ocr == []
    assert perception.stats.ocr_calls == 0
    assert perception.stats.ocr_readings == 0
