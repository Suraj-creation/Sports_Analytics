"""Import published FineBadminton hit references without asserting our human review.

The provider describes human refinement of machine-assisted annotations in
He et al., FineBadminton (ACM MM 2025), sections 3.1 and 3.2. Imports remain
``draft`` and diagnostic by default. Explicit acceptance of provider review can
mark them reviewed, while recording that we did not review them ourselves.
Each output covers one annotated rally; unlabelled video spans are never
declared exhaustive.

No network or inference is performed. Use an ignored or temporary output
directory; real source videos and annotation files do not belong in Git.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from fractions import Fraction
from pathlib import Path

DATASET_REVISION = "72cae601e08c83ee8ec7e19f8fd7850e9158af7d"
PUBLICATION = "https://arxiv.org/html/2508.07554v1"
DATASET = "iLearn-Lab/Finebadminton-20K"
MAPPING_VERSION = "finebadminton-reference-map-v1"
VERSION = "finebadminton-reference-v1"

_DIRECT = {
    "clear": "clear",
    "drive": "drive",
    "drop": "drop",
    "drop shot": "drop",
    "net lift": "lift",
    "lift": "lift",
    "lob": "lift",
    "net shot": "net_shot",
    "block": "block",
    "push": "push",
    "push shot": "push",
    "rush": "rush",
    "smash": "smash",
    "short serve": "short_serve",
    "long serve": "long_serve",
    "high serve": "long_serve",
    "flick serve": "long_serve",
    "net kill": "rush",
    "unknown": "unknown",
}
_SHORT_SERVES = {"short serve", "short service"}
_LONG_SERVES = {"long serve", "long service", "high serve", "flick serve"}
_SMASHES = {
    "common smash",
    "full smash",
    "stick smash",
    "jump smash",
    "slice smash",
    "half smash",
    "wrist smash",
    "smash",
}


def _hash(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _map_family(raw: str, subtypes: list[str]) -> tuple[str, str | None, str]:
    family = raw.strip().lower()
    detail = {value.strip().lower() for value in subtypes}
    if family == "cross-court net shot":
        return "net_shot", "cross_court", "source cross-court placement separated from net-shot family"
    if family == "serve":
        short, long = bool(detail & _SHORT_SERVES), bool(detail & _LONG_SERVES)
        if short != long:
            return ("short_serve" if short else "long_serve"), None, "explicit source serve subtype"
        return "unknown", None, "serve subtype missing, unsupported or contradictory"
    if family == "kill":
        # FineBadminton uses kill for rear-court jump/full/stick smashes too.
        # The word alone cannot establish the ontology's near-net rush class.
        smash, net = bool(detail & _SMASHES), bool(detail & {"net kill", "net rush"})
        if smash != net:
            return ("smash" if smash else "rush"), None, "explicit source smash or net-kill subtype"
        return "unknown", None, "kill subtype missing, unsupported or contradictory"
    if family in _DIRECT:
        return _DIRECT[family], None, "explicit source primary-type mapping; source subtypes retained"
    return "unknown", None, "unsupported source primary type retained without inference"


def convert_reference(
    raw: bytes,
    *,
    session_id: str,
    video_name: str,
    media_sha256: str,
    expected_media_sha256: str,
    expected_source_sha256: str,
    fps_num: int,
    fps_den: int,
    n_frames: int,
    width: int,
    height: int,
    source_revision: str = DATASET_REVISION,
    split: str = "diagnostic",
    held_out_reserved_before_tuning: bool = False,
    accept_published_review: bool = False,
) -> list[dict]:
    """Return source-bound shot-benchmark manifests, one per published rally.

    ``media_sha256`` must be computed from the actual evaluated MP4, while
    ``expected_media_sha256`` is its independently obtained release/LFS digest.
    Media metadata must come from that file, never from guessed annotation FPS.
    The CLI computes the actual media digest and accepts probed metadata.
    ``provider_human_verified`` records the publication's account. Explicitly
    accepting that account sets ``human_verified`` with provider scope; the
    separate ``our_human_reviewed`` field always remains false.
    """
    if not isinstance(raw, bytes) or not _hash(expected_source_sha256):
        raise ValueError("valid source bytes and annotation hash required")
    source_hash = hashlib.sha256(raw).hexdigest()
    if source_hash != expected_source_sha256:
        raise ValueError("annotation hash mismatch")
    if not _hash(media_sha256) or not _hash(expected_media_sha256) or media_sha256 != expected_media_sha256:
        raise ValueError("media hash mismatch or invalid hash")
    if not isinstance(source_revision, str) or not re.fullmatch(r"[0-9a-f]{40}", source_revision):
        raise ValueError("pinned source revision required")
    if not isinstance(session_id, str) or not session_id or not session_id.isalnum():
        raise ValueError("valid session id required")
    if not isinstance(video_name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+\.mp4", video_name):
        raise ValueError("source video basename required")
    if any(not _integer(value) or value <= 0 for value in (fps_num, fps_den)):
        raise ValueError("positive integer fps numerator and denominator required")
    if any(not _integer(value) or value <= 0 for value in (n_frames, width, height)):
        raise ValueError("positive integer media frame count and resolution required")
    if split not in ("diagnostic", "development", "held_out"):
        raise ValueError("explicit valid split required")
    if split == "held_out" and held_out_reserved_before_tuning is not True:
        raise ValueError("held-out recording must have been reserved before tuning")
    if not isinstance(accept_published_review, bool):
        raise ValueError("provider review acceptance must be an explicit boolean")
    rows = json.loads(raw)
    if not isinstance(rows, list) or not rows:
        raise ValueError("source JSON must be a nonempty list of rallies")
    revision_url = f"https://huggingface.co/datasets/{DATASET}/resolve/{source_revision}"
    provenance = {
        "converter_version": VERSION,
        "mapping_version": MAPPING_VERSION,
        "dataset": DATASET,
        "dataset_revision": source_revision,
        "annotations_sha256": source_hash,
        "annotations_url": f"{revision_url}/finebadminton-20K/{Path(video_name).stem}_updated.json",
        "media_url": f"{revision_url}/videos/{video_name}",
        "source_media_sha256": expected_media_sha256,
        "publication": PUBLICATION,
        "publication_sections": ["3.1", "3.2"],
        "license": "Apache-2.0",
        "annotation_process": (
            "Provider: manual annotation or machine proposals refined and verified by human annotators."
        ),
        "coverage": "published annotated rally windows only",
        "anchor_semantics": (
            "published hitting.start_frame, without retiming or deriving contacts from model predictions"
        ),
    }
    manifests = []
    previous_end = -1
    for rally_index, rally in enumerate(rows):
        if not isinstance(rally, dict) or rally.get("video") != video_name:
            raise ValueError("source video binding mismatch")
        fps = rally.get("fps")
        if (
            not isinstance(fps, (int, float))
            or isinstance(fps, bool)
            or not math.isfinite(fps)
            or Fraction(str(fps)) != Fraction(fps_num, fps_den)
        ):
            raise ValueError("source fps differs from probed media fps")
        if rally.get("resolution") != {"width": width, "height": height}:
            raise ValueError("source resolution differs from probed media resolution")
        start, end = rally.get("start_frame"), rally.get("end_frame")
        if not _integer(start) or not _integer(end) or not 0 <= start < end <= n_frames or start < previous_end:
            raise ValueError("invalid, overlapping or out-of-order rally frame window")
        if not _integer(rally.get("duration_frames")) or rally["duration_frames"] != end - start:
            raise ValueError("rally duration does not match frame window")
        previous_end = end
        roster = rally.get("playerList")
        if not isinstance(roster, list) or len(roster) != 2:
            raise ValueError("exactly two named source players required")
        names = [player.get("name") if isinstance(player, dict) else None for player in roster]
        if any(not isinstance(name, str) or not name.strip() for name in names) or len(set(names)) != 2:
            raise ValueError("source player names must be nonempty and unique")
        hits = rally.get("hitting")
        if not isinstance(hits, list) or not hits:
            raise ValueError("published rally must contain hitting records")
        shots, sides, side_players = [], {}, {}
        expected_start = start
        for hit_index, hit in enumerate(hits):
            if not isinstance(hit, dict):
                raise ValueError("invalid hitting record")
            anchor, hit_end = hit.get("start_frame"), hit.get("end_frame")
            if (
                not _integer(anchor)
                or not _integer(hit_end)
                or not start <= anchor < hit_end <= end
                or anchor != expected_start
            ):
                raise ValueError("hit anchors must be ordered, contiguous and inside the half-open rally window")
            expected_start = hit_end
            player = hit.get("player")
            if not isinstance(player, str) or player not in names:
                raise ValueError("hit player must name an actual source player; no identity inference is allowed")
            foundation = hit.get("Foundational Actions Level")
            if not isinstance(foundation, dict):
                raise ValueError("source Foundational Actions Level required")
            raw_family, subtypes, side = foundation.get("hit type"), foundation.get("subtype"), foundation.get("hitter")
            if (
                not isinstance(raw_family, str)
                or not raw_family.strip()
                or not isinstance(subtypes, list)
                or any(not isinstance(value, str) or not value.strip() for value in subtypes)
            ):
                raise ValueError("source hit type and subtype list required")
            if side not in (None, "top", "bottom"):
                raise ValueError("invalid source hitter side")
            if side is not None:
                if sides.get(player, side) != side or side_players.get(side, player) != player:
                    raise ValueError("contradictory player-side labels within source rally")
                sides[player], side_players[side] = side, player
            family, placement, reason = _map_family(raw_family, subtypes)
            shots.append(
                {
                    "annotation_id": (
                        f"finebadminton:{source_revision}:{video_name}:rally-{rally_index}:hit-{hit_index}"
                    ),
                    "time_s": float(Fraction(anchor * fps_den, fps_num)),
                    "family": family,
                    "player_id": player,
                    "frame_idx": anchor,
                    "source_start_frame": anchor,
                    "source_end_frame": hit_end,
                    "source_player": player,
                    "source_hitter": side,
                    "raw_family": raw_family,
                    "raw_subtypes": list(subtypes),
                    "source_ball_area": foundation.get("ball area"),
                    "placement": placement,
                    "mapping_version": MAPPING_VERSION,
                    "mapping_reason": reason,
                }
            )
        if expected_start != end:
            raise ValueError("source hits must cover the complete published rally frame window")
        manifests.append(
            {
                "schema_version": 1,
                "session_id": session_id,
                "media_sha256": media_sha256,
                "timebase": "canonical_media_seconds",
                "window_s": [float(Fraction(start * fps_den, fps_num)), float(Fraction(end * fps_den, fps_num))],
                "window_frames": [start, end],
                "fps_num": fps_num,
                "fps_den": fps_den,
                "media_n_frames": n_frames,
                "width": width,
                "height": height,
                "status": "reviewed" if accept_published_review else "draft",
                "split": split,
                "exhaustive": True,
                "review": {
                    "human_verified": accept_published_review,
                    "provider_human_verified": True,
                    "our_human_reviewed": False,
                    "accepted_published_review": accept_published_review,
                    "origin": "published_human_refined_reference",
                    "publication": PUBLICATION,
                    "method": "Deterministic import of provider labels; no new human review or AI relabelling.",
                    "held_out_reserved_before_tuning": held_out_reserved_before_tuning,
                },
                "rally_index": rally_index,
                "source_player_list": roster,
                "shots": shots,
                "reference_provenance": dict(provenance),
                "limitations": [
                    "Provider labels include machine assistance followed by reported human refinement.",
                    "Import does not independently verify annotation correctness or pixel/frame correspondence.",
                    "Only published rally windows are covered; other video spans are unlabelled.",
                    "Cross-court net predictions require the same family/placement normalization before comparison.",
                ],
            }
        )
    return manifests


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-json", type=Path, required=True)
    parser.add_argument("--media", type=Path, required=True, help="Actual evaluated source MP4, read only to hash it")
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--expected-media-sha256", required=True, help="Independently obtained release/LFS SHA-256")
    parser.add_argument("--video-name", required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--source-revision", default=DATASET_REVISION)
    for option in ("fps-num", "fps-den", "n-frames", "width", "height"):
        parser.add_argument(f"--{option}", type=int, required=True, help="Metadata probed from the evaluated MP4")
    parser.add_argument("--split", choices=("diagnostic", "development", "held_out"), default="diagnostic")
    parser.add_argument("--held-out-reserved-before-tuning", action="store_true")
    parser.add_argument(
        "--accept-published-review",
        action="store_true",
        help="Accept provider-reported human refinement; does not assert our own human review",
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True, help="Ignored or temporary directory; never overwrites"
    )
    args = parser.parse_args()
    try:
        digest = hashlib.sha256()
        with args.media.open("rb") as media:
            for block in iter(lambda: media.read(1024 * 1024), b""):
                digest.update(block)
        manifests = convert_reference(
            args.source_json.read_bytes(),
            session_id=args.session,
            video_name=args.video_name,
            media_sha256=digest.hexdigest(),
            expected_media_sha256=args.expected_media_sha256,
            expected_source_sha256=args.expected_source_sha256,
            fps_num=args.fps_num,
            fps_den=args.fps_den,
            n_frames=args.n_frames,
            width=args.width,
            height=args.height,
            source_revision=args.source_revision,
            split=args.split,
            held_out_reserved_before_tuning=args.held_out_reserved_before_tuning,
            accept_published_review=args.accept_published_review,
        )
        paths = [args.output_dir / f"{Path(args.video_name).stem}-rally-{i:04d}.json" for i in range(len(manifests))]
        if any(path.exists() for path in paths):
            raise ValueError("output file already exists")
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for path, manifest in zip(paths, manifests, strict=True):
            with path.open("x", encoding="utf-8") as output:
                output.write(json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
        print(
            json.dumps(
                {
                    "files": [str(path.resolve()) for path in paths],
                    "source_annotations_sha256": manifests[0]["reference_provenance"]["annotations_sha256"],
                    "source_revision": args.source_revision,
                    "publication": PUBLICATION,
                },
                indent=2,
            )
        )
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
