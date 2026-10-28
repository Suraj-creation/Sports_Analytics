# Evaluating automatic player candidates

`research/participant_benchmark.py` measures shot detection and shot-family predictions against an exhaustive shot-label window, and separately measures the correctness of the system's *automatic tracking-episode hypothesis* after an external episode-to-person mapping is applied. The person metric is conditional on that mapping: it does **not** measure automatic re-identification, full-match coverage, doubles rules, or a person's total match performance.

Use `research/shot-annotation-protocol.md` for the source-bound, exhaustive per-contact annotation, including no-contact spans. Before viewing the model's contact or shot outputs, separately inspect each player track episode in the same window, its stored track boxes and source video. Assign stable person IDs only for periods whose visual identity is supported. If the detector is wrong or the person cannot be identified, leave that interval unbound. Split when tracking resets, exits, IDs are reused or identity may have switched. Track-to-person review must be independent from shot/contact annotations and complete for the window, with unresolved episodes documented. `human_verified` and `exhaustive_for_window` are reviewer attestations, not independent proof. Confirm that the reserved held-out recording was not used for tuning.

The separate mapping file has the same session, media hash, canonical timebase and half-open window as the shot file. Intervals are half-open seconds; overlapping assignments to the same track, episode or person are rejected. An empty list is valid if no identity can be established, but produces no resolved-player accuracy. The example below is a schema illustration, not reviewed data:

```json
{
  "schema_version": 1,
  "session_id": "SESSION_ID",
  "event_log_sha256": "64_LOWERCASE_HEX_CHARACTERS_FOR_THE_EVALUATED_EVENT_LOG",
  "media_sha256": "64_LOWERCASE_HEX_CHARACTERS",
  "timebase": "canonical_media_seconds",
  "window_s": [0.0, 10.0],
  "status": "draft",
  "review": {"human_verified": false, "independent_of_shot_labels": true, "exhaustive_for_window": false},
  "bindings": [
    {"participant_id": "participant-epoch123-000001", "track_id": 4, "player_id": "alice", "start_s": 0.0, "end_s": 5.0}
  ]
}
```

Set `status` to `reviewed` only after exhaustive independent human review; then set both review booleans to true. Draft labels or mappings require `--allow-draft` and are explicitly ineligible for an accuracy claim. The event-log hash must match the exact evaluation snapshot because tracker episode IDs may be reused after reanalysis. Compute the hash using the same newline-joined event bodies described by `predictions_from_session`. The episode ID and track ID must come from the actual input session's tracker evidence, not labels guessed from position, side, or the ground-truth hitter. Keep separately versioned label and binding files and their source evidence.

Run on a read-only snapshot rather than a live, changing database:

```sh
source ../gpu-env.sh
.venv/bin/python -m research.participant_benchmark \
  --session SESSION_ID --annotations shots.json --bindings episode-bindings.json \
  --data-dir /path/to/snapshot --tolerance-s 0.2
```

The evaluator rejects changed logs, human-corrected or retracted shot/contact
records and unsupported source bindings, then pairs contacts chronologically
one-to-one. `accuracy_all_labelled_truth` includes missed/unresolved contacts;
`accuracy_resolved_matched` excludes them and must accompany coverage and
detection counts. Version 2 adds `end_to_end.per_person` precision/recall and
joint contact/family/hitter scores, so spurious assigned events lower precision.
`shot_classification.known_family` excludes unknown ground-truth families;
the legacy macro-F1 still includes unknown as a class. Read metric-specific
eligibility and support. Hashes identify annotation files and the event log.
Results remain conditional on the external map and tested windows.

Use the separate [sampled tracking protocol](tracking-annotation-protocol.md)
to test automatic identity continuity with one global mapping, explicit missed
frames and hashed track evidence. Episode-to-person rebinding can conceal
fragmentation and swaps; it cannot substitute for that tracking test.
