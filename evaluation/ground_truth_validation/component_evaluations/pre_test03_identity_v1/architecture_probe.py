"""Synthetic model-free identity/review/scoring architecture probe.

All stores are private temporary fixtures. 'Human' assertions below are synthetic
test assertions, never real reviewed footage or benchmark ground truth. This
does not assign the private identity latch or modify any production source.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch

import pytest


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def audit(root):
    import bai_badminton.engine as engine_module
    from bai_badminton.analytics.individual import build_individual_analytics
    from bai_badminton.identity import IdentityResolver
    from bai_badminton.identity_review import IdentityReviewLedger

    source=root/"sports/badminton/src/bai_badminton"
    tests=root/"sports/badminton/tests"
    if Path(engine_module.__file__).resolve()!=source/"engine.py":
        raise ValueError("Probe must import the exact candidate source")
    inputs=[source/name for name in ("engine.py","identity.py","identity_review.py","components.py","plugin.py","score_ocr.py",
                                    "analytics/individual.py","analytics/automatic_individual.py","analytics/reviewed_motion.py")]
    inputs += [tests/"test_unbound_initial_singles_identity.py",tests/"test_score_late_reconciliation.py"]
    inputs += [root/"apps/api/src/bai_api/routes/identity_reviews.py",root/"apps/api/src/bai_api/routes/sessions.py"]
    hashes={str(path):sha(path)for path in inputs}
    initial=load("audit_initial_identity_fixture",tests/"test_unbound_initial_singles_identity.py")
    late=load("audit_late_ocr_fixture",tests/"test_score_late_reconciliation.py")
    assignments=[]
    for node in ast.walk(ast.parse((source/"engine.py").read_text())):
        if isinstance(node,ast.Assign):
            if any(isinstance(target,ast.Attribute)and target.attr=="_multi_person_identity_ambiguous"for target in node.targets):
                assignments.append({"line":node.lineno,"literal":node.value.value if isinstance(node.value,ast.Constant)else ast.unparse(node.value)})
    assign_calls=[]
    original=IdentityResolver.assign
    def observed_assign(self,*args,**kwargs):
        assign_calls.append(True)
        return original(self,*args,**kwargs)
    with tempfile.TemporaryDirectory(prefix="identity-contract-probe-")as directory:
        path=Path(directory)
        with patch.object(IdentityResolver,"assign",observed_assign):
            engine,store,capture,item=initial.setup(path)
        stroke,_=initial.classify(engine,store,capture,item)
        initial.official_fixture(store,stroke)
        assert engine._multi_person_identity_ambiguous is True
        assert all(engine._geometry_valid)
        assert not assign_calls
        ledger=IdentityReviewLedger(store,{"sen","loh"},max_frame=16,fps=30)
        hypothesis=stroke.payload["participant_hypothesis"]
        birth=store.get(hypothesis["observation_id"])
        identity=ledger.confirm(birth.event_id,"loh",birth.frame_start,16)
        identity_only=build_individual_analytics(store,initial.roster(),max_frame=16,fps=30)
        scoped=ledger.confirm_stroke(stroke.event_id,identity.event_id)
        reviewed=build_individual_analytics(store,initial.roster(),max_frame=16,fps=30)
        assert identity_only["accounting"]["attributed_shots"]==0
        assert reviewed["participants"]["loh"]["total_shots"]==1
        assert reviewed["participants"]["sen"]["total_shots"]==0
        assert engine._multi_person_identity_ambiguous is True
        assert store.get(stroke.event_id).actors.player_id is None and item.event.actors.player_id is None
        assert not store.query(types=["point"])
        reviewed_result={"latch_initial_and_after_reviews":True,"geometry_valid_frames":len(engine._geometry_valid),
                         "named_resolver_assign_calls":len(assign_calls),"identity_only_attributed":0,
                         "explicit_hitter_review_attributed":1,"machine_contact_actor":item.event.actors.player_id,
                         "machine_stroke_actor":store.get(stroke.event_id).actors.player_id,"accepted_points":0,
                         "identity_applied_to_machine_attribution":identity.payload["applied_to_attribution"],
                         "review_kind":scoped.type}
        store.close()
    scoring=[]
    for discipline in("singles","doubles"):
        for named in(True,False):
            with tempfile.TemporaryDirectory(prefix="score-slot-contract-probe-")as directory,pytest.MonkeyPatch.context()as monkeypatch:
                engine,store,names=late._engine(Path(directory),monkeypatch,discipline=discipline,
                                               player_names=None if named else {})
                assert engine._multi_person_identity_ambiguous is True
                late._finalize_unknown(engine,store)
                late._board(engine,500,(4,2),names)
                points=store.query(types=["point"])
                assert len(points)==int(named)
                assert engine._multi_person_identity_ambiguous is True
                assert (points[0].payload["winner"]if points else None)==("P1"if named else None)
                scoring.append({"format":discipline,"explicit_score_names":named,"latch_remains_true":True,
                                "accepted_points":len(points),"winner_score_slot":points[0].payload["winner"]if points else None,
                                "identity_or_hitter_review_supplied":False,"scope":"synthetic cached phase/unknown terminal; real OCR/rules/ledger"})
                store.close()
    if any(sha(path)!=digest for path,digest in hashes.items()):
        raise ValueError("Read-only probe source changed")
    return {"scope":"Synthetic model-free contracts, not benchmark or human-reviewed physical accuracy",
            "candidate_root":str(root),"candidate_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip(),
            "static_latch_assignments":assignments,"reviewed_individual_path":reviewed_result,"named_score_slot_cases":scoring,
            "production_source_unchanged":True,"latch_forced_false":False,"NN_performed":False,"live_database_opened":False,
            "Test3_accessed":False,"synthetic_review_assertions_are_real_GT":False,"input_sha256":hashes,"probe_sha256":sha(__file__)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pipeline-root",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args();result=audit(args.pipeline_root.resolve(strict=True))
    with args.output.open("x")as stream:json.dump(result,stream,indent=2);stream.write("\n")
    print(json.dumps({key:result[key]for key in("candidate_commit","reviewed_individual_path","named_score_slot_cases")},indent=2))


if __name__=="__main__":main()
