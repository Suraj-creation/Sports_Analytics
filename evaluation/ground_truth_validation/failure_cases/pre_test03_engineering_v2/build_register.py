"""Publish a NEW immutable engineering-evidence register, never inference or GT.

Inputs are closed prior reports/caches/prefix records. Current fresh worker state
is not opened. Reproduce into a new folder/version; do not overwrite outputs.
"""

from __future__ import annotations

# ruff: noqa: E501
import csv
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
WORK = ROOT / "evaluation/ground_truth_validation"
SCENE = WORK / "component_evaluations/pre_test03_scene_foreground_v1"
TEMP = WORK / "component_evaluations/pre_test03_temporal_v1"
IDENT = WORK / "component_evaluations/pre_test03_identity_v1"
PERCEPT = WORK / "component_evaluations/pre_test03_perception_v1"
OLD = WORK / "failure_cases/test_01_02_pre_test03_v1"
REFERENCES = {}
RECORDS = []
REQUIRED = (
    "Component",
    "Video",
    "TimestampFrame",
    "GroundTruth",
    "Prediction",
    "ErrorType",
    "RootCause",
    "Fix",
    "Validation",
)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(name, data):
    with (OUT / name).open("x") as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def ref(key, path, role, selector=None):
    path = Path(path).resolve()
    if key in REFERENCES:
        assert REFERENCES[key]["path"] == str(path)
        return key
    assert path.is_file(), path
    REFERENCES[key] = {
        "path": str(path),
        "sha256": sha(path),
        "bytes": path.stat().st_size,
        "role": role,
        "selector": selector,
    }
    return key


def read(key, path, role):
    ref(key, path, role)
    return json.loads(Path(path).read_text())


def previous_tree():
    return {
        str(p.relative_to(OLD)): sha(p) for p in sorted(OLD.rglob("*")) if p.is_file() and "__pycache__" not in p.parts
    }


def compact(row):
    evidence = row["raw_content"]
    return {
        "frame": row["frame"],
        "person_count": len(row["persons"]),
        "persons": [
            {"bbox": p["bbox"], "detector_matched": p["detector_matched"], "raw_episode_opaque": p["raw_track"]}
            for p in row["persons"]
        ],
        "outside_person_count": row["outside_person_count"],
        "foreground_count": len(row["foreground_regions"]),
        "foreground_regions": [
            {"key": p["key"], "detector_matched": p["detector_matched"], "bbox": p["bbox"]}
            for p in row["foreground_regions"]
        ],
        "raw_hypothesis": evidence["hypothesis"],
        "supporting_region_keys": evidence.get("supporting_region_keys", []),
        "raw_reasons": evidence["reasons"],
        "layout_decision": row["decision"]["decision"] if row["decision"] else None,
        "barrier": row["barrier"],
        "detector_observed": row["detector_observed"],
        "episode_scope": "Opaque machine episode records; not physical identities or roster names.",
    }


def add(
    case_id,
    group,
    component,
    tests,
    frames,
    error,
    cause,
    fix,
    expectation,
    evidence,
    *,
    prediction=None,
    reference=None,
    aliases=(),
    counts=None,
    scope=None,
):
    frame = None if frames is None else frames[0]
    RECORDS.append(
        {
            "case_id": case_id,
            "group": group,
            "related_issue_ids": list(aliases),
            "Component": component,
            "Video": {"tests": tests, "source_media_ids": [f"TEST{t}_MEDIA" for t in tests]},
            "TimestampFrame": {
                "frame": frame,
                "frames": frames,
                "seconds": None if frame is None else frame / 30,
                "timebase": "zero-origin canonical CFR30/1; listed frames inclusive; separate intervals explicitly half-open",
                "not_applicable_reason": "Component-level contract across singles/doubles, not one physical source instant"
                if frames is None
                else None,
            },
            "GroundTruth": None,
            "diagnostic_expectation": {
                "basis": "software_contract"
                if frames is None
                else "agent_reviewed_source_diagnostic_and_machine_contract",
                "physical_ground_truth": False,
                "text": expectation,
            },
            "supplied_reference": reference,
            "Prediction": prediction,
            "ErrorType": error,
            "RootCause": cause,
            "Fix": fix,
            "Validation": {
                "scope": scope
                or "Focused software/source-prefix evidence; no physical accuracy or full fresh acceptance claimed.",
                "full_fresh_Test1_status": "pending; final c585e35 fresh inference running at publication",
                "full_fresh_Test2_status": "pending",
                "success_from_unit_execution_alone": False,
                "next_gate": "Completed source-native fresh Test1 and Test2, unchanged original evaluators/all annotations, source-bound visual checks and preserved before/after outputs.",
            },
            "evidence_refs": evidence,
            "measured_extent": counts,
            "frequency_scope": "Only enumerated observations; no prevalence or aggregate physical accuracy inferred.",
        }
    )


