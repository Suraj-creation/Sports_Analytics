"""Match-phase gating: warm-up / practice / replayed hitting must never reach the official score."""

from pathlib import Path

import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.match_phase import MatchPhaseTracker, Phase, RallyEvidence, serve_formation
from bai_badminton.perception_types import ChunkPerception, FramePerception, ScoreReading
from bai_badminton.testing.synth import broadcast_homography, make_rally, to_frames
from bai_engine.schema import EventStatus, Provenance
from bai_engine.store import EventStore

FPS = 30.0
# warm-up: both players deep on the same lateral side — not diagonal service courts
WARM = {"near_xy": (-1.5, -5.6), "far_xy": (-1.5, 5.6)}


def _rally(winner: str, seed: int, lead_in: int = 30, **kw: object):  # type: ignore[no-untyped-def]
    n = 5 if winner == "P1" else 4  # odd count: P1 hits last into the far half and wins
    land = (0.5, 4.5) if winner == "P1" else (0.5, -4.5)
    return make_rally(n_shots=n, fps=FPS, lead_in=lead_in, land_court=land, seed=seed, **kw)  # type: ignore[arg-type]


def _run(tmp_path: Path, rallies: list, ocr: list[ScoreReading] | None = None, names: dict | None = None):  # type: ignore[no-untyped-def,type-arg]
    frames: list[FramePerception] = []
    for r in rallies:
        frames.extend(to_frames(r, len(frames)))
    store = EventStore(tmp_path / "e.sqlite", "S1")
    cfg = EngineConfig(fps=FPS, frame_width=1280, frame_height=720)
    eng = BadmintonMatchEngine("S1", cfg, store, player_names=names)
    eng.set_calibration(0, broadcast_homography())
    pending = sorted(ocr or [], key=lambda r: r.frame_idx)
    for s in range(0, len(frames), 64):
        part = frames[s : s + 64]
        while pending and pending[0].frame_idx <= part[-1].frame_idx:
            eng.on_ocr(pending.pop(0))
        eng.ingest(ChunkPerception(start=part[0].frame_idx, end=part[-1].frame_idx, frames=part))
    eng.flush()
    return eng, store


# ---------------------------------------------------------------------- rules
def test_serve_formation_is_diagonal() -> None:
    assert serve_formation((0.5, -4.0), (-0.5, 4.0)) is True  # both in their own right court
    assert serve_formation((-0.8, -4.0), (0.8, 4.0)) is True  # both left
    assert serve_formation((0.8, -4.0), (0.8, 4.0)) is False  # near right, far left: parallel
    assert serve_formation((0.5, -4.0), (0.5, -2.5)) is False  # same half
    assert serve_formation((0.5, -1.0), (-0.5, 4.0)) is False  # inside the short service line
    assert serve_formation(None, (-0.5, 4.0)) is None


def test_tracker_needs_positive_evidence_to_start_the_match() -> None:
    t = MatchPhaseTracker()
    assert not t.decide(0, RallyEvidence(formation=None)).official  # unseen players never start it
    d = t.decide(100, RallyEvidence(formation=False, still=False, gap_s=2.0))
    assert not d.official and t.phase is Phase.WARMUP and "diagonal" in d.reason
    assert not t.decide(200, RallyEvidence(formation=True, still=True, gap_s=1.5)).official  # quick restart
    assert t.decide(500, RallyEvidence(formation=True, still=True, gap_s=9.0)).official
    assert t.phase is Phase.MATCH_PLAY
    assert t.decide(600, RallyEvidence(formation=False)).official  # in play: missing set-up is noise
    assert not t.decide(700, RallyEvidence(formation=False, after_cut=True)).official  # replay tail
    assert not t.decide(800, RallyEvidence(formation=True, scoreboard="unchanged")).official
    assert not t.decide(900, RallyEvidence(), match_finished=True).official
    assert t.phase is Phase.COMPLETED


def test_human_marker_and_override_win() -> None:
    t = MatchPhaseTracker(match_start_frame=1000)
    assert not t.decide(10, RallyEvidence(formation=True, scoreboard="changed")).official
    assert t.decide(1000, RallyEvidence(formation=False)).official
    assert t.decide(5, RallyEvidence(), override=True).official


