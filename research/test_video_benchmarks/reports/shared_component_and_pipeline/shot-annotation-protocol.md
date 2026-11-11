# Shot benchmark annotation protocol

This protocol creates evidence for Task 2; it does not provide labels. A reviewer must inspect source video at the original frame rate, including several frames before and after each hit, with slow playback and frame stepping where available. Hide model predictions during initial annotation. Never infer a family or hitter just to complete a field.

## Selection and review

Choose separate recordings/sessions for development and held-out evaluation. Reserve held-out recordings before tuning, including all clips from the same recording in the same split; document camera angle, resolution, frame rate, lighting, occlusions, type of play (singles/doubles/practice), and limitations. Include representative and difficult examples, not only obvious shots. The tool evaluates one session/window at a time: maintain a separate split manifest and verify that recording identities do not cross splits. It does not establish split independence, inter-reviewer agreement, class representativeness, or the truth of a reviewer attestation.

Define a half-open window `[start, end)` in canonical media seconds, and exhaustively annotate **every physical hit**, including practice and ambiguous hits. If contact is unobservable, mark the best supported time and describe uncertainty; where even occurrence is uncertain, exclude that window from reviewed evaluation until adjudicated. Record the timing tolerance before evaluating and ensure it is justified by frame rate, blur and uncertainty. Use one annotation per physical hit. A separate rally/official-play evaluation is required for official event counts; this evaluator includes all live stroke events in the window, regardless of phase.

Use stable participant IDs only where identity is supported throughout the clip; use `null` when the hitter is unclear. Record track and team identifiers and evidence separately in annotation notes if available. Preserve frames, evidence, assumptions and corrections so another person can audit them. A second reviewer should adjudicate disputed families, hitter identities, contact boundaries and recording/split assignments before marking the file reviewed. `human_verified: true` is an assertion made by the annotator, not proof of review.

## Taxonomy

Use the project ontology (`sports/badminton/src/bai_badminton/ontology.yaml`) as the initial shared vocabulary. Label by observable intended flight and context: `clear` is a high deep shot from the rear; `drop` descends toward the opponent's front from an overhead/rear stroke; `smash` is a forceful steep attacking shot; `drive` is relatively flat and fast; `lift` rises from the front to the rear; `net_shot` is a controlled shot near the net; `block`, `push`, `rush`, `short_serve`, and `long_serve` use their ontology meanings. Use `unknown` when the evidence does not distinguish the family. Candidate subtypes such as jump, forehand/backhand, cross-court, and outcome are independent properties and must not be inferred from the shot family. The existing `cross_net` model label mixes family and placement: explicitly document any mapping, apply it consistently to labels and predictions before comparison, and do not compare incompatible vocabularies. Do not call a smash a winner without rally outcome evidence.

## Manifest

A separate JSON file describes each exhaustive window. Its `media_sha256` must match the session catalogue source hash; `session_id` identifies that same session. `status` is `draft` until human review is complete. No actual labels are included below:

```json
{
  "schema_version": 1,
  "session_id": "SESSION_ID",
  "media_sha256": "64_LOWERCASE_HEX_CHARACTERS",
  "timebase": "canonical_media_seconds",
  "window_s": [0.0, 10.0],
  "status": "draft",
  "split": "diagnostic",
  "exhaustive": true,
  "review": {"human_verified": false, "method": "describe review and limitations"},
  "shots": []
}
```

Each reviewed shot has at minimum `time_s` (contact in canonical seconds), `family` (ontology key or `unknown`), and `player_id` (stable participant ID or null). Notes may record footage conditions, uncertain contact range, clip/frame references, reviewer, class alternatives and separate variation/placement/outcome fields. Assign `reviewed` and `human_verified: true` only after review, and `held_out` only for a recording reserved from tuning. Store the annotation file securely; it may reference private video.

## Run and interpret

From the repository root on the server:

```sh
source ../gpu-env.sh
.venv/bin/python research/shot_benchmark.py --session SESSION_ID --annotations PATH_TO_JSON --tolerance-s 0.2
```

The tool reads the existing catalogue and session event store without modifying them. It compares the reviewed manifest with the current event view and emits hashes of both annotation file and event log. Draft files require `--allow-draft` and are explicitly ineligible for accuracy claims. `accuracy_claim_eligible` signals only reviewed held-out status and human-attestation; it does not verify recording separation or annotation quality. Save the JSON report outside historical session stores before making changes, then use the same labels, tolerance, session and windows to compare; retain version, code revision, analysis configuration and resource measurements separately.

Matches maximize the number of chronological one-to-one pairs within tolerance,
then minimize total absolute timestamp error. Missed truth events and spurious
predictions appear in the confusion matrix and lower per-class F1. Version 2
validates family keys against the project ontology and reports its taxonomy
version. The legacy `per_class`, `confusion` and `macro_f1` fields retain
`unknown` as a class for comparison with previous reports. **An unknown-to-unknown
match is not evidence of correct known-family classification.** Use
`known_family`: it excludes unknown truth and predictions matched to that
unobservable truth, while missed known truth, wrong known families and spurious
known predictions lower its scores. Its macro-F1 is null without known truth.
Report `metric_eligibility` and support separately for each property.

Attribution accuracy remains conditional on matched shots with labelled hitters.
`accuracy_all_labelled` counts unresolved predictions as incorrect;
`accuracy_resolved` excludes them and must accompany unresolved/missed counts.
For event accounting, use `end_to_end.per_person` precision/recall/F1 and
`joint_contact_family_hitter`. The joint metric requires time, family and person
to agree; missed, wrong, unresolved and spurious events are errors. Predictions
matched to unobservable family/person truth are excluded only for that property,
with joint exclusion counts shown. Timestamp error is conditional on a match.
Small/nonrepresentative samples cannot establish general accuracy. Manual
corrections affect the current event view: distinguish machine-only from
corrected evaluations.
