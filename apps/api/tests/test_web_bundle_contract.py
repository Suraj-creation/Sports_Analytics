"""A frontend rebuild must not make the independent API factory crash."""

import pytest
from fastapi.testclient import TestClient

from bai_api import app as app_module


@pytest.mark.parametrize("layout", ["absent", "empty", "index_only", "assets_only", "complete"])
def test_only_complete_web_bundle_installs_spa(settings, tmp_path, monkeypatch, layout):
    root = tmp_path / "dist"
    if layout != "absent":
        root.mkdir()
    if layout in ("index_only", "complete"):
        (root / "index.html").write_text("<html>controlled build</html>")
    if layout in ("assets_only", "complete"):
        (root / "assets").mkdir()
        (root / "assets" / "app.js").write_text("export {};")
    monkeypatch.setattr(app_module, "WEB_DIST", root)
    application = app_module.create_app(settings, start_engine=False)
    with TestClient(application) as client:
        response = client.get("/library")
        assert response.status_code == (200 if layout == "complete" else 404)
        if layout == "complete":
            assert response.text == "<html>controlled build</html>"
            assert client.get("/assets/app.js").status_code == 200
        assert client.get("/api/nonexistent").status_code == 404