# ---------------------------------------------------------------------- engine
def test_warmup_rallies_are_not_scored(tmp_path: Path) -> None:
    rallies = [
        _rally("P1", 1, **WARM),
        _rally("P2", 2, **WARM),
        _rally("P1", 3, lead_in=180),  # players set in serve formation after a pause: the match
        _rally("P2", 4),
        _rally("P1", 5),
    ]
    eng, store = _run(tmp_path, rallies)
    ends = store.query(types=["rally_end"])
    assert len(ends) == 5
    assert [e.payload["official"] for e in ends] == [False, False, True, True, True]
    assert [e.payload["rally_no"] for e in ends] == [None, None, 1, 2, 3]
    assert ends[0].payload["winner"] is None and ends[0].payload["observed_winner"] == "P1"
    assert len(store.query(types=["point"])) == 3
    assert eng.public_state()["score"] == {"P1": 2, "P2": 1}
    phases = [e.payload["phase"] for e in store.query(types=["match_phase"])]
    assert phases == ["warmup", "match_play"]
    a = eng.analytics.to_public()
    assert a["rallies"] == 3 and a["unofficial_rallies"] == 2
    # warm-up strokes stay on the timeline but out of the statistics
    n_strokes = sum(sum(p["strokes"].values()) for p in a["players"].values())
    official_shots = sum(e.payload["n_shots"] for e in ends if e.payload["official"])
    assert n_strokes == official_shots < len(store.query(types=["stroke"]))
    assert all(h.rally_id != ends[0].event_id for h in eng.analytics.highlights(k=10))


def test_api_rebuild_matches_engine(tmp_path: Path) -> None:
    from bai_badminton.analytics.rebuild import build

    eng, store = _run(tmp_path, [_rally("P1", 1, **WARM), _rally("P2", 2, lead_in=180), _rally("P1", 3)])
    rebuilt = build(store, None, FPS).to_public()
    live = eng.analytics.to_public()
    for k in ("rallies", "unofficial_rallies", "active_play_s"):
        assert rebuilt[k] == live[k]
    assert rebuilt["players"]["P1"]["strokes"] == live["players"]["P1"]["strokes"]


def test_unchanged_scoreboard_rejects_rally_in_play(tmp_path: Path) -> None:
    rallies = [_rally("P1", 1), _rally("P2", 2), _rally("P1", 3)]
    starts, n = [], 0
    for r in rallies:
        starts.append(n)
        n += r.obs.n
    board = [("AXELSEN", 0), ("LEE", 0)]

    def read(f: int, a: int, b: int) -> list[ScoreReading]:
        return [ScoreReading(frame_idx=f + k, rows=((board[0][0], a), (board[1][0], b)), conf=0.9) for k in (0, 5)]

    # before rally 1: 0-0; after rally 1: 1-0; rally 2 is a replay — the board stays 1-0; after 3: 2-0
    ocr = read(starts[0] + 2, 0, 0) + read(starts[1] + 2, 1, 0) + read(starts[2] + 2, 1, 0) + read(n - 12, 2, 0)
    eng, store = _run(tmp_path, rallies, ocr)
    ends = store.query(types=["rally_end"])
    assert [e.payload["official"] for e in ends] == [True, False, True]
    assert ends[1].payload["phase_basis"] == "scoreboard"
    assert eng.public_state()["score"] == {"P1": 2, "P2": 0}


