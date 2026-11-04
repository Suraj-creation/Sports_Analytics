"""Built-in profiles select an executable provider, not an absent model label."""

import pytest
import yaml

from bai_badminton.components import DomainContext, register_domain_components
from bai_badminton.events.stroke import StrokeContext
from bai_badminton.rules import MatchConfig
from bai_engine.components import ComponentRegistry
from bai_engine.config import REPO_ROOT, load_profile
from bai_engine.runtime.registry import ModelRegistry


@pytest.mark.parametrize("profile_name", ["cpu-dev", "gpu-high", "gpu-rtx4000", "gpu-doubles-identity"])
@pytest.mark.parametrize("match_format", ["singles", "doubles"])
def test_builtin_stroke_choice_executes_without_any_bst_artifact(tmp_path, profile_name, match_format):
    profile = load_profile(profile_name, REPO_ROOT / "config/profiles")
    # An empty artifact registry makes any hidden checkpoint dependency fail.
    models = tmp_path / "models"
    models.mkdir()
    (models / "manifest.yaml").write_text(yaml.safe_dump({"models": {}}))
    artifacts = ModelRegistry(models)
    registry = ComponentRegistry()
    register_domain_components(registry)
    choice = profile.components["stroke"].model_copy(deep=True)
    context = DomainContext(30, 1280, 720, MatchConfig(discipline=match_format), artifacts)
    handle = registry.create(
        "stroke", choice.implementation, context=context,
        configuration=choice.model_dump(mode="json"), match_format=match_format,
        context_identity={"profile": profile.name},
    )
    try:
        result = handle.instance.predict(StrokeContext(
            frame=8, player_id=None, is_serve=None, hitter_court_xy=None,
            speed_after_px_s=None, frame_height_px=720, flight_time_s=None,
            vy_after_px_s=None, hitter_side=None, contact_above_head=None,
        ))
        assert handle.contract.implementation == "stroke-rules-v0"
        assert result.model == "stroke_rules_v0"
        assert result.top[0] == "unknown" and result.abstention_reason == "missing_required_evidence"
        assert choice.model == "none" and choice.backend == "none"
        assert profile.stroke.model == "none" and profile.stroke.backend == "none"
        assert list(artifacts.cache.iterdir()) == []
    finally:
        handle.close()
