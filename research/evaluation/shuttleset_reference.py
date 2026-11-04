"""Convert external ShuttleSet22 CSV rows into draft, source-bound references.

This research importer uses only the standard library. It does not fetch data,
decode media, run detectors, infer alignment or modify application sessions.
Caller-selected windows are evaluation populations, never detector inputs.

The CSV's published hitter/type truth is retained separately from the unverified
translation to canonical proxy frames. A/B scoring labels are not person IDs.
Only an explicit, name-checked evaluation actor map can expose benchmark IDs;
that map must never be used as a production identity/near-far binding.

CLI metadata contains the keyword arguments accepted by ``convert_reference``.
The CLI additionally verifies the actual source/proxy bytes against those hashes
and writes to a new output directory. Media dimensions/FPS/offset remain caller
declarations that need independent video/proxy review.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from urllib.parse import urlsplit

VERSION = "shuttleset22-reference-v1"
MAPPING_VERSION = "shuttleset22-native12-v1"
DATASET = "CoachAI-ShuttleSet22"
_REQUIRED_COLUMNS = {"rally", "ball_round", "frame_num", "player", "type"}
_SHOT_TYPES = {
    "放小球": "net_shot",
    "擋小球": "block",
    "殺球": "smash",
    "點扣": "smash",
    "挑球": "lift",
    "防守回挑": "lift",
    "長球": "clear",
    "平球": "drive",
    "小平球": "drive",
    "後場抽平球": "drive",
    "切球": "drop",
    "過渡切球": "drop",
    "過度切球": "drop",  # spelling present in the released SS22 CSVs
    "推球": "push",
    "撲球": "rush",
    "防守回抽": "drive",
    "勾球": "cross_net",
    "發短球": "short_serve",
    "發長球": "long_serve",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _hash(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    return parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username and not parsed.password


def _csv_integer(value: object, field: str, *, minimum: int) -> int:
    _require(isinstance(value, str) and re.fullmatch(r"[0-9]+", value) is not None, f"invalid {field} integer")
    result = int(value)
    _require(result >= minimum, f"invalid {field} integer")
    return result


def _provenance(provenance: dict) -> dict:
    _require(isinstance(provenance, dict), "published source provenance required")
    _require(provenance.get("dataset") == DATASET, "unsupported annotation dataset")
    revision = provenance.get("dataset_revision")
    _require(isinstance(revision, str) and re.fullmatch(r"[0-9a-f]{40}", revision) is not None,
             "immutable dataset revision required")
    _require(_text(provenance.get("match_id")), "source match ID required")
    _require(_integer(provenance.get("set_no")) and provenance["set_no"] > 0, "positive source set number required")
    for field in ("annotations_url", "source_video_url", "publication"):
        _require(_url(provenance.get(field)), f"published {field} HTTPS URL required")
    _require(provenance.get("annotation_origin") == "published_human_annotation",
             "published human annotation origin required")
    _require(isinstance(provenance.get("upstream_tuned"), bool), "explicit upstream tuning declaration required")
    names = provenance.get("source_competitors")
    _require(isinstance(names, dict) and set(names) == {"A", "B"}, "source A/B competitor names required")
    _require(all(_text(name) for name in names.values()) and names["A"] != names["B"],
             "distinct source competitor names required")
    evidence = provenance.get("license_evidence")
    _require(isinstance(evidence, dict), "publisher license evidence required")
    _require(_text(evidence.get("id")) and _text(evidence.get("scope")), "license identity and scope required")
    _require(_url(evidence.get("url")) and _hash(evidence.get("sha256")), "license URL and hash required")
    # Preserve the supplied evidence; validation is not a legal rights determination.
    json.dumps(provenance, allow_nan=False)
    return deepcopy(provenance)


def _actor_bindings(mapping: dict | None, scoring_labels: dict, provenance: dict) -> dict[str, str]:
    _require(isinstance(scoring_labels, dict) and set(scoring_labels) == {"A", "B"},
             "explicit A/B scoring labels required")
    _require(all(_text(value) for value in scoring_labels.values()) and scoring_labels["A"] != scoring_labels["B"],
             "distinct scoring labels required")
    if mapping is None:
        return {}
    _require(isinstance(mapping, dict) and set(mapping) == {"A", "B"}, "complete evaluation actor map required")
    actors = {}
    for source, entry in mapping.items():
        _require(isinstance(entry, dict), "invalid benchmark actor binding")
        for field in ("source_competitor", "configured_competitor", "scoring_label", "actor_id"):
            _require(_text(entry.get(field)), f"benchmark actor {field} required")
        expected_name = provenance["source_competitors"][source]
        _require(entry["source_competitor"] == expected_name == entry["configured_competitor"],
                 "benchmark competitor names do not match")
        _require(entry["scoring_label"] == scoring_labels[source], "benchmark scoring label does not match")
        actors[source] = entry["actor_id"]
    _require(len(set(actors.values())) == 2, "benchmark actors must be distinct")
    return actors


def _windows(selected_windows: list[dict], n_frames: int) -> list[dict]:
    _require(isinstance(selected_windows, list) and bool(selected_windows), "selected reference windows required")
    ids, rallies, result = set(), set(), []
    for window in selected_windows:
        _require(isinstance(window, dict), "invalid reference window")
        key = window.get("window_id")
        _require(isinstance(key, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", key) is not None,
                 "safe reference window ID required")
        rally = window.get("rally_id")
        _require(_integer(rally) and rally > 0, "positive selected rally ID required")
        _require(key not in ids and rally not in rallies, "duplicate window or rally ID")
        bounds = window.get("window_frames")
        _require(isinstance(bounds, list) and len(bounds) == 2 and all(_integer(v) for v in bounds),
                 "integer half-open window frames required")
        _require(0 <= bounds[0] < bounds[1] <= n_frames, "reference window outside canonical media frames")
        _require(window.get("exhaustive_published_contacts") is True,
                 "explicit published-contact population scope required")
        ids.add(key)
        rallies.add(rally)
        result.append(deepcopy(window))
    result.sort(key=lambda window: (window["window_frames"][0], window["window_id"]))
    _require(all(left["window_frames"][1] <= right["window_frames"][0] for left, right in zip(result, result[1:])),
             "overlapping selected reference windows")
    return result


def _read_rows(raw_csv: bytes, selected_rallies: set[int]) -> dict[int, list[tuple[dict, int, int, int]]]:
    reader = csv.DictReader(io.StringIO(raw_csv.decode("utf-8-sig"), newline=""), strict=True)
    fields = reader.fieldnames
    _require(fields is not None and len(fields) == len(set(fields)) and _REQUIRED_COLUMNS <= set(fields),
             "missing or duplicate required CSV columns")
    groups = defaultdict(list)
    seen_rounds, seen_frames = set(), set()
    for row_number, row in enumerate(reader, start=2):
        _require(None not in row and all(isinstance(value, str) for value in row.values()), "malformed CSV row")
        rally = _csv_integer(row["rally"], "rally", minimum=1)
        if rally not in selected_rallies:
            continue
        ball_round = _csv_integer(row["ball_round"], "ball_round", minimum=1)
        frame = _csv_integer(row["frame_num"], "frame_num", minimum=0)
        _require((rally, ball_round) not in seen_rounds, "duplicate selected ball_round")
        _require(frame not in seen_frames, "duplicate selected contact frame")
        seen_rounds.add((rally, ball_round))
        seen_frames.add(frame)
        groups[rally].append((row, frame, ball_round, row_number))
    _require(set(groups) == selected_rallies, "selected rally missing from CSV")
    for group in groups.values():
        group.sort(key=lambda item: item[1])
    return groups


def convert_reference(
    raw_csv: bytes,
    *,
    expected_csv_sha256: str,
    session_id: str,
    source_media_sha256: str,
    proxy_sha256: str,
    timebase: str,
    fps_num: int,
    fps_den: int,
    n_frames: int,
    width: int,
    height: int,
    label_to_proxy_frame_offset: int,
    match_format: str,
    selected_windows: list[dict],
    scoring_labels: dict[str, str],
    provenance: dict,
    split: str = "diagnostic",
    benchmark_actor_map: dict | None = None,
    held_out_reserved_before_tuning: bool = False,
) -> list[dict]:
    """Return draft manifests compatible with ``research.shot_benchmark``.

    ``canonical_frame = CSV.frame_num + label_to_proxy_frame_offset`` is an
    explicit caller-supplied integer translation. It is not fitted here and
    cannot represent retiming, VFR resampling or arbitrary frame duplication.
    The caller must verify that such a translation describes the actual proxy.
    Public conversion validates hash syntax; the CLI verifies actual media bytes.
    """
    _require(isinstance(raw_csv, bytes), "raw external CSV bytes required")
    _require(_hash(expected_csv_sha256), "valid expected annotation hash required")
    csv_hash = hashlib.sha256(raw_csv).hexdigest()
    _require(csv_hash == expected_csv_sha256, "annotation hash mismatch")
    _require(_hash(source_media_sha256), "valid source media hash required")
    _require(_hash(proxy_sha256), "valid canonical proxy hash required")
    _require(_text(session_id), "session ID required")
    _require(timebase == "canonical_media_seconds", "canonical media timebase required")
    _require(all(_integer(value) and value > 0 for value in (fps_num, fps_den)), "positive rational fps required")
    _require(all(_integer(value) and value > 0 for value in (n_frames, width, height)),
             "positive canonical media frames and resolution required")
    _require(_integer(label_to_proxy_frame_offset), "explicit integer frame offset required")
    _require(match_format == "singles", "ShuttleSet22 reference importer supports singles only")
    _require(split in ("diagnostic", "development", "held_out"), "explicit supported project split required")
    _require(isinstance(held_out_reserved_before_tuning, bool), "boolean reservation declaration required")
    _require(split != "held_out" or held_out_reserved_before_tuning, "held-out match must be reserved before tuning")
    source = _provenance(provenance)
    actors = _actor_bindings(benchmark_actor_map, scoring_labels, source)
    windows = _windows(selected_windows, n_frames)
    groups = _read_rows(raw_csv, {window["rally_id"] for window in windows})
    rate = Fraction(fps_num, fps_den)
    documents = []
    for window in windows:
        lo, hi = window["window_frames"]
        group = groups[window["rally_id"]]
        shots = []
        for row, source_frame, ball_round, row_number in group:
            frame = source_frame + label_to_proxy_frame_offset
            _require(lo <= frame < hi, "selected contact anchor outside its half-open reference window")
            raw_family = row["type"]
            family = _SHOT_TYPES.get(raw_family.strip(), "unknown")
            hitter = row["player"].strip() if row["player"].strip() in ("A", "B") else None
            identity = json.dumps(
                [DATASET, source["dataset_revision"], csv_hash, source["match_id"], source["set_no"],
                 window["rally_id"], ball_round, source_frame], separators=(",", ":"), ensure_ascii=False,
            )
            shots.append({
                "annotation_id": "ss22:" + hashlib.sha256(identity.encode("utf-8")).hexdigest(),
                "frame_idx": frame,
                "time_s": float(frame / rate),
                "source_frame": source_frame,
                "source_ball_round": ball_round,
                "source_csv_row": row_number,
                "source_hitter": hitter,
                "source_competitor": source["source_competitors"].get(hitter),
                "scoring_label": scoring_labels.get(hitter),
                "player_id": actors.get(hitter),
                "family": family,
                "raw_family": raw_family,
                "mapping_reason": ("documented_source_type_to_native12" if family != "unknown"
                                   else "unknown_or_unsupported_source_type_retained"),
                "source_row": dict(row),
            })
        known = sum(shot["family"] != "unknown" for shot in shots)
        hitter_count = sum(shot["source_hitter"] is not None for shot in shots)
        actor_count = sum(shot["player_id"] is not None for shot in shots)
        final_row = group[-1][0]
        winner = final_row.get("getpoint_player")
        winner = winner if winner in ("A", "B") else None
        reference_provenance = {
            **deepcopy(source),
            "annotations_sha256": csv_hash,
            "source_media_sha256": source_media_sha256,
            "proxy_sha256": proxy_sha256,
            "mapping_version": MAPPING_VERSION,
            "frame_mapping": {"kind": "caller_declared_integer_translation", "offset": label_to_proxy_frame_offset},
            "benchmark_actor_map": deepcopy(benchmark_actor_map),
            "actor_map_scope": "evaluation_reference_only; never a production person/near-far binding",
            "license_verification": "supplied publisher evidence retained; no additional rights inferred",
        }
        documents.append({
            "schema_version": 1,
            "converter_version": VERSION,
            "session_id": session_id,
            "media_sha256": source_media_sha256,
            "proxy_sha256": proxy_sha256,
            "timebase": timebase,
            "fps_num": fps_num,
            "fps_den": fps_den,
            "media_n_frames": n_frames,
            "width": width,
            "height": height,
            "match_format": match_format,
            "window_id": window["window_id"],
            "window_frames": [lo, hi],
            "window_s": [float(lo / rate), float(hi / rate)],
            "status": "draft",
            "split": split,
            "exhaustive": True,
            "review": {
                "human_verified": False,
                "our_human_reviewed": False,
                "origin": "published_human_annotation_with_draft_timeline_binding",
                "method": "Published source truth retained; no human alignment or all-physical-contact review asserted.",
            },
            "alignment": {"status": "unverified", "label_to_proxy_frame_offset": label_to_proxy_frame_offset,
                          "source_pts_mapping": "not inferred by this importer"},
            "reference_provenance": reference_provenance,
            "population": {
                "project_split": split,
                "held_out_reserved_before_tuning": held_out_reserved_before_tuning,
                "upstream_tuned": source["upstream_tuned"],
                "source_rally_id": window["rally_id"],
                "contact_scope": "published official rally contact anchors in explicitly selected windows",
                "exhaustive_published_contacts": True,
                "all_physical_contacts_independently_reviewed": False,
                "use": "evaluation only; these windows are not detector inputs",
            },
            "truth_coverage": {"contacts": len(shots), "known_shot": known, "unknown_shot": len(shots) - known,
                               "source_hitter": hitter_count, "benchmark_actor": actor_count},
            "metric_availability": {
                "published_contact_anchors": True,
                "known_shot_labels": bool(known),
                "annotated_competitor": bool(hitter_count),
                "benchmark_hitter_ids": bool(actor_count),
                "physical_contact_timing_accuracy": False,
                "rally_down_boundaries": False,
                "dense_shuttle": False,
                "score_sequence": False,
                "durable_player_identity": False,
            },
            "published_rally_outcome": {
                "roundscore_A_raw": final_row.get("roundscore_A"),
                "roundscore_B_raw": final_row.get("roundscore_B"),
                "source_point_winner": winner,
                "winner_scoring_label": scoring_labels.get(winner),
                "winner_benchmark_actor": actors.get(winner),
                "win_reason_raw": final_row.get("win_reason"),
                "lose_reason_raw": final_row.get("lose_reason"),
                "status": "published annotation; not an accepted application point or observed OCR reading",
            },
            "shots": shots,
        })
    return documents


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        _require(key not in result, f"duplicate metadata key: {key}")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON metadata: {value}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--source-media", required=True, type=Path)
    parser.add_argument("--proxy", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        _require(not args.output_dir.exists() and not args.output_dir.is_symlink(), "output directory already exists")
        metadata_raw = args.metadata.read_bytes()
        metadata = json.loads(metadata_raw.decode("utf-8-sig"), object_pairs_hook=_unique_object,
                              parse_constant=_invalid_constant)
        _require(isinstance(metadata, dict), "metadata must be an object")
        source_hash, proxy_hash = _file_digest(args.source_media), _file_digest(args.proxy)
        _require(source_hash == metadata.get("source_media_sha256"), "source media hash mismatch")
        _require(proxy_hash == metadata.get("proxy_sha256"), "canonical proxy hash mismatch")
        documents = convert_reference(args.csv.read_bytes(), **metadata)
        for document in documents:
            document["reference_provenance"]["binding_metadata_sha256"] = hashlib.sha256(metadata_raw).hexdigest()
            document["reference_provenance"]["media_hash_verification"] = "CLI read actual source and proxy bytes"
        serialized = [(document["window_id"], json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
                      for document in documents]
        _require(_file_digest(args.source_media) == source_hash and _file_digest(args.proxy) == proxy_hash,
                 "media changed during conversion")
        args.output_dir.mkdir(parents=True, exist_ok=False)
        for key, body in serialized:
            with (args.output_dir / f"{key}.json").open("x", encoding="utf-8") as stream:
                stream.write(body)
    except (OSError, ValueError, TypeError, UnicodeError, csv.Error) as error:
        parser.error(str(error))
    print(json.dumps({"version": VERSION, "status": "draft", "windows": len(documents),
                      "contacts": sum(len(document["shots"]) for document in documents),
                      "output_dir": str(args.output_dir.resolve()), "accuracy_evaluated": False}))


if __name__ == "__main__":
    main()