def test_match_start_marker_refolds_and_survives_restore(tmp_path: Path) -> None:
    rallies = [_rally("P1", 1, **WARM), _rally("P2", 2, **WARM), _rally("P1", 3, lead_in=180), _rally("P2", 4)]
    eng, store = _run(tmp_path, rallies)
    assert eng.public_state()["score"] == {"P1": 1, "P2": 1}
    second = store.query(types=["rally_end"])[1]
    eng.set_match_start(second.frame_start, Provenance(model="human"))
    ends = store.query(types=["rally_end"])
    assert [e.payload["official"] for e in ends] == [False, True, True, True]
    assert [e.payload["rally_no"] for e in ends] == [None, 1, 2, 3]
    assert eng.public_state()["score"] == {"P1": 1, "P2": 2}
    pts = store.query(types=["point"])
    assert len(pts) == 3 and pts[-1].payload["state_after"]["score"] == {"P1": 1, "P2": 2}
    assert store.state_at(10**9).state["score"] == {"P1": 1, "P2": 2}  # type: ignore[union-attr]

    # restart: the marker and the re-fold are rebuilt from the log
    eng2 = BadmintonMatchEngine("S1", EngineConfig(fps=FPS, frame_width=1280, frame_height=720), store)
    assert eng2.restore_from_log(10**6) == 4
    assert eng2.phase.match_start_frame == second.frame_start
    assert eng2.public_state()["score"] == {"P1": 1, "P2": 2}
    assert eng2.analytics.to_public()["rallies"] == 3


def test_reviewer_can_mark_a_rally_official_or_not(tmp_path: Path) -> None:
    eng, store = _run(tmp_path, [_rally("P1", 1, **WARM), _rally("P2", 2, lead_in=180), _rally("P1", 3)])
    first, second = store.query(types=["rally_end"])[:2]
    eng.set_rally_official(first.event_id, True, Provenance(model="human"))
    ends = store.query(types=["rally_end"])
    assert ends[0].payload["official"] and ends[0].status is EventStatus.HUMAN_VERIFIED
    assert eng.public_state()["score"] == {"P1": 2, "P2": 1}
    eng.set_rally_official(second.event_id, False, Provenance(model="human"))
    assert eng.public_state()["score"] == {"P1": 2, "P2": 0}
    assert [e.payload["rally_no"] for e in store.query(types=["rally_end"])] == [1, None, 2]


def test_winner_correction_on_warmup_rally_makes_it_official(tmp_path: Path) -> None:
    eng, store = _run(tmp_path, [_rally("P1", 1, **WARM), _rally("P2", 2, lead_in=180)])
    first = store.query(types=["rally_end"])[0]
    eng.correct_rally_winner(first.event_id, "P2", Provenance(model="human"))
    assert eng.public_state()["score"] == {"P1": 0, "P2": 2}


@pytest.mark.parametrize("pos", [{"near_xy": (0.3, -4.9), "far_xy": (-0.2, 4.9)}])
def test_video_starting_at_the_serve_is_scored(tmp_path: Path, pos: dict) -> None:  # type: ignore[type-arg]
    eng, _ = _run(tmp_path, [_rally("P1", 1, **pos), _rally("P1", 2, **pos)])
    assert eng.public_state()["score"] == {"P1": 2, "P2": 0}


def test_video_starting_mid_game_takes_the_score_from_the_board(tmp_path: Path) -> None:
    rallies = [_rally("P1", 1), _rally("P2", 2)]
    starts, n = [], 0
    for r in rallies:
        starts.append(n)
        n += r.obs.n

    def read(f: int, a: int, b: int) -> list[ScoreReading]:
        return [ScoreReading(frame_idx=f + k, rows=(("AXELSEN", a), ("LEE", b)), conf=0.9) for k in (0, 5)]

    ocr = read(starts[0] + 2, 11, 9) + read(starts[1] + 2, 12, 9) + read(n - 12, 12, 10)
    names = {"P1": "Viktor Axelsen", "P2": "Lee Zii Jia"}
    eng, store = _run(tmp_path, rallies, ocr, names)
    assert eng.public_state()["score"] == {"P1": 12, "P2": 10}
    ends = store.query(types=["rally_end"])
    assert [e.payload["winner_source"] for e in ends] == ["ocr", "ocr"]
    pts = store.query(types=["point"])
    assert [p.payload["state_after"]["score"] for p in pts] == [{"P1": 12, "P2": 9}, {"P1": 12, "P2": 10}]
    base = [e for e in store.query(types=["match_phase"]) if e.payload.get("base_state")]
    assert base and base[0].payload["base_state"]["score"] == {"P1": 11, "P2": 9}
    eng2 = BadmintonMatchEngine("S1", EngineConfig(fps=FPS, frame_width=1280, frame_height=720), store)
    eng2.restore_from_log(10**6)
    assert eng2.public_state()["score"] == {"P1": 12, "P2": 10}
