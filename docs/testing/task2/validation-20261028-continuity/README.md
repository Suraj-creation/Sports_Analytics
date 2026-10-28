# Task 2: continuity and classification context validation

**Task 2 remains incomplete.** The changes fix attribution and classification-input defects. They do not establish reliable identity through full crossings or high shot-family accuracy. The neural association experiment regressed and remains opt-in; `gpu-rtx4000` and `cpu-dev` do not enable it.

## Implementation and execution

Code revision: `3a17473` (`Preserve player association uncertainty and anonymous shot context`). Baseline: `b97c069`. Code was authored in an isolated Windows Git worktree, pushed, fetched into a clean GPU-server checkout, and tested there. The user's later clarification requires all further tests and media/model processing on the GPU server. Earlier local CPU/frontend checks are superseded by server verification.

The changes add bounded, private OSNet appearance/motion association, raw/canonical identity provenance and cache codec 9. Only current uniquely matched detections teach neural descriptors; descriptors are not persisted. Ambiguous identities remain unresolved. Optional neural association recomputes sequentially, bypassing cached reads and seek-ahead previews, because mixed cached/fresh chunks could otherwise reuse a canonical ID for another person.

Additional fixes preserve unmatched-person metadata through camera stabilization, withhold team hypotheses when extra unidentified people are visible, and prevent doubles from filling singles scoring slots. Anonymous singles shot geometry can survive a camera cut only with exactly two current supported court observations, verified geometry and matching birth/track provenance. All visible observations are counted before participant admission, so a newly appearing third/fourth player cannot slip through that guard. This context never restores names, credited actors or roster totals.

## Four-player development experiment

Both runs use the same 250-frame, 25-fps doubles excerpt, source/proxy hashes and calibration. The baseline was rerun from `b97c069`. The neural run used the existing detector/pose cadence with the pinned OSNet checkpoint and `neural-motion-v3` policy. Its source-file manifest is preserved separately because this experiment preceded the later singles-only context fix.

The comparison uses 64 boxes in 16 **AI-draft** source frames. These figures measure sampled draft agreement, not independently human-reviewed identity accuracy or continuity between frames.

| Measurement | Baseline | Neural experiment |
|---|---:|---:|
| Box agreement precision / recall | 0.983 / 0.922 | 0.983 / 0.922 |
| Sampled identity F1 agreement | 0.919 | 0.694 |
| Sampled switches | 0 | 5 |
| Frames with four distinct compatible identities | 14/16 | 11/16 |
| Analysis wall time | 21.677 s | 28.463 s |
| Sampled peak process GPU memory | 2122 MiB | 2140 MiB |

Timing is descriptive: individual runs included model startup and shared host activity. The neural experiment is not promoted to the default profile.

## Published per-hit reference

FineBadminton's publication describes machine-assisted annotations refined by human annotators. We imported the published records without retiming or generating new labels. This is provider review, not our own human review. Exact physical-contact timing uncertainty is not established; the temporal metric is **agreement with published `hitting.start_frame` anchors at ±0.20 s**, or five frames at 25 fps. Court-side agreement is not durable player identity or four-player hitter accuracy.

Dataset revision: `72cae601e08c83ee8ec7e19f8fd7850e9158af7d`. See the [converter/evaluator protocol](../../../../research/README-finebadminton-reference.md) for hashes, source links, taxonomy mapping and commands. Both source videos were processed on the GPU server; media and weights are not committed here.

Recording **0044** (Sen–Teh, 41 anchors in four rallies) exposed the singles context defect and is development data. Its final comparison replays the same cached GPU observations with the corrected semantic engine; it is not a second fresh model inference. Known-family macro F1 rose from 0 to 0.05934, with 1/3 resolved matched court sides correct. This remains poor performance.

Recording **0046** (Sen–Ogawa, 72 anchors in seven rallies) was reserved at `2026-10-28T17:13:21.0189127Z`, before predictions were inspected and before the context fix. It is a different match, with one athlete shared. Baseline and `3a17473` both ran fresh GPU inference over all 7,616 frames using identical copied source/proxy/calibration. Pretrained-model training overlap is unknown; this is a project-level holdout, not proof of model-level independence.

| Held-out 0046 measurement | Baseline | `3a17473` |
|---|---:|---:|
| Published anchors / machine stroke candidates | 72 / 50 | 72 / 50 |
| Matched anchors | 20 | 20 |
| Anchor precision / recall / F1 | 0.400 / 0.278 / 0.328 | 0.400 / 0.278 / 0.328 |
| Known-family macro F1 | 0 | 0 |
| Unknown-family fraction of candidates | 88% | 64% |
| Resolved matched court sides / correct | 0 / 0 | 7 / 7 |
| Joint anchor + family + court-side F1 | 0 | 0 |

The seven correct sides cover only 7/20 matched anchors and 7/72 reference hits. Thirteen matched anchors still have unresolved sides; 52 anchors are missed. Reduced unknown-family output did **not** improve measured family F1. The installed classifier remains `stroke_rules_v0`; configuring a BST model name does not supply a trained temporal classifier.

## Verification and preservation

- Clean pushed GPU checkout: **941 Python tests passed**, no skips. See `gpu-python-tests.log`.
- GPU-server frontend checks: **68 tests passed** in 23 files. No frontend source changed; the app serves the existing built frontend.
- Independent review found and fixed camera-provenance loss, mixed-cache identity collision, unresolved-extra team credit and participant-admission delay. The final focused GPU regression run passed 40 tests; Ruff checks and formatting passed.
- Browser checks used `http://127.0.0.1:18010`, an SSH forward to GPU `127.0.0.1:8010`. Four roster entries, separate reviewed/automatic totals, unresolved counts, video playback and bounded evidence navigation were inspected. Cloudflare was not started.
- Seven original event ledgers were backed up with SQLite's backup API; logical row hashes remain identical. Analysis and replays use isolated data directories. Original Windows user files and server working changes were preserved.

Full JSON reports retain per-class confusion, misses/spurious predictions, abstentions, source/event hashes and limitations. The remaining work is validated four-person continuity, independent doubles identity/hitter labels and a trained, evaluated shot classifier. These results do not support a high-accuracy or completed-Task-2 claim.

The baseline-ingestion and development-replay harnesses are archived as `.py.txt`
to preserve the exact executed source. They use fixed isolated server paths and
refuse an existing output directory. The fresh comparison harness is
`docs/testing/task2/continuation/fresh_session_benchmark.py`; always source the
server GPU environment and use its existing virtual environment before running it.