def main():
    assert not (OUT / "cases.json").exists(), "Use a new register version"
    old_before = previous_tree()
    snapshots = OUT / "source_snapshots"
    snapshots.mkdir()
    spec = WORK / "reports/test_01_02_root_cause_and_improvement_spec.md"
    snapshot = snapshots / "root_cause_SPEC_at_publication.md"
    snapshot.open("xb").write(spec.read_bytes())
    ref(
        "SPEC_SNAPSHOT",
        snapshot,
        "Point-in-time copy of mutable root-owned SPEC; canonical D01/D02 identities and fresh-pending scope",
    )
    spec_origin = {
        "path": str(spec),
        "sha256_at_copy": sha(snapshot),
        "current_origin_required_unchanged": False,
        "reason": "Root owns ongoing status; immutable copied bytes are validated instead.",
    }
    ref("OLD_V1_FREEZE", OLD / "freeze_receipt.json", "Previous v1 engineering/rally review preserved, not rewritten")
    read(
        "OLD_COMPONENTS",
        OLD / "component_cases.json",
        "Prior17 separate component cases; no inflation of53 packaged rally cases",
    )
    s1 = read(
        "PREFIX_V1_SUMMARY",
        SCENE / "prefix_v1/summary.json",
        "Closed initial7ed2f73 chronological source trial; failed7857 acceptance",
    )
    s2 = read(
        "PREFIX_V2_SUMMARY",
        SCENE / "prefix_v2/summary.json",
        "Closed5b6d429 chronological source trial; bounded acceptance only",
    )
    assert s1["status"] == s2["status"] == "completed_bounded_scene_foreground_probe"
    for version in [1, 2]:
        folder = SCENE / f"prefix_v{version}"
        for name, label in [
            ("artifact_receipt.json", "ARTIFACTS"),
            ("source_commit_receipt.json", "SOURCE"),
            ("executed_probe.py", "HELPER"),
        ]:
            ref(
                f"PREFIX_V{version}_{label}",
                folder / name,
                "Exact closed prefix output, executed helper and candidate source provenance",
            )
    ref(
        "CONTROL_PARITY",
        SCENE / "prefix_v2/control_parity_receipt.json",
        "Exact per-row unchanged original/c7 control parity across all10 windows",
    )
    ref("SCENE_REPORT", SCENE / "REPORT.md", "Bounded scene diagnosis, scope and all10 windows")
    ref(
        "SCENE_VERIFY",
        SCENE / "verification_receipt_v2.json",
        "Closed bounded-source/artifact verification, not full acceptance",
    )
    ref("SCENE_TESTS", SCENE / "final_focused_tests/source_receipt.json", "Exact5b6d429 committed new test sources")
    ref(
        "SCENE_GREEN",
        SCENE / "ambiguity_recovery_GREEN.log",
        "Root177 focused tests, separate from physical validation",
    )
    ref(
        "AMBIG_RED",
        SCENE / "ambiguity_recovery_RED.log",
        "Genuine pre-fix3 failing missing-context/reacquisition contracts",
    )
    ref(
        "LAYOUT_RED",
        SCENE / "raw_layout_continuity_RED.log",
        "Genuine raw-layout/participant-admission coupling failures",
    )
    ref(
        "SCENE_SOURCE",
        SCENE / "prefix_v2/executed_candidate_commit/sports/badminton/src/bai_badminton/perception/scene_change.py",
        "Exact executedV3 witness implementation at5b6d429",
    )
    ref(
        "FG_SOURCE",
        SCENE / "prefix_v2/executed_candidate_commit/sports/badminton/src/bai_badminton/perception/foreground.py",
        "Exact executed bounded scene-only memory; no player authority",
    )
    ref(
        "ENGINE_SOURCE",
        SCENE / "prefix_v2/executed_candidate_commit/sports/badminton/src/bai_badminton/engine.py",
        "Exact preserved engine source with typed temporal composition correction",
    )
    ref(
        "PLUGIN_SOURCE",
        SCENE / "prefix_v2/executed_candidate_commit/sports/badminton/src/bai_badminton/plugin.py",
        "Exact preserved capability reporting implementation",
    )
    for name in ["test_player_foreground.py", "test_scene_witness_v3.py", "test_pipeline_foreground.py"]:
        ref(name, SCENE / "final_focused_tests" / name, "Exact committed focused regression test")
    ref(
        "C7_CASES",
        WORK / "regression_tests/pre_test03_v1/test01_independent_review/structured_failure_cases.json",
        "Actual completed c7 fresh-run failed source controls",
    )
    ref(
        "C7_LEASE",
        WORK / "regression_tests/pre_test03_v1/test01_independent_review/scene_lease_diagnostics.json",
        "Native court/lease reconstruction; private timestamps explicitly unpersisted",
    )
    data = {}
    for version in [1, 2]:
        for test, start, end in [
            (1, 7650, 8150),
            (2, 5505, 6510),
            (2, 11300, 11360),
            (2, 7640, 7740),
            (2, 23570, 23680),
        ]:
            key = f"V{version}_T{test}_{start}_{end}"
            data[version, test, start] = read(
                key,
                SCENE / f"prefix_v{version}/test{test}_{start:05d}_{end:05d}.json",
                "Closed source/PTS/pixel-bound chronological raw proposal and all-arm scene/player evidence",
            )

    def state(version, test, start, frame, arm="foreground"):
        return compact(data[version, test, start]["variants"][arm][frame - start])

    media = {}
    for test, start in [(1, 7650), (2, 5505)]:
        packet = data[2, test, start]
        key = f"TEST{test}_MEDIA"
        source = (
            ROOT.parent / "ground-truth-validation-artifacts-20261110" / f"test_0{test}/improved_v1/run/inference.json"
        )
        info = read(key, source, "Completed original worker media/source/proxy identity; no large source video reread")
        assert packet["source_sha256"] == info["source_sha256"] and packet["proxy_sha256"] == info["proxy_sha256"]
        media[key] = {
            "test": test,
            "source_sha256": info["source_sha256"],
            "proxy_sha256": info["proxy_sha256"],
            "fps_num": 30,
            "fps_den": 1,
            "large_raw_accessed": False,
            "origin_worker_ref": key,
        }
    for test, start, end, frames in [
        (1, 7650, 8150, [7857, 7858, 7859, 8106, 7800, 7801, 7856, 8105]),
        (2, 5505, 6510, [5958, 6307, 6492]),
        (2, 11300, 11360, [11346]),
        (2, 7640, 7740, [7703]),
        (2, 23570, 23680, [23639]),
    ]:
        for frame in frames:
            ref(
                f"PNG_T{test}_{frame}",
                SCENE / f"prefix_v2/test{test}_{start:05d}_{end:05d}_frame_{frame:05d}.png",
                "Exact three-arm source panel; source frame/PTS/pixels bound in corresponding JSON",
            )
    scene_fix = {
        "status": "implemented; focused and bounded source validation only",
        "implementation_commits": [
            "7ed2f731e2d58273e381710226500f30d47e00bb",
            "5b6d429b277e60837146ee02361a9961076079b6",
        ],
        "description": "Separate court-origin image context from participant admission; explicit>=2 independent source witnesses; raw-layout positive veto; bounded ambiguous missing context; versioned dependent caches.",
        "unchanged": "Court authority lease, numeric thresholds, model/checkpoint and annotation/evaluation rules unchanged.",
    }
    for frame in [7857, 8106]:
        add(
            f"ENG2-SCENE-T1-{frame}",
            "confirmed_engineering",
            "Scene continuity / target-court input composition",
            [1],
            [frame],
            "missed_source_edit_after_court_authority_expiry",
            "Scene input was built only from admitted persons. A real offcourt athlete lost authority and also disappeared from scene evidence; fewer than2 prior regions prevented acquisition. At7857 detector cadence carries an old box;8106 fresh cadence happens to replace it without content reset.",
            scene_fix,
            "An agent-reviewed same-camera edit should obtain independent image evidence and current-layout corroboration; athlete authority must remain withheld outside its lease.",
            [
                "C7_CASES",
                "C7_LEASE",
                "V1_T1_7650_8150",
                "V2_T1_7650_8150",
                f"PNG_T1_{frame}",
                "SCENE_SOURCE",
                "FG_SOURCE",
                "SCENE_TESTS",
                "SCENE_GREEN",
                "PREFIX_V2_SOURCE",
            ],
            prediction={
                "original_prefix": state(2, 1, 7650, frame, "original"),
                "c7_prefix": state(2, 1, 7650, frame, "c7"),
                "scene_v1": state(1, 1, 7650, frame),
                "scene_v2": state(2, 1, 7650, frame),
            },
            aliases=["SCENE-CONTEXT", "ENG2-STALE-T1-7857_7859"],
            counts={
                "source_confirmed_removed_c7_barriers": [7857, 8106],
                "before_barriers_full_Test1": 13,
                "c7_barriers_full_Test1": 11,
                "not_total_true_edit_count": True,
            },
        )
    add(
        "ENG2-FG-T1-7806_7812",
        "confirmed_engineering",
        "Scene-only image-context missing/reacquisition",
        [1],
        [7806, 7812],
        "transient_ambiguous_match_permanently_deletes_court_origin_context",
        "At7806 both athlete(.636083IoU) and official(.360303) overlap the old image box. Initial memory deletes its key. At7812 athlete.558191/official.216148 is unique, but an offcourt actor cannot reseed a deleted court-origin key.",
        scene_fix,
        "Treat ambiguous image correspondence as bounded missing evidence: no box/time/authority renewal; allow later unique reacquisition before expiry; never turn image keys into physical identity.",
        [
            "V1_T1_7650_8150",
            "V2_T1_7650_8150",
            "FG_SOURCE",
            "AMBIG_RED",
            "SCENE_GREEN",
            "test_player_foreground.py",
            "PREFIX_V1_SOURCE",
            "PREFIX_V2_SOURCE",
        ],
        prediction={
            "initial7806": state(1, 1, 7650, 7806),
            "initial7812": state(1, 1, 7650, 7812),
            "final7806": state(2, 1, 7650, 7806),
            "final7812": state(2, 1, 7650, 7812),
        },
        aliases=["FG-AMBIGUITY", "ENG2-SCENE-T1-7857"],
        counts={"demonstrated_ambiguous_event": 1, "reacquisition_gap_frames": 6, "prevalence_unknown": True},
    )
    add(
        "ENG2-STALE-T1-7857_7859",
        "confirmed_dependent_effect",
        "Player carry / content-boundary reset",
        [1],
        [7857, 7858, 7859],
        "old_observation_carried_on_visibly_empty_new_source_region",
        "Dependent effect of missed7857 content acquisition plus idle detector stride6. The near box from7854 remains in empty rightcourt until the next scheduled detector7860; opaque episode IDs do not establish identity truth.",
        scene_fix,
        "Reset source-incompatible carry from independent observed image change, force a current detector acquisition and preserve detector_matched provenance.",
        [
            "C7_CASES",
            "V2_T1_7650_8150",
            "PNG_T1_7857",
            "PNG_T1_7858",
            "PNG_T1_7859",
            "test_pipeline_foreground.py",
            "PREFIX_V2_ARTIFACTS",
        ],
        prediction={
            "c7": [state(2, 1, 7650, f, "c7") for f in [7857, 7858, 7859]],
            "final": [state(2, 1, 7650, f) for f in [7857, 7858, 7859]],
        },
        aliases=["SCENE-CONTEXT", "ENG2-SCENE-T1-7857"],
        counts={"exact_visually_reviewed_stale_frames": 3, "independent_failure_count_increment": 0},
    )
    for key, name in [
        ("6151_REVIEW", "REPORT.md"),
        ("6151_RECEIPT", "verification_receipt.json"),
        ("6151_DECISION", "decision_evidence.json"),
        ("6150_SOURCE", "frame_06150_source.png"),
        ("6151_SOURCE", "frame_06151_source.png"),
    ]:
        ref(
            key,
            SCENE / "independent_review_6151_v1" / name,
            "Independent source-bound review of real6150→6151 edited jump, not a new rally/winner label",
        )
    add(
        "ENG2-SCENE-T2-6151",
        "confirmed_engineering",
        "Scene multi-region innovation with static context",
        [2],
        [6151],
        "static_extra_region_vetoes_independent_athlete_source_change",
        "Original all-region conjunction includes a static official with insufficient features, suppressing two independently changed athlete regions. Exact source layout and broadcast10:13→10:14 show an edited jump; source change is not a point-to-rally identity decision.",
        scene_fix,
        "Retain all telemetry; require>=2 independently qualified nonoverlapping witnesses per channel, not every static extra region; current raw detector corroborates discontinuous layout.",
        [
            "V1_T2_5505_6510",
            "V2_T2_5505_6510",
            "6151_REVIEW",
            "6151_RECEIPT",
            "6151_DECISION",
            "6150_SOURCE",
            "6151_SOURCE",
            "SCENE_SOURCE",
            "test_scene_witness_v3.py",
            "PREFIX_V2_SOURCE",
        ],
        prediction={
            "original": state(2, 2, 5505, 6151, "original"),
            "c7": state(2, 2, 5505, 6151, "c7"),
            "final": state(2, 2, 5505, 6151),
        },
        aliases=["SCENE-CONTEXT"],
        counts={"new_independently_reviewed_source_edit_in_this_window": 1, "exhaustive_scene_recall_unknown": True},
    )
    ref(
        "PERCEPTION_REPORT",
        PERCEPT / "REPORT.md",
        "Two distinct birth and court-authority defects, exact detector observations and chronological controls",
    )
    ref(
        "PERCEPTION_RECEIPT",
        PERCEPT / "verification_receipt_final.json",
        "Closed121-test/7-prefix source-bound tracking validation; not full NN acceptance",
    )
    ref(
        "BIRTH_TEST",
        SCENE / "prefix_v2/executed_candidate_commit/sports/badminton/src/bai_badminton/perception/_bytetrack.py",
        "Exact observed-first-birth adapter implementation",
    )
    ref(
        "PLAYER_SOURCE",
        SCENE / "prefix_v2/executed_candidate_commit/sports/badminton/src/bai_badminton/perception/players.py",
        "Exact target-court lease and separate foreground integration",
    )
    common = [
        "PERCEPTION_REPORT",
        "PERCEPTION_RECEIPT",
        "V2_T2_5505_6510",
        "PNG_T2_5958",
        "PNG_T2_6492",
        "PLAYER_SOURCE",
        "PREFIX_V2_SOURCE",
    ]
    add(
        "ENG2-AUTH-T2-6492",
        "confirmed_engineering",
        "Court-origin participant authority lease",
        [2],
        [5958, 6492],
        "outside_detection_renews_its_own_court_authority",
        "After overlapping athlete→official handover, the old rolling outside continuity timestamp renews on every matched official observation. Spatial correspondence was conflated with actual last in-court authority.",
        {
            "status": "implemented; source-prefix/focused verified; final fresh acceptance pending",
            "canonical_issue": "D04",
            "description": "Keep last fresh positively in-court timestamp separate from latest moving box; expire on carries too, without changing the one-second allowance.",
        },
        "Exclude seated official from player evidence while preserving uniquely supported short jumps/runoff. A scene-only visual episode may persist without athlete/team authority.",
        common,
        prediction={
            "original6492": state(2, 2, 5505, 6492, "original"),
            "strict_lease6492": state(2, 2, 5505, 6492, "c7"),
            "separate_visual6492": state(2, 2, 5505, 6492),
        },
        aliases=["D04", "PERCEPTION-01"],
        counts={"two_reviewed_handover_focus_instants": [5958, 6492], "video_prevalence_unknown": True},
    )
    add(
        "ENG2-BIRTH-T2-6492",
        "confirmed_engineering",
        "Player detection→ByteTrack birth integration",
        [2],
        [6492],
        "eligible_initial_current_observation_dropped_by_backend_birth_contract",
        "Exact RFDETR proposals already contain both athletes. Wrapper discards first eligible observations because upstream backend exposes an unassigned ID until another match despite configured minimum1. Detector confidence is not the missing-near cause.",
        {
            "status": "implemented; deterministic and chronological source verified; final fresh pending",
            "canonical_issue": "D03",
            "description": "Narrow adapter counts initial detection as an observation without changing association, allocation or confidence thresholds.",
        },
        "Emit eligible first observed athlete boxes with fresh source stamps; this is detection availability, not named identity/AP/HOTA verification.",
        [*common, "BIRTH_TEST"],
        prediction={"original6492": state(2, 2, 5505, 6492, "original"), "candidate6492": state(2, 2, 5505, 6492)},
        aliases=["D03", "PERCEPTION-01", "ENG2-AUTH-T2-6492"],
        counts={"paired_reviewed_missing_near_instant": 1, "same_instant_has_distinct_D04_authority_failure": True},
    )
    add(
        "ENG2-BIRTH-T2-11346",
        "confirmed_with_inherited_limitation",
        "Immediate track birth / cold scene-context acquisition",
        [2],
        [11346],
        "fresh_athlete_boxes_available_but_original_birth_output_empty",
        "Current detector proposes both athletes at the source edit; original backend first-hit behavior returns neither until a later tick. Correct birth does not itself supply historical two-region scene context.",
        {
            "status": "birth availability bounded-source verified; full scene behavior pending",
            "canonical_issue": "D03",
            "description": "Honor first-observation activation; retain independent source-continuity uncertainty rather than calling an ID change an edit.",
        },
        "Recover both current detected athletes immediately. Separately evaluate content acquisition with genuine prior court-origin memory; this11300-start prefix may begin with an already-offcourt actor.",
        [
            "PERCEPTION_REPORT",
            "PERCEPTION_RECEIPT",
            "V2_T2_11300_11360",
            "PNG_T2_11346",
            "BIRTH_TEST",
            "PREFIX_V2_SOURCE",
        ],
        prediction={
            "original": state(2, 2, 11300, 11346, "original"),
            "birth_corrected": state(2, 2, 11300, 11346, "c7"),
            "scene_final_bounded": state(2, 2, 11300, 11346),
        },
        aliases=["D03", "SCENE-01"],
        counts={"demonstrated_birth_restoration_focus": 1, "full_scene_acquisition_gain_not_established": True},
        scope="Bounded11300–11360 startup; no pre11300 court-origin visual memory. No full-video scene-performance inference.",
    )
    for frame, start, end in [(7703, 7640, 7740), (23639, 23570, 23680)]:
        r = state(2, 2, start, frame)
        add(
            f"CTRL2-T2-{frame}",
            "regression_control",
            "Scene continuity false-reset protection",
            [2],
            [frame],
            "negative_control_not_failure",
            "Natural same-camera appearance/pose change must not automatically reset tracking. Raw image hypotheses and positive current-layout continuity are separate evidence.",
            {
                "status": "safety control preserved in bounded final trial",
                "description": "V3 needs independent witnesses; complete injective correspondence of supporting image regions vetoes a reset even outside participant admission.",
            },
            "No content reset on this source-reviewed uninterrupted sequence; do not turn a model hypothesis into edit GT.",
            [
                f"V2_T2_{start}_{end}",
                f"PNG_T2_{frame}",
                "SCENE_REPORT",
                "CONTROL_PARITY",
                "LAYOUT_RED",
                "test_scene_witness_v3.py",
                "PREFIX_V2_ARTIFACTS",
            ],
            prediction={
                "final": r,
                "distinction": "No independent raw witness quorum; no layout decision in this bounded startup."
                if frame == 7703
                else "Raw two-witness hypothesis; explicit complete-current-layout no_barrier veto.",
            },
            counts={"checked_control_frame": 1, "failures_contributed": 0, "scene_false_positive_rate_unknown": True},
        )
    temporal = read(
        "TEMP_RECEIPT",
        TEMP / "candidate_receipt_v2.json",
        "Closed deterministic RED/GREEN and array-diagnostic source/test receipts",
    )
    for key, name in [
        ("TEMP_REPORT", "REPORT.md"),
        ("TEMP_RED", "expanded_contract_RED.log"),
        ("TEMP_GREEN", "focused_GREEN_v2.log"),
        ("TEMP_PATCH", "candidate_engine_only.patch"),
        ("TEMP_TEST", "test_missing_association_reconstruction.py"),
    ]:
        ref(key, TEMP / name, "Temporal provenance contract reproduction; no inferred physical trajectory labels")
    windows = {}
    for test in [1, 2]:
        doc = read(
            f"TEMP_T{test}_WINDOW",
            TEMP / f"test0{test}_cache_window_review_v1.json",
            "Full retained-array window diagnostic; not full streaming engine replay or fresh NN",
        )
        windows[f"Test{test}"] = {
            k: doc[k]
            for k in [
                "frames",
                "old_reconstructed_frames",
                "candidate_reconstructed_frames",
                "existing_continuation_supported_groups",
                "existing_continuation_supported_frames",
                "observed_mask_difference_count",
            ]
        }
    add(
        "D01",
        "confirmed_engineering",
        "Temporal raw-observation/reconstruction composition",
        [1, 2],
        None,
        "valid_raw_missing_erases_separately_marked_reconstructed_context",
        "Modern typed status!=observed cleared both vis and interp after bounded postprocessing. Ordinary valid raw absence was treated like contradictory/invalid/rejected evidence; equivalent legacy data retained estimated context.",
        {
            "status": "implemented;204 focused tests and retained-array diagnostics verified; fresh integration pending",
            "description": "Preserve explicitly reconstructed ordinary missing context; add private barriers before/after ambiguous/invalid/rejected/temporally invalid evidence. Keep observed-only contacts/speeds and benchmark use_reconstruction=False unchanged.",
        },
        "Preserve estimated provenance independently of raw missing observations; never call interpolated coordinates observed shuttle, contact, landing or physical truth.",
        [
            "SPEC_SNAPSHOT",
            "TEMP_REPORT",
            "TEMP_RECEIPT",
            "TEMP_RED",
            "TEMP_GREEN",
            "TEMP_PATCH",
            "TEMP_TEST",
            "TEMP_T1_WINDOW",
            "TEMP_T2_WINDOW",
            "ENGINE_SOURCE",
        ],
        prediction=windows,
        aliases=["D01", "COMPOSITION-01"],
        counts={
            "new_regression_tests": temporal["new_tests"],
            "focused_tests_passed": temporal["focused_tests_passed"],
            "full_observed_mask_changes": 0,
            "physical_recovered_detection_count": None,
        },
        scope="Model-free exact RED/GREEN plus full retained-array context diagnostics; no full cached streaming replay was performed or guard bypassed.",
    )
    ident = read(
        "IDENT_RECEIPT",
        IDENT / "receipt.json",
        "Closed capability-reporting RED/GREEN; no installed checkpoint or identity/accuracy gain",
    )
    for key, name in [
        ("IDENT_REPORT", "REVIEW.md"),
        ("IDENT_RED", "red_v2_effective_choices.log"),
        ("IDENT_GREEN", "green_v2.log"),
        ("IDENT_ARCH", "architecture_audit.md"),
        ("IDENT_ARCH_RECEIPT", "architecture_audit_receipt.json"),
    ]:
        ref(
            key,
            IDENT / name,
            "Appearance capability reporting and explicit unbound identity/scoring architecture scope",
        )
    add(
        "D02",
        "confirmed_engineering",
        "Appearance component capability/failure reporting",
        [1, 2],
        None,
        "real_loader_failure_overwritten_by_false_format_disabled_reason",
        "Singles/unknown format overwrote an actual checkpoint/CUDA loader failure with doubles-only disabled messaging, despite explicitly configured provider capability for singles/unknown.",
        {
            "status": "reporting fix focused verified; no tracking accuracy gain claimed",
            "description": "Preserve effective request and actual construction failure; distinguish intentional omitted default from failed load. No checkpoint installed or roster/track binding inferred.",
        },
        "Report actual capability and missing-model/provider reason; unbound athletes, review-ledger names and scoring rows remain distinct. Missing physical identity labels stay unknown.",
        [
            "SPEC_SNAPSHOT",
            "IDENT_RECEIPT",
            "IDENT_REPORT",
            "IDENT_RED",
            "IDENT_GREEN",
            "IDENT_ARCH",
            "IDENT_ARCH_RECEIPT",
            "PLUGIN_SOURCE",
        ],
        prediction={
            "red_failures": ident["red_failures"],
            "red_passed": ident["red_passed"],
            "green_focused_contracts": ident["green_focused_and_contract_passed"],
            "physical_accuracy_gain_claimed": False,
            "model_installed": False,
        },
        aliases=["D02", "IDENTITY-01"],
        counts={"focused_reporting_cases": 9, "physical_identity_accuracy": None},
        scope="Capability/API contract, not a temporal source event; D02 is appearance reporting in the canonical SPEC, not a second temporal defect.",
    )
    register = read(
        "TEMPORAL_REGISTER",
        WORK / "test_02/diagnostics/temporal_root_cause/case_register.json",
        "Completed original source-bound semantic case register; generated reference disagreement",
    )
    g69 = next(c for c in register["cases"] if c["case_id"] == "gt_069")
    for key, path in [
        ("G69_REPORT", WORK / "test_02/diagnostics/temporal_root_cause/REPORT.md"),
        ("G69_RAW", WORK / "test_02/diagnostics/current_scene_and_ocr_review/g69_gap_extended/REVIEW.md"),
        ("G69_BOUND", WORK / "test_02/diagnostics/current_scene_and_ocr_review/completed_snapshot_binding.json"),
        (
            "G69_PNG",
            WORK
            / "test_02/diagnostics/current_scene_and_ocr_review/g69_gap_extended/frame_27348_current_prefix_overlay.png",
        ),
    ]:
        ref(key, path, "Retained raw gap/branch source evidence; prefix observations separately bound to completed run")
    csv_path = ROOT / "Part2/dataset/Test2_Full/Test2_Full_rally.csv"
    ref(
        "G69_CSV",
        csv_path,
        "Original immutable legacy-generated rally intervals; not independent shuttle/contact/outcome truth",
        {"data_row": 69, "csv_line": 70},
    )
    with csv_path.open(newline="", encoding="utf-8-sig") as stream:
        raw_rows = list(csv.DictReader(stream))
    row = raw_rows[68]
    assert [int(row["Start_Frame"]), int(row["End_Frame"])] == [26616, 27668]
    add(
        "I-G69",
        "inherited_unresolved",
        "Raw shuttle acquisition / branch selection / rally continuity",
        [2],
        [27326, 27347, 27348, 27354],
        "raw_shuttle_absence_then_branch_ambiguity_and_interval_split",
        "22 raw-absent frames precede association: not a veto of accepted raw coordinates. Reacquisition27348 is23frames after tentative end27325, beyond unchanged merge22; publication follows existing state machine. Lower branch may be racket/head/hand distractor, not adjudicated shuttle truth.",
        {
            "status": "unresolved; no timeout/threshold/trajectory fabrication",
            "description": "D01 repairs optional estimated context only. Benchmark use_reconstruction=False remains false; investigate raw high-clear coverage and competing branches under separately reviewed labels before any new policy trial.",
        },
        "Preserve measured split/reference disagreement and uncertainty. Source movement suggests continuing activity but does not locate the true shuttle or certify an unconditional merge/contact/winner.",
        [
            "TEMPORAL_REGISTER",
            "G69_REPORT",
            "G69_RAW",
            "G69_BOUND",
            "G69_PNG",
            "G69_CSV",
            "TEMP_T2_WINDOW",
            "TEMP_REPORT",
        ],
        prediction={
            "supplied_reference_comparison": {
                "expected_reference": g69["expected_reference"],
                "actual_prediction": g69["actual_prediction"],
                "metrics": g69["metrics"],
            },
            "second_exported_interval_half_open": [27349, 27649],
            "raw_gap_half_open": [27326, 27348],
            "reacquisition_frame": 27348,
            "publication_frame": g69["prediction_finalization"]["frame"],
            "candidate_estimated_gap_observed": False,
        },
        reference={
            "basis": "supplied_legacy_generated_csv_not_physical_GT",
            "evidence_ref": "G69_CSV",
            "data_row": 69,
            "csv_line": 70,
            "raw_values": row,
            "frames_half_open": [26616, 27668],
        },
        aliases=["I03", "SHUTTLE-01", "SEGMENTATION-01", "gt_069", "pred_071"],
        counts={
            "raw_absent_frames_in_local_gap": 22,
            "below_threshold_retained_candidates": 15,
            "gap_frames_with_retained_candidates": 12,
            "gap_frames_without_retained_candidates": 10,
            "highest_retained_support": 0.220703125,
            "unchanged_decoder_threshold": 0.5,
            "measured_interval_case": 1,
        },
        scope="Existing completed original semantic replay and source diagnostics; not a corrected full-run result or labelled shuttle accuracy.",
    )
    assert len(RECORDS) == 13 and len({r["case_id"] for r in RECORDS}) == 13
    assert all(all(key in r for key in REQUIRED) for r in RECORDS)
    assert all(r["GroundTruth"] is None and not r["diagnostic_expectation"]["physical_ground_truth"] for r in RECORDS)
    assert all(e in REFERENCES for r in RECORDS for e in r["evidence_refs"])
    rankings = [
        {
            "rank": 1,
            "issue": "D03/D04 athlete availability and court authority",
            "measured_basis": "Two explicit reviewed birth-restoration examples6492/11346; distinct6492 authority handover. No video-wide miss or identity rate.",
            "records": ["ENG2-BIRTH-T2-6492", "ENG2-AUTH-T2-6492", "ENG2-BIRTH-T2-11346"],
        },
        {
            "rank": 2,
            "issue": "Scene-context/foreground-memory integration",
            "measured_basis": "Two lost Test1 barriers and one dependent3-frame stale carry, plus one independently reviewed6151 source edit. Causal records are not independent frequency counts.",
            "records": [
                "ENG2-SCENE-T1-7857",
                "ENG2-SCENE-T1-8106",
                "ENG2-FG-T1-7806_7812",
                "ENG2-STALE-T1-7857_7859",
                "ENG2-SCENE-T2-6151",
            ],
        },
        {
            "rank": 3,
            "issue": "I-G69 raw gap/branch ambiguity",
            "measured_basis": "One generated-reference split with22 local raw-absent frames; current physical shuttle branch and exact boundaries unreviewed.",
            "records": ["I-G69"],
        },
        {
            "rank": 4,
            "issue": "D01 provenance contract",
            "measured_basis": "All-array diagnostics17268/29296 frames, zero observed-mask differences; optional estimated context only, benchmark reconstruction remains disabled.",
            "records": ["D01"],
        },
        {
            "rank": 5,
            "issue": "D02 truthful capability reporting",
            "measured_basis": "Nine focused reporting scenarios; no physical identity/score accuracy gain.",
            "records": ["D02"],
        },
    ]
    document = {
        "schema": "pre-test03-engineering-failure-cases:v2",
        "created_utc": datetime.now(UTC).isoformat(),
        "records_immutable": True,
        "scope": "Engineering diagnostics and controls only; no newGT/AP/aggregate physicalaccuracy; original CSVs/evaluators/baselines untouched; no Test3 access.",
        "required_case_fields": REQUIRED,
        "case_count": 13,
        "causal_record_count_is_not_failure_frequency": True,
        "physical_ground_truth_case_count": 0,
        "full_fresh_final_candidate_status": {
            "candidate": "c585e35",
            "Test1": "running at publication; acceptance pending",
            "Test2": "pending",
            "later_results": "Append a NEW receipt/version; never rewrite this immutable case database.",
        },
        "media": media,
        "groups": {
            "confirmed_engineering_or_dependent_example_records": 10,
            "regression_controls": 2,
            "inherited_unresolved": 1,
        },
        "priority_ranking": rankings,
        "cases": RECORDS,
    }
    save("cases.json", document)
    save("evidence_index.json", {"evidence": REFERENCES, "mutable_SPEC_origin_snapshot": spec_origin})
    save(
        "old_v1_preservation.json",
        {
            "old_root": str(OLD),
            "files_sha256": old_before,
            "old_tree_unchanged_after_build": old_before == previous_tree(),
        },
    )
    assert old_before == previous_tree()
    with (OUT / "case_summary.csv").open("x", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "Case",
                "Component",
                "Video",
                "Timestamp/Frame",
                "GroundTruth",
                "Prediction",
                "ErrorType",
                "RootCause",
                "Fix",
                "Validation",
            ],
        )
        writer.writeheader()
        for r in RECORDS:
            writer.writerow(
                {
                    "Case": r["case_id"],
                    "Component": r["Component"],
                    "Video": ",".join(map(str, r["Video"]["tests"])),
                    "Timestamp/Frame": "N/A"
                    if r["TimestampFrame"]["frame"] is None
                    else ",".join(map(str, r["TimestampFrame"]["frames"])),
                    "GroundTruth": "unavailable; null in JSON",
                    "Prediction": "See compact before/after in cases.json; exact evidence_index links",
                    "ErrorType": r["ErrorType"],
                    "RootCause": r["RootCause"],
                    "Fix": r["Fix"]["description"],
                    "Validation": r["Validation"]["scope"] + " Full final fresh Test1/Test2 pending.",
                }
            )

    def link(key):
        item = REFERENCES[key]
        return f"[{key}]({item['path']})"

    lines = [
        "# Pre-Test 3 engineering failure register v2",
        "",
        "Thirteen records preserve confirmed software mechanisms, their dependent effects, two safety controls and the unresolved G69 limitation. Every `GroundTruth` field is `null`: source review and synthetic contract expectations are explicitly separate from original CSV/generated references. The CSV is a navigation summary; the JSON contains the complete structured fields and measured before/after outputs.",
        "",
        "Final candidate `c585e35` fresh Test 1 inference is running at publication; full Test 1 acceptance and Test 2 regression remain **pending**. Focused tests and bounded source controls establish their stated contracts, not full pipeline or physical accuracy. Publish future results in a new receipt/version; do not rewrite this database.",
        "",
        "[Structured records](cases.json) · [Evidence paths, hashes and selectors](evidence_index.json) · [Compact CSV](case_summary.csv) · [Preserved v1 tree](old_v1_preservation.json)",
        "",
        "## Ranked priorities and measured extent",
        "",
        "| Priority | Issue | Measured basis; no prevalence inference |",
        "|---|---|---|",
    ]
    for r in rankings:
        lines.append(f"| {r['rank']} | {r['issue']} | {r['measured_basis']} |")
    lines += [
        "",
        "D01 is temporal provenance. D02 is appearance capability reporting, as in the preserved canonical SPEC; both have no applicable physical frame. Opaque track IDs identify machine episodes, never named players or edit truth. Dependent stale-box and scene/ambiguity records share causal chains and must not be summed as independent failure frequency.",
        "",
        "## Confirmed mechanisms, limitations and controls",
        "",
    ]
    for r in RECORDS:
        frames = r["TimestampFrame"]["frames"]
        when = (
            "N/A — component/API contract, not a single video instant"
            if frames is None
            else ", ".join(f"{f} ({f / 30:.3f}s)" for f in frames)
        )
        # Full numeric structures stay in JSON; no raw arrays in Markdown cells.
        if r["case_id"] == "D01":
            summary = "Retained-array reconstructed context1→827 samples in Test1;9→2204 in Test2; observed-mask differences0. This is derived-context availability, not recovered detections."
        elif r["case_id"] == "D02":
            summary = "Six original failing/nine reporting cases; candidate focused contracts pass. No checkpoint installed or physical identity gain claimed."
        elif r["case_id"] == "I-G69":
            summary = "Supplied reference[26616,27668); first prediction[26654,27325), second[27349,27649). Original comparisonIoU0.637833, start+38/end−343frames; local raw gap22frames. These are generated-reference metrics, not physical accuracy."
        elif r["group"] == "regression_control":
            summary = r["Prediction"]["distinction"] + " Final barrier=false."
        elif "7806" in r["case_id"]:
            summary = "Initial memory loses the far context permanently at ambiguous7806. Final retains it unmatched at7806 and uniquely reacquires7812 with no participant-authority renewal."
        elif "STALE" in r["case_id"]:
            summary = "c7 carries one old box over7857–7859; final prefix has two current7857 detections, then explicitly unobserved carries on7858–7859."
        elif "6151" in r["case_id"]:
            summary = "Original/c7 no barrier; both new scene trials barrier6151. Independent exact-source review confirms an edited jump; no winner label is created."
        elif "AUTH" in r["case_id"]:
            summary = "Original6492 contains far athlete plus outside official; strict-lease/final prefixes contain the two current athletes and no outside participant."
        elif "11346" in r["case_id"]:
            summary = "Original returns0persons; birth-corrected and final bounded arms return2. No content barrier in this11300-start window; full prior-memory scene behavior is unresolved."
        elif "BIRTH" in r["case_id"]:
            summary = "Raw model already proposes both athletes; original drops the near birth, adapter restores current observations. Court-authority handover is a separate defect at the same instant."
        else:
            f = r["TimestampFrame"]["frame"]
            summary = f"Original prefix barrier=true; c7=false; final source-prefix barrier=true at{f}. Initial scene trial recovered8106 but missed7857; ambiguity correction completes the specified bounded control."
        lines += [
            f"### {r['case_id']}",
            "",
            f"**Component → Video → Timestamp/Frame:** {r['Component']} → Test "
            + ", ".join(map(str, r["Video"]["tests"]))
            + f" → {when}.",
            "",
            f"**GroundTruth:** unavailable (`null`). **Diagnostic expectation:** {r['diagnostic_expectation']['text']}",
            "",
            f"**Prediction:** {summary}",
            "",
            f"**ErrorType:** `{r['ErrorType']}`. **RootCause:** {r['RootCause']}",
            "",
            f"**Fix:** {r['Fix']['description']}",
            "",
            f"**Validation:** {r['Validation']['scope']} Full final fresh Test1/Test2 validation pending.",
            "",
            "Evidence: " + ", ".join(link(k) for k in r["evidence_refs"][:7]) + ".",
            "",
        ]
    lines += [
        "## Provenance and limits",
        "",
        "The closed prefix trials compare exact original dacc05e, c7cf871 and scene-only candidate implementations against the same source/crop-bound detector proposals with original recorded geometry/rate scheduling. Initial7ed2f73 trial executed282 previously unavailable crops; final5b6d429 trial reused911 distinct retained observations with2728 retained lookups and zero fresh NN calls. All10 windows/2399 chronological frames per arm have exact unchanged original/c7 control parity; zero foreground overflow was measured, maximum4 regions. These are bounded component diagnostics, not fresh end-to-end inference or doubles generalisation.",
        "",
        "The register reads only closed artifacts and the original G69 CSV row. No live worker caches, mutable event database, raw source videos, network, NN, current production source, annotations or original outputs were modified. Original v1 file hashes are checked before and after building. Selected evidence has exact paths/SHA256/bytes; prefix source copies and their receipts preserve executed code even when working trees evolve. A point-in-time SPEC copy avoids treating ongoing root status edits as immutable evidence.",
        "",
        "G69 retains `use_reconstruction=False`, the original decoder threshold and merge/gap policies. No accepted shuttle location, named identity, contact, stroke, rally winner, point score, AP/mAP/IDF1/HOTA/PCK/OKS or physical aggregate is manufactured. Frame-level agent review remains diagnostic. Original interval references retain their provenance and matching conventions.",
    ]
    (OUT / "README.md").open("x").write("\n".join(lines) + "\n")
    for target in re.findall(r"\]\(([^)]+)\)", (OUT / "README.md").read_text()):
        path = Path(target) if target.startswith("/") else OUT / target
        assert path.exists(), path
    save(
        "validation.json",
        {
            "status": "validated_structured_engineering_register",
            "case_count": 13,
            "all_required_fields": True,
            "all_physical_ground_truth_values_null": True,
            "old_v1_unchanged": True,
            "all_evidence_files_exist_and_hashed": True,
            "all_markdown_links_exist": True,
            "full_final_fresh_acceptance": False,
            "no_new_inference": True,
            "no_new_ground_truth": True,
            "no_Test3_access": True,
        },
    )
    save(
        "manifest.json",
        {
            "schema": "immutable-engineering-register-manifest:v2",
            "status": "published_scoped_engineering_register_full_fresh_pending",
            "created_utc": datetime.now(UTC).isoformat(),
            "artifact_sha256": {
                str(p.relative_to(OUT)): sha(p)
                for p in sorted(OUT.rglob("*"))
                if p.is_file() and "__pycache__" not in p.parts
            },
            "evidence_sha256": REFERENCES,
            "future_results": "Create NEWreceipt/version; do not modify this DB/README/manifest.",
        },
    )
    print(
        json.dumps(
            {
                "status": "published",
                "records": 13,
                "evidence_files": len(REFERENCES),
                "old_files_preserved": len(old_before),
                "full_final_fresh_acceptance": False,
            }
        )
    )


if __name__ == "__main__":
    main()
