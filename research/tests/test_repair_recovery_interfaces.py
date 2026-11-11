import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from research import pipeline_repair_evaluation as evaluation
from research import production_external_semantic_replay as replay


def test_no_reference_access_when_completion_proof_fails(tmp_path, monkeypatch):
    def fail(*args, **kwargs):
        raise ValueError("incomplete producer")

    monkeypatch.setattr(evaluation, "load_finished_input", fail)
    monkeypatch.setattr(evaluation, "read_csv", lambda *a: pytest.fail("reference read before verification"))
    with pytest.raises(ValueError, match="incomplete producer"):
        evaluation.evaluate(
            tmp_path / "run",
            "SESSION",
            tmp_path / "labels.csv",
            tmp_path / "out",
            completion_recovery=tmp_path / "recovery",
        )


def test_default_loader_does_not_infer_recovery_for_failed_worker(tmp_path):
    (tmp_path / "inference.json").write_text('{"status":"partial_or_failed"}')
    tmp_path.with_suffix(".executor.json").write_text("{}")
    with pytest.raises(ValueError, match="finished source-guarded"):
        replay.load_finished_input(tmp_path, "SESSION")


def test_explicit_recovery_cannot_be_used_for_other_session(tmp_path, monkeypatch):
    session = tmp_path / "session.json"
    session.write_text('{"session_id":"ACTUAL"}')
    module = SimpleNamespace(verify_completion_receipt=lambda *a: {"session_path": session})
    monkeypatch.setitem(sys.modules, "research.pipeline_repair_completion", module)
    with pytest.raises(ValueError, match="different session"):
        replay.load_finished_input(tmp_path, "OTHER", completion_recovery=Path("explicit"))


def test_product_recovery_proof_is_checked_before_asset_copy(tmp_path, monkeypatch):
    from research import production_product_smoke as product

    def fail(*args, **kwargs):
        raise ValueError("tampered recovery proof")

    module = SimpleNamespace(verify_completion_receipt=fail)
    monkeypatch.setitem(sys.modules, "research.pipeline_repair_completion", module)
    monkeypatch.setattr(product.shutil, "copyfile", lambda *a: pytest.fail("copied before verified completion"))
    with pytest.raises(ValueError, match="tampered recovery proof"):
        product.stage_completed_run(tmp_path / "run", {}, completion_recovery=tmp_path / "proof")
