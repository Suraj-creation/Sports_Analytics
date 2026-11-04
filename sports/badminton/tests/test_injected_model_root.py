"""Derived perception caches use the same injected root as model artifacts."""

import pytest

from bai_badminton import plugin as plugin_module
from bai_engine.config import Profile, get_settings
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import MediaInfo, Session, Source, SourceKind
from bai_engine.schema.session import ParticipantRoster
from bai_engine.store import EventStore


@pytest.mark.parametrize("match_format", [None, "singles", "doubles"])
def test_perception_uses_injected_registry_root_instead_of_global_settings(tmp_path, monkeypatch, match_format):
    class CapturingPerception:
        def __init__(self, profile, registry, fps, models_dir, **kwargs):
            self.registry = registry
            self.models_dir = models_dir
            self.close_count = 0

        def close(self):
            self.close_count += 1

    get_settings.cache_clear()
    try:
        with monkeypatch.context() as patch:
            # Isolate .env discovery as well as the contrasting process setting.
            patch.chdir(tmp_path)
            global_root = tmp_path / "global-models"
            patch.setenv("BAI_MODELS_DIR", str(global_root))
            assert get_settings().models_dir == global_root
            injected_root = tmp_path / "injected-models"
            injected_root.mkdir()
            (injected_root / "manifest.yaml").write_text("models: {}\n")
            registry = ModelRegistry(injected_root)
            patch.setattr(plugin_module, "BadmintonPerception", CapturingPerception)
            session = Session(
                title="Injected model root",
                source=Source(kind=SourceKind.UPLOAD, uri="controlled-input"),
                media=MediaInfo(
                    fps_num=30,
                    fps_den=1,
                    n_frames=30,
                    width=1280,
                    height=720,
                    duration_us=1_000_000,
                ),
                roster=ParticipantRoster(match_format=match_format) if match_format else None,
            )
            with EventStore(tmp_path / "events.sqlite", session.session_id) as store:
                sport = plugin_module.BadmintonSession(
                    session, store, Profile(name="root-test"), registry, lambda _: None
                )
                perception = sport.perception
                try:
                    assert perception.registry is registry
                    assert perception.models_dir == injected_root
                    assert perception.models_dir != global_root
                finally:
                    sport.close()
                assert perception.close_count == 1
                assert not global_root.exists()
    finally:
        # Do not retain this test's environment-derived Settings in other tests.
        get_settings.cache_clear()
