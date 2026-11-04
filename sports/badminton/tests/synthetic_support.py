"""Explicit controlled identity boundary for labelled legacy-engine unit tests.

The synthetic fixtures in these tests declare track 1 = P1 near and track 2 =
P2 far as input labels. This is not inferred from camera position, competitor
names or match format. Production ingestion must retain its anonymous default;
the initial-identity and reset regression suites test that default separately.
"""

from bai_badminton.engine import BadmintonMatchEngine


def bind_labelled_synthetic_singles(engine: BadmintonMatchEngine) -> None:
    """Admit the unit fixture's explicit labelled identity before any frames.

    These tests isolate downstream geometry, match-phase, persistence and
    correction contracts from identity admission. This internal seam is not a
    production review API and must not be used by synthetic/demo runtime paths.
    """
    assert engine.match_cfg.discipline == "singles"
    assert engine._last_frame == -1
    engine._multi_person_identity_ambiguous = False
    engine._provenance["player_detector"] = "labelled-synthetic-person-observations@1"
