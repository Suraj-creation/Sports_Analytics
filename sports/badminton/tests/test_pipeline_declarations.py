"""The replaceable whole pipeline publishes composition and actual provider identity."""
from test_plugin_discipline import make_session

from bai_badminton.plugin import BadmintonPlugin


def test_whole_pipeline_declares_its_streaming_stage_dependencies_and_lifecycle():
    declaration = BadmintonPlugin().describe_pipeline()
    assert declaration['plugin'] == 'badminton'
    assert declaration['pipeline_version']
    assert set(declaration['supported_formats']) == {'singles', 'doubles', 'unknown'}
    assert declaration['input_schema'] and declaration['output_schema']
    assert declaration['lifecycle']['per_session_factory'] is True
    seen = set()
    for stage in declaration['stages']:
        assert stage['id'] not in seen
        assert set(stage['depends_on']) <= seen
        assert stage['components']
        seen.add(stage['id'])
    assert {'perception', 'format', 'identity', 'activity', 'contact', 'rally', 'stroke',
            'outcome', 'scoring', 'analytics'} <= seen


def test_session_pipeline_declaration_is_detached_and_binds_actual_components(tmp_path):
    plugin = make_session(tmp_path, 'doubles')
    try:
        description = plugin.describe_pipeline()
        assert description['components']['tracking']['implementation'] == 'court-player-episodes-v1'
        assert description['components']['identity']['implementation'] == 'participant-identity-v1'
        assert description['components']['stroke']['implementation'] == 'stroke-rules-v0'
        assert description['format']['match_format'] == 'doubles'
        description['stages'].clear()
        assert plugin.describe_pipeline()['stages']
        assert plugin.capabilities()['pipeline']['fingerprint'] == plugin.describe_pipeline()['fingerprint']
        assert plugin._isolation_id()['pipeline_fingerprint'] == plugin.describe_pipeline()['fingerprint']
    finally:
        plugin.close()


def test_source_calibration_changes_pipeline_identity_without_changing_provider(tmp_path):
    from bai_badminton.court import fit_homography
    from test_plugin_discipline import CLICKS

    plugin = make_session(tmp_path, 'singles')
    try:
        before = plugin.describe_pipeline()
        plugin._apply_calibration(fit_homography(CLICKS), emit=False, mode='static')
        after = plugin.describe_pipeline()
        assert before['fingerprint'] != after['fingerprint']
        assert before['components'] == after['components']
    finally:
        plugin.close()


def test_configured_format_observation_history_does_not_invalidate_its_own_raw_cache(tmp_path):
    import numpy as np
    from bai_engine.decode import DecodedChunk

    plugin = make_session(tmp_path, 'singles')
    try:
        chunk = plugin.perceive(DecodedChunk(0, [np.zeros((720, 1280, 3), dtype=np.uint8)]))
        encoded = plugin.encode_perception(chunk)
        plugin.ingest(chunk)
        assert plugin.decode_perception(encoded, diagnostic=True).frames[0].frame_idx == 0
    finally:
        plugin.close()
