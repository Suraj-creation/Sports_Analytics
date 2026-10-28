"""Optional identity inference uses only pinned local artifacts and explicit devices."""

from pathlib import Path
from types import SimpleNamespace

from bai_badminton.perception import offline_reid
from bai_badminton.perception.pipeline import BadmintonPerception
from bai_engine.config import ModelChoice, load_profile
from bai_engine.runtime.registry import ModelError


def pipeline():
    p = BadmintonPerception.__new__(BadmintonPerception)
    p.models = {}
    p.degraded = []
    return p


def test_existing_profiles_keep_optional_reid_disabled():
    assert load_profile("cpu-dev").player_reid is None
    assert load_profile("gpu-rtx4000").player_reid is None


def test_descriptor_loading_is_local_and_device_explicit(monkeypatch):
    calls = []

    class Registry:
        def path(self, name, *, fetch):
            calls.append((name, fetch))
            return Path("weights.pt")

        def get(self, name):
            return SimpleNamespace(ref=name + "@1")

    monkeypatch.setattr(offline_reid, "OSNetAppearanceEmbedder", lambda path, **kw: (path, kw))
    p = pipeline()
    result = p._load_reid(ModelChoice(model="osnet_ain_x0_25", backend="torch-cpu"), Registry())
    assert calls == [("osnet_ain_x0_25", False)]
    assert result[1]["device"] == "cpu"
    assert p.models["player_reid"] == "osnet_ain_x0_25@1"


def test_missing_checkpoint_and_unsupported_precision_degrade_without_download():
    class Registry:
        def path(self, *args, **kw):
            raise ModelError("checkpoint not cached")

    p = pipeline()
    assert p._load_reid(ModelChoice(model="osnet_ain_x0_25", backend="torch-cuda"), Registry()) is None
    assert p.degraded[0].stage == "player_identity"
    assert (
        p._load_reid(ModelChoice(model="osnet_ain_x0_25", backend="torch-cuda", precision="fp16"), Registry()) is None
    )
    assert len(p.degraded) == 2


def test_disabled_choice_never_opens_an_artifact():
    p = pipeline()
    assert p._load_reid(None, None) is None
